from Performance_Testing_Agent.jira_agent_integration.app.jira_client import get_pending_issues, transition_issue, download_attachment

from Performance_Testing_Agent.jira_agent_integration.attachment_service import extract_attachment, MAX_ATTACHMENTS_PER_ISSUE, SUPPORTED_EXTENSIONS

from Performance_Testing_Agent.jira_agent_integration.adk_runner import run_orchestrator


async def extract_issue_attachments(attachments):
    """
    Download and extract supported Jira attachments.
    """

    extracted = []

    supported_count = 0

    for attachment in attachments:

        if supported_count >= MAX_ATTACHMENTS_PER_ISSUE:
            extracted.append(
                "[Additional attachment skipped because "
                "the attachment count limit was reached.]"
            )
            break

        filename = attachment.get("filename", "")
        attachment_id = attachment.get("id")

        extension = (
            "." + filename.rsplit(".", 1)[-1].lower()
            if "." in filename
            else ""
        )

        if extension not in SUPPORTED_EXTENSIONS:
            print(f"Skipping unsupported attachment: {filename}")
            continue
        
        try:
            print(
                f"Downloading attachment: "
                f"{filename} ({attachment_id})"
            )

            content = download_attachment(attachment_id)

            text = extract_attachment(filename, content)

            extracted.append(
                f"--- Attachment: {filename} ---\n"
                f"{text}"
            )

            supported_count += 1

        except Exception as e:
            print(
                f"Failed to process attachment "
                f"{filename}: {e}"
            )

            extracted.append(
                f"--- Attachment: {filename} ---\n"
                f"[Attachment could not be processed: {e}]"
            )

    return "\n\n".join(extracted)

async def process_single_issue(issue):
    issue_key = issue["key"]
    fields = issue["fields"]

    summary = fields.get("summary", "")
    description = fields.get("description", "")
    attachments = fields.get("attachment", [])

    attachment_content = await extract_issue_attachments(attachments)

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

