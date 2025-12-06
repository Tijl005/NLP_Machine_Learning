from crewai.tools import BaseTool
from serpapi import GoogleSearch
import os
from typing import Type
from pydantic import BaseModel, Field


class SearchOnlineInput(BaseModel):
    """Input schema for SearchOnlineTool."""
    query: str = Field(..., description="The search query string")


class SearchOnlineTool(BaseTool):
    name: str = "search_online"
    description: str = "Search the web using SerpAPI (Google Search) and return relevant results about World War II topics."
    args_schema: Type[BaseModel] = SearchOnlineInput

    def _run(self, query: str) -> str:
        """Execute the search."""
        # Get API key from environment variable
        api_key = os.getenv("SERPAPI_API_KEY")
        
        if not api_key:
            return "Error: SERPAPI_API_KEY not found in environment variables. Please add it to your .env file."
        
        try:
            # Perform the search
            params = {
                "q": query,
                "api_key": api_key,
                "num": 3,  # Limit to 3 results for efficiency
                "engine": "google"
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Extract organic results
            organic_results = results.get("organic_results", [])
            
            if not organic_results:
                return f"No results found for query: {query}"
            
            # Format the results
            formatted_results = []
            for idx, result in enumerate(organic_results[:3], 1):
                title = result.get("title", "No title")
                snippet = result.get("snippet", "No description available")
                link = result.get("link", "No link")
                
                formatted_results.append(
                    f"{idx}. {title}\n"
                    f"   {snippet}\n"
                    f"   URL: {link}\n"
                )
            
            return "\n".join(formatted_results)
            
        except Exception as e:
            return f"Error performing search: {str(e)}"


# Create an instance of the tool
search_online = SearchOnlineTool()
