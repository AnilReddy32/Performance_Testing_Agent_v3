import os
import uuid
from pathlib import Path

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from Performance_Testing_Agent.execution_context import (
    artifact_directory_reference,
    create_execution_job_context,
    create_context_for_test_case,
    extract_catalog_test_case_id,
    is_k6_test_request,
    is_simulated_tool_request,
    resolve_artifact_directory,
)
from Performance_Testing_Agent.test_case_catalog.catalog import get_test_case
from Performance_Testing_Agent.artifact_store import (
    artifact_retention_days,
    write_artifact_manifest,
)

from .agent import (
    analysis_agent,
    monitoring_agent,
    report_agent,
    root_agent,
    security_agent,
)
from .logger import logger
from .pipeline import complete_real_k6_pipeline, json_object

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

    async def _get_state(self, user_id: str, session_id: str) -> dict:
        session = await self.session_service.get_session(
            app_name=ADK_APP_NAME,
            user_id=user_id,
            session_id=session_id,
        )
        return dict(session.state) if session else {}

    async def _invoke_agent(
        self,
        agent,
        *,
        user_id: str,
        session_id: str,
        message: str,
    ) -> str | None:
        """Run one specialist against the current shared session state."""
        runner = Runner(
            agent=agent,
            app_name=ADK_APP_NAME,
            session_service=self.session_service,
        )
        content = genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=message)],
        )
        final_text = None
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                text_parts = [part.text for part in event.content.parts if part.text]
                if text_parts:
                    final_text = "\n".join(text_parts)
        return final_text

    async def _complete_real_k6_pipeline(
        self,
        *,
        user_id: str,
        session_id: str,
        user_query: str,
        state: dict,
        agents_called: list[str],
    ) -> tuple[dict, dict] | None:
        async def invoke_and_refresh(agent, message: str) -> None:
            await self._invoke_agent(
                agent,
                user_id=user_id,
                session_id=session_id,
                message=message,
            )
            refreshed = await self._get_state(user_id, session_id)
            state.clear()
            state.update(refreshed)

        pipeline = await complete_real_k6_pipeline(
            state=state,
            user_query=user_query,
            invoke_agent=invoke_and_refresh,
            monitoring_agent=monitoring_agent,
            security_agent=security_agent,
            analysis_agent=analysis_agent,
            report_agent=report_agent,
            agents_called=agents_called,
        )
        return (state, pipeline) if pipeline is not None else None

    async def execute(
        self,
        user_query: str,
        execution_context: dict | None = None,
    ) -> dict:
        user_id = "api_user"
        session_id = str(uuid.uuid4())

        context = execution_context or {}
        test_case_id = extract_catalog_test_case_id(user_query)
        if test_case_id:
            supplied_case_id = context.get("test_case_id")
            if supplied_case_id and supplied_case_id.upper() != test_case_id:
                raise ValueError(
                    "The request's catalog test case does not match the "
                    "provided execution context."
                )
            catalog_case = get_test_case(test_case_id)
            job_context = create_context_for_test_case(
                catalog_case,
                source_id=context.get("execution_source_id") or "API_CHAT",
            )
        elif is_k6_test_request(user_query):
            execution_mode = "REAL"
        else:
            execution_mode = (
                "SIMULATED"
                if is_simulated_tool_request(user_query)
                else context.get("execution_mode", "SIMULATED")
            )
        if not test_case_id:
            job_context = create_execution_job_context(
                execution_mode=execution_mode,
                workload_profile=context.get("workload_profile"),
                source_id=context.get("execution_source_id"),
                job_id=context.get("job_id"),
                test_case_name=context.get("test_case_name"),
            )

        await self.session_service.create_session(
            app_name=ADK_APP_NAME,
            user_id=user_id,
            session_id=session_id,
            state=job_context,
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
        state = await self._get_state(user_id, session_id)

        pipeline_result = await self._complete_real_k6_pipeline(
            user_id=user_id,
            session_id=session_id,
            user_query=user_query,
            state=state,
            agents_called=agents_called,
        )
        if pipeline_result is not None:
            state, pipeline_status = pipeline_result
            report_payload = json_object(state.get("report_result"))
            if report_payload is not None:
                state["report_result"] = report_payload
                if report_payload.get("file_path"):
                    final_text = (
                        "REAL k6 pipeline completed. Final report: "
                        f"{report_payload['file_path']}"
                    )
                else:
                    final_text = (
                        "REAL k6 pipeline completed, but the report agent "
                        "did not return a report file path."
                    )
            elif "report" in pipeline_status:
                final_text = (
                    "REAL k6 pipeline did not complete report generation. "
                    f"Stage status: {pipeline_status['report']}"
                )

        logger.info(f"Agents called: {agents_called}")
        logger.info("Orchestrator run complete")

        artifact_manifest = state.get("execution_artifacts") or {}
        artifacts = (
            artifact_manifest.get("artifacts", {})
            if isinstance(artifact_manifest, dict)
            else {}
        )
        report = json_object(state.get("report_result"))
        report_artifacts = (
            report.get("artifacts", {})
            if isinstance(report, dict)
            else {}
        )
        registered_artifacts: dict[str, str] = {}
        job_id = state.get("job_id")
        execution_mode = state.get("execution_mode", "SIMULATED")
        if isinstance(job_id, str) and isinstance(artifacts, dict):
            job_directory = resolve_artifact_directory(job_id)
            for key, filename in {**artifacts, **(
                report_artifacts if isinstance(report_artifacts, dict) else {}
            )}.items():
                if (
                    not isinstance(key, str)
                    or not isinstance(filename, str)
                    or Path(filename).name != filename
                ):
                    continue
                artifact_path = (job_directory / filename).resolve()
                if (
                    artifact_path.parent == job_directory
                    and artifact_path.is_file()
                ):
                    registered_artifacts[key] = filename
            if registered_artifacts:
                stored_manifest = write_artifact_manifest(
                    job_id,
                    execution_mode,
                    registered_artifacts,
                )
                public_base_url = os.getenv(
                    "ARTIFACT_PUBLIC_BASE_URL",
                    "",
                ).rstrip("/")
                artifact_references = {
                    key: (
                        f"{public_base_url}/artifacts/{job_id}/{key}"
                        if public_base_url
                        else f"/artifacts/{job_id}/{key}"
                    )
                    for key in registered_artifacts
                }
                artifact_expiration = stored_manifest["expires_at"]
            else:
                artifact_references = {}
                artifact_expiration = None
        else:
            artifact_references = {}
            artifact_expiration = None

        if report:
            report = dict(report)
            report["final_response"] = final_text
            report["execution_job"] = {
                "job_id": job_id,
                "execution_mode": execution_mode,
                "status": state.get("execution_status", "not_started"),
                "pipeline_stages": state.get("real_k6_pipeline"),
                "artifact_directory": (
                    artifact_directory_reference(job_id)
                    if job_id
                    else None
                ),
                "artifacts": artifact_references,
                "artifact_expires_at": artifact_expiration,
                "artifact_retention_days": (
                    artifact_retention_days()
                    if registered_artifacts
                    else None
                ),
            }
            return report

        public_state = dict(state)
        if public_state.get("job_id"):
            public_state["execution_artifact_directory"] = (
                artifact_directory_reference(public_state["job_id"])
            )

        return {
            "message": final_text or "Execution completed",
            "agents_called": agents_called,
            "execution_job": {
                "job_id": job_id,
                "execution_mode": execution_mode,
                "status": state.get("execution_status", "not_started"),
                "pipeline_stages": state.get("real_k6_pipeline"),
                "artifact_directory": (
                    artifact_directory_reference(job_id)
                    if job_id
                    else None
                ),
                "artifacts": artifact_references,
                "artifact_expires_at": artifact_expiration,
                "artifact_retention_days": (
                    artifact_retention_days()
                    if registered_artifacts
                    else None
                ),
            },
            "state": public_state,
        }
