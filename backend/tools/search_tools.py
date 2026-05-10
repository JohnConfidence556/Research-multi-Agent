import os
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

load_dotenv()

def get_web_search_tool():
    """
    Returns a tool that can search the internet.
    k=3 means it will return the top 3 most relevant results.
    """
    return TavilySearchResults(k=2)