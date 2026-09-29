from fastapi import FastAPI

from Performance_Testing_Agent.jira_agent_integration.app.routes.jira import router as jira_router

app = FastAPI(
    title="Jira Agent Integration API",
    description="API for integrating Jira with Agentic AI",
    version="1.0.0"
)

app.include_router(jira_router)


@app.get("/")
def root():
    return{
        "message" : "Jira Agent Integration API is running"
    }