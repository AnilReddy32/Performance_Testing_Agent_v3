import asyncio

from Performance_Testing_Agent.jira_agent_integration.app.routes.jira import process_pending_issues

POLL_INTERVAL = 60

async def poll_jira():

    print("================================")
    print("Jira pollar started.")
    print(f"Polling INterval: {POLL_INTERVAL} seconds")
    print("=====================================")

    while True:

        try:
            print("Checking Jira for pending issues...")

            result = await process_pending_issues()

            print("Poll Results: ")
            print(result)

        except Exception as e:
            print(f"\nJira polling error: {e}")

        print(f"\nWaiting {POLL_INTERVAL} seconds...")

        await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(poll_jira())