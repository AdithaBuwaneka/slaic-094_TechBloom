from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI 
from app.core.config import settings
from .graph_state import GraphState
from typing import Optional 

class RouteQuery(BaseModel):
    """Represents a structured travel query."""
    tool_choice: str = Field(
        ...,
        description="The tool to use, must be 'google_maps_search' or 'database_search'."
    )
    origin: Optional[str] = Field(None, description="The starting point of the journey, if specified.")
    destination: Optional[str] = Field(None, description="The destination of the journey, if specified.")

class RouterAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            google_api_key=settings.GOOGLE_API_KEY
        )
        
        prompt_template = """You are an expert travel assistant in Sri Lanka. Your task is to analyze a user's query and decide the best tool to use.

You have two tools available:
1.  `Maps_search`: Use this for standard point-to-point travel requests (e.g., "how to get from Colombo to Kandy", "Galle Fort to Mirissa").
2.  `database_search`: Use this ONLY when the user specifically asks about a known bus route number (e.g., "tell me about the 138 bus", "what are the stops for route 177").

Based on the user query below, identify the origin, destination, and choose the correct tool. The tool choice must be either 'google_maps_search' or 'database_search'.

User Query:
{user_query}
"""
        prompt = ChatPromptTemplate.from_template(prompt_template)
        
        # This chains the prompt, the LLM, and the structured output parser
        self.structured_llm = prompt | self.llm.with_structured_output(RouteQuery)

    async def route_query(self, state: GraphState) -> GraphState:
        """Determines the next step based on the user query."""
        user_query = state['user_query']
        print(f"---ROUTING QUERY: {user_query}---")
        
        response: RouteQuery = await self.structured_llm.ainvoke({"user_query": user_query})
        
        print(f"---ROUTER DECISION: {response.tool_choice}---")
        
        state['tool_choice'] = response.tool_choice
        state['origin'] = response.origin
        state['destination'] = response.destination
        return state