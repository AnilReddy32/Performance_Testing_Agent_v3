from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from Performance_Testing_Agent.execution_context import (
    create_execution_job_context,
)
from Performance_Testing_Agent.orchestrator.agent import root_agent

from uuid import uuid4

APP_NAME = "jira_agent_integration"
USER_ID = "jira_user"

async def run_orchestrator(
    prompt: str,
    initial_state: dict | None = None,
):
    session_service = InMemorySessionService()
    session_id = f"jira_session_{uuid4().hex}"
    initial_state = initial_state or create_execution_job_context()

    await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session_id,
        state=initial_state,
    )

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    content = types.Content(
        role="user",
        parts=[
            types.Part(text=prompt)
        ],
    )

    final_response = None

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session_id,
        new_message=content,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response = "".join(
                    part.text for part in event.content.parts if part.text
                )


    return final_response
        