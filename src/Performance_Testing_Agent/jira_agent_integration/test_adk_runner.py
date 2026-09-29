import asyncio
from Performance_Testing_Agent.jira_agent_integration.adk_runner import run_orchestrator

async def main():
    response = await run_orchestrator(
        "Hello. confirm that you're the PTA Orchestrator"
    )

    print("==============AGENT RESPONSE=========")
    print(response)



if __name__ == "__main__":
    asyncio.run(main())