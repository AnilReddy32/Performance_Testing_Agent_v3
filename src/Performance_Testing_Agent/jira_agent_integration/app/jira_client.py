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
            "fields": "summary,description,status,labels",
            "maxResults": 10
        },
        timeout=30
    )

    print("JIRA: Pending issues response:", response.status_code)

    response.raise_for_status()

    return response.json()

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

























