import pytest
from google.genai import types
from google.adk.runners import InMemoryRunner

from security_agent.agent import app


@pytest.fixture
def runner():
    return InMemoryRunner(app=app)


async def run_agent(runner, prompt: str):
    session = await runner.session_service.create_session(
        app_name=app.name,
        user_id="integration_test_user",
    )

    events = []

    async for event in runner.run_async(
        user_id="integration_test_user",
        session_id=session.id,
        new_message=types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt)
            ],
        ),
    ):
        events.append(event)

    return events


def get_final_response(events):
    for event in reversed(events):
        if event.is_final_response() and event.content:
            if event.content.parts:
                return event.content.parts[0].text

    return None


@pytest.mark.asyncio
async def test_security_agent_jwt_assessment(runner):
    events = await run_agent(
        runner,
        "Validate JWT authentication.",
    )

    response = get_final_response(events)

    assert response is not None
    assert len(response.strip()) > 0

    assert any(
        event.author == "security_agent"
        for event in events
    )


@pytest.mark.asyncio
async def test_security_agent_rbac_assessment(runner):
    events = await run_agent(
        runner,
        "Validate RBAC authorization.",
    )

    response = get_final_response(events)

    assert response is not None
    assert len(response.strip()) > 0

    assert any(
        event.author == "security_agent"
        for event in events
    )


@pytest.mark.asyncio
async def test_security_agent_overall_assessment(runner):
    events = await run_agent(
        runner,
        "Perform an overall security assessment.",
    )

    response = get_final_response(events)

    assert response is not None
    assert len(response.strip()) > 0

    assert any(
        event.author == "security_agent"
        for event in events
    )