from langchain_groq import ChatGroq
from tools.search_tools import get_web_search_tool
from state import AgentState

llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0)

def researcher_node(state: AgentState):
    """
    The Researcher Agent logic.
    It reads the task from the state, searches the web,
    and writes findings back to research_notes.
    """
    search_tool = get_web_search_tool()
    query = state["task"]
    results = search_tool.invoke({"query": query})

    # BUG WAS HERE: str(results)[1000] gets ONE char at index 1000
    # Fix: use [:2000] slice to get first 2000 chars as a summary
    summary = str(results)[:2000]

    return {
        "research_notes": summary,
        "messages": ["Researcher: I have gathered the latest news and trends."],
        "revision_number": 1  # increments the counter by 1
    }