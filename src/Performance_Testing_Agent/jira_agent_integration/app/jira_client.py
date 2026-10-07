import requests

from Performance_Testing_Agent.jira_agent_integration.app.config import JIRA_API_TOKEN, JIRA_EMAIL, JIRA_URL, JIRA_PROJECT_KEY

def get_issue(issue_key: str):

    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}"

    response = requests.get(
        url,
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={
            "Accept": "application/json"})

    response.raise_for_status()

    return response.json()


def get_pending_issues():
    print("JIRA: Getting pending issues..")

    url = f"{JIRA_URL}/rest/api/3/search/jql"

    jql = (
        f'project = {JIRA_PROJECT_KEY} '
        'AND status = "To Do" '
        'AND labels = "agent-execute" '
        'ORDER BY created ASC'
    )

    response = requests.get(
        url,
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={
            "Accept": "application/json"
        },
        params={
            "jql": jql,
            "fields": (
                "summary,description,status,labels,attachment,"
                "customfield_10332"
            ),
            "maxResults": 10
        },
        timeout=30
    )

    print("JIRA: Pending issues response:", response.status_code)

    response.raise_for_status()

    data = response.json()

    # print("JIRA RESPONSE")
    # # print(data)

    # print("JQL:", jql)
    # print("Total issues returned:", data.get("total"))
    # print(
    #     "Issue Keys:",
    #     [issue["key"] for issue in data.get("issues", [])]
    # )

    return data

def get_transitions(issue_key: str):

    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"

    response = requests.get(
        url,
        auth = (JIRA_EMAIL, JIRA_API_TOKEN),
        headers = {
            "Accept": "application/json"
        },
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def transition_issue(issue_key: str, transition_id: str):

    print(
        f"JIRA: Transitioning {issue_key} "
        f"using transition {transition_id}..."
    )

    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/transitions"

    response = requests.post(
        url,
        auth = (JIRA_EMAIL, JIRA_API_TOKEN),
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
        json={
            "transition": {
                "id": transition_id
            }
        },
        timeout=30
    )

    print(
        f"JIRA: Transition response for {issue_key}: "
        f"{response.status_code}"
    )

    response.raise_for_status()

    if response.status_code == 204:
        return {
            "success": True,
            "status_code": 204
        }

    if response.content:
        return response.json()

    return{
        "success": True,
        "status_code": response.status_code
    }


MAX_ATTACHMENT_SIZE  = 10 * 1024 * 1024 #10MB

def download_attachment(attachment_id: str) -> bytes:
    """
    Download a Jira attachment safely with a size limit.
    """

    url = (
        f"{JIRA_URL}/rest/api/3/"
        f"attachment/content/{attachment_id}"
    )

    response = requests.get(
        url,
        auth = (JIRA_EMAIL, JIRA_API_TOKEN),
        headers={
            "Accept": "*/*"
        },
        stream=True,
        timeout=(10, 60),
    )

    response.raise_for_status()

    content_length = response.headers.get("Content-Length")

    if content_length:
        if int(content_length) > MAX_ATTACHMENT_SIZE:
            raise ValueError(
                "Attachment exceeds maximum allowed size."
            )
    
    chunks = []
    total_size=0

    for chunk in response.iter_content(chunk_size=64 * 1024):
        if not chunk:
            continue

        total_size += len(chunk)

        if total_size > MAX_ATTACHMENT_SIZE:
            raise ValueError(
                "Attachment exceeds maximum allowed size."
            ) 

        chunks.append(chunk)

    return b"".join(chunks)


# def get_current_user():
#     url = f"{JIRA_URL}/rest/api/3/myself"

#     response= requests.get(
#         url,
#         auth = (JIRA_EMAIL, JIRA_API_TOKEN),
#         headers = {
#             "Accept": "application/json"
#         },
#         timeout = 30
#     )

#     response.raise_for_status()

#     return response.json()


# def get_project(project_key: str):
#     url = f"{JIRA_URL}/rest/api/3/project/{project_key}"

#     response = requests.get(
#         url,
#         auth = (JIRA_EMAIL, JIRA_API_TOKEN)
#         headers = {
#             "Accept": "application/json"
#         },
#         timeout = 30
#     )

#     response.raise_for_status()

#     return response.json()

def find_test_case_fields():
    response = requests.get(
        f"{JIRA_URL.rstrip('/')}/rest/api/3/field",
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={"Accept": "application/json"},
        timeout=30,
    )
    response.raise_for_status() 

    return [
        field
        for field in response.json()
        if field.get("name") == "Test Case ID"
    ]


def inspect_field_contexts(field_id: str):
    response = requests.get(
        f"{JIRA_URL.rstrip('/')}/rest/api/3/field/{field_id}/context",
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={"Accept": "application/json"},
        timeout=30,
    )

    # Return diagnostic details even if Jira rejects this request.
    return {
        "status_code": response.status_code,
        "body": response.text,
    }



def add_issue_comment(issue_key: str, comment: str) -> dict:
    """Post a plain-text comment using Jira Cloud's document format."""

    if not isinstance(comment, str) or not comment.strip():
        raise ValueError("Jira comment cannot be empty.")

    # Jira Cloud REST API v3 expects Atlassian Document Format (ADF).
    paragraphs = []

    for line in comment.splitlines():
        paragraphs.append(
            {
                "type": "paragraph",
                "content": (
                    [{"type": "text", "text": line}]
                    if line
                    else []
                ),
            }
        )

    response = requests.post(
        f"{JIRA_URL.rstrip('/')}/rest/api/3/issue/{issue_key}/comment",
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        json={
            "body": {
                "type": "doc",
                "version": 1,
                "content": paragraphs,
            }
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json()














