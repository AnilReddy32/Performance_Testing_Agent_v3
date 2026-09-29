from Performance_Testing_Agent.jira_agent_integration.app.jira_client import get_pending_issues, transition_issue

from Performance_Testing_Agent.jira_agent_integration.adk_runner import run_orchestrator



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
        print(f"{issue_key}: Starting ADK orchestrator...")

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

        print(f"{issue_key}: FAILED - {e}")

        return {
            "issue_key": issue_key,
            "summary": summary,
            "status": "Failed",
            "error": str(e)
        }


async def process_pending_issues():

    print(f"Checking Jira for pending issues...")

    result = get_pending_issues()

    issues = result.get("issues", [])

    if not issues:
        print("No pending Jira issues found")

        return{
            "success": True,
            "message": "No pending Jira issues found",
            "processed": [],
        }

    processed = []

    for issue in issues:
        result = await process_single_issue(issue)
        processed.append(result)

    return {
        "success": True,
        "processed_count": len(processed),
        "processed": processed,
    }
