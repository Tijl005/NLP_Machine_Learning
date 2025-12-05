"""
Simplified tools zonder externe API's - alleen Wikipedia
Gebruik deze als je geen Serper API key hebt
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
            # Zoek Wikipedia
            results = wikipedia.search(query, results=3)
            if not results:
                return f"No Wikipedia results found for '{query}'"
           
            # Pak eerste resultaat
            page = wikipedia.page(results[0])
            # Return eerste 1500 characters als samenvatting
            summary = page.content[:1500] + "..."
            return f"Wikipedia: {page.title}\n\n{summary}\n\nSource: {page.url}"
        except Exception as e:
            return f"Error searching Wikipedia: {str(e)}"
 
# Instantieer de tool
wikipedia_tool = WikipediaSearchTool()
search_tool = wikipedia_tool  # Gebruik Wikipedia als backup voor web search
