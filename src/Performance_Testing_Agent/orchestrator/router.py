import json
 
from langchain_google_genai import ChatGoogleGenerativeAI
 
from Performance_Testing_Agent.config import (

    GOOGLE_API_KEY,

    MODEL_NAME,

    TEMPERATURE,

)
 
from .prompts import ORCHESTRATOR_SYSTEM_PROMPT
 
 
class Router:

    """

    Router Agent
 
    Responsibilities:

    1. Analyze the user query.

    2. Send the query to Gemini.

    3. Determine which agents should be executed.

    4. Return the selected agents to the Orchestrator.

    """
 
    def __init__(self):

        self.llm = ChatGoogleGenerativeAI(

            model=MODEL_NAME,

            google_api_key=GOOGLE_API_KEY,

            temperature=TEMPERATURE,

        )
 
    async def route(self, user_query: str) -> list[str]:

        """

        Uses Gemini to determine which agents

        should be executed for the given user query.

        """
 
        prompt = f"""

{ORCHESTRATOR_SYSTEM_PROMPT}
 
User Query:

{user_query}

"""
 
        response = self.llm.invoke(prompt)
 
        content = response.content.strip()
 
        # Remove Markdown code fences if Gemini returns them

        if content.startswith("```json"):

            content = content.replace("```json", "", 1)
 
        if content.endswith("```"):

            content = content[:-3]
 
        content = content.strip()
 
        result = json.loads(content)
 
        return result["selected_agents"]
