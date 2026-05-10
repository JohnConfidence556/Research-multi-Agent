from langchain_groq import ChatGroq
from state import AgentState

llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.2)

def competitor_node(state: AgentState):
    notes = state.get("research_notes", "No research notes available.")

    prompt = (
        f"Based on these research notes: {notes}\n\n"
        "Identify the top 3 competitors and one key weakness for each. "
        "Format as a short numbered list."
    )

    response = llm.invoke(prompt)

    return {
        "competitor_analysis": response.content,
        "messages": ["Competitor Agent: Identified key market rivals."],
        "revision_number": 1
    }