from fastapi import FastAPI

from Performance_Testing_Agent.api_docs import docs_urls, ok
from Performance_Testing_Agent.jira_agent_integration.app.routes.jira import router as jira_router

TAGS_METADATA = [
    {"name": "System", "description": "Is the service running."},
    {
        "name": "Jira",
        "description": "Read Jira issues and run the performance-test workflow for them.",
    },
]

app = FastAPI(
    title="Jira Agent Integration API",
    description="API for integrating Jira with Agentic AI",
    version="1.0.0",
    openapi_tags=TAGS_METADATA,
    **docs_urls(),
)

app.include_router(jira_router)


@app.get(
    "/",
    tags=["System"],
    summary="Is the Jira API running",
    responses=ok({"message": "Jira Agent Integration API is running"}),
)
def root():
    return{
        "message" : "Jira Agent Integration API is running"
    }