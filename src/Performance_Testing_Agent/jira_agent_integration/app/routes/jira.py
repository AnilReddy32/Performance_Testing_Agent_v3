from fastapi import APIRouter, HTTPException

from Performance_Testing_Agent.jira_agent_integration.app.jira_client import get_issue, get_pending_issues, get_transitions, transition_issue

from Performance_Testing_Agent.jira_agent_integration.adk_runner import run_orchestrator

from Performance_Testing_Agent.jira_agent_integration.jira_service import process_pending_issues

router = APIRouter(
    prefix="/jira",
    tags=["Jira"]
)

@router.get("/issues/{issue_key}")
def get_jira_issue(issue_key: str):
    try:
        issue = get_issue(issue_key)

        return{
            "success": True,
            "issue": issue
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/execute/{issue_key}")
async def execute_jira_issue(issue_key: str):
    try:
        
        issue = get_issue(issue_key)

        summary = issue["fields"]["summary"]
        description = issue["fields"].get("description")

        agent_prompt = f"""
You have received a task from Jira.

Jira Issue Key:
{issue["key"]}

Summary:
{summary}

Description:
{description}

Analyze this jira request and execute the appropriate workflow using your available specialized agents.
"""

        agent_response = await run_orchestrator(agent_prompt)

        return{
            "success": True,
            "issue_key": issue["key"],
            "summary": summary,
            "agent_response": agent_response
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/pending")
def get_pending_jira_issues():
    try:
        result = get_pending_issues()

        return {
            "success": True,
            "issues": result.get("issues", [])
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/process-pending")
async def process_pending_issue():
    try:
        return await process_pending_issues()

    except Exception as e:
        raise HTTPException(
            status_code = 500,
            detail = str(e)
        )


@router.get("/transitions/{issue_key}")
def get_issue_transitions(issue_key: str):
    try:
        return get_transitions(issue_key)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


async def process_single_issue(issue):
    issue_key = issue["key"]
    fields = issue["fields"]

    summary = fields.get("summary", "")
    description = fields.get("description", "")

    print(f"==========PROCESSING {issue_key} ========")
    print(f"Summary: {summary}")

    print(f"{issue_key}: Moving to In Progress...")
    transition_issue(issue_key, "21")

    print(f"{issue_key}: Starting ADK orchestrator")

    agent_prompt = f"""
You have received a task from Jira.

Jira Issue Key:
{issue_key}

Summary:
{summary}

Description:
{description}

Analyze this request and execute the appropriate workflow using your available specialized agents.
"""


    try:
        agent_response = await run_orchestrator(agent_prompt)

        print(f"{issue_key}: ADK execution completed")

        print(f"{issue_key}: Moving to Done..")
        transition_issue(issue_key, "31")

        print(f"=========={issue_key} COMPLETED ============")

        return {
            "issue_key": issue_key,
            "summary": summary,
            "status": "Done",
            "agent_response": agent_response
        }
    
    except Exception as e:
        return {
            "issue_key": issue_key,
            "summary": summary,
            "status": "Failed",
            "error": str(e)
        }