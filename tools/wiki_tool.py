"""
Simplified Wikipedia search tool (no external API key required).
Use this as a fallback when Serper API is not available.
"""
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class WikipediaSearchInput(BaseModel):
    """Input schema for WikipediaSearchTool."""
    query: str = Field(..., description="Search query for Wikipedia")


class WikipediaSearchTool(BaseTool):
    name: str = "Wikipedia Search"
    description: str = "Search Wikipedia for historical information about World War 2 topics"
    args_schema: Type[BaseModel] = WikipediaSearchInput

    def _run(self, query: str) -> str:
        """Search Wikipedia for information."""
        try:
            import wikipedia
            results = wikipedia.search(query, results=3)
            if not results:
                return f"No Wikipedia results found for '{query}'"

            page = wikipedia.page(results[0])
            summary = page.content[:1500] + "..."
            return f"Wikipedia: {page.title}\n\n{summary}\n\nSource: {page.url}"
        except Exception as e:
            return f"Error searching Wikipedia: {str(e)}"

wikipedia_tool = WikipediaSearchTool()
search_tool = wikipedia_tool
