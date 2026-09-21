import uuid

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from .agent import root_agent
from .logger import logger

ADK_APP_NAME = "performance_testing_agent"


class Orchestrator:
    """
    Thin wrapper around the ADK Runner.

    Responsibilities:
    1. Receive a user query.
    2. Run it through the ADK orchestrator agent (root_agent), which decides
       itself which specialist agents to call and in what order.
    3. Collect which agents were called and the orchestrator's final
       natural-language answer.
    4. Pull the authoritative structured results back out of shared session
       state (each specialist agent's tool writes its exact result there -
       see agents/*.py) rather than relying on any agent's natural-language
       reply, since that text is only a human-readable summary and isn't
       guaranteed to preserve every number exactly.
    5. Return the final response to the caller (e.g. the FastAPI /chat
       endpoint).
    """

    def __init__(self):
        self.session_service = InMemorySessionService()
        self.runner = Runner(
            agent=root_agent,
            app_name=ADK_APP_NAME,
            session_service=self.session_service,
        )

    async def execute(self, user_query: str) -> dict:
        user_id = "api_user"
        session_id = str(uuid.uuid4())

        await self.session_service.create_session(
            app_name=ADK_APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )

        logger.info("Running orchestrator agent....")

        content = genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=user_query)],
        )

        final_text = None
        agents_called: list[str] = []

        async for event in self.runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        ):
            for fc in event.get_function_calls():
                agents_called.append(fc.name)

            if event.is_final_response() and event.content and event.content.parts:
                text_parts = [p.text for p in event.content.parts if p.text]
                if text_parts:
                    final_text = "\n".join(text_parts)

        # Pull the authoritative structured results back out of shared
        # session state - this is where each specialist agent's tool
        # (agents/*.py) actually wrote its exact numbers.
        session = await self.session_service.get_session(
            app_name=ADK_APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        state = dict(session.state) if session else {}

        logger.info(f"Agents called: {agents_called}")
        logger.info("Orchestrator run complete")

        report = state.get("report_result")

        if report:
            report = dict(report)
            report["final_response"] = final_text
            return report

        return {
            "message": final_text or "Execution completed",
            "agents_called": agents_called,
            "state": state,
        }
