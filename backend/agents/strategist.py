from langchain_groq import ChatGroq
from state import AgentState

llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.3)

def strategist_node(state: AgentState):
    context = f"""
    Research: {state.get('research_notes', 'N/A')}
    Finances: {state.get('financial_stats', 'N/A')}
    Competitors: {state.get('competitor_analysis', 'N/A')}
    """

    prompt = (
        f"Using this context: {context}\n\n"
        "Provide a 2-sentence SWOT summary and one clear strategic recommendation."
    )

    response = llm.invoke(prompt)

    return {
        "strategy_report": response.content,
        "messages": ["Strategist: Finalized SWOT and recommendations."],
        "revision_number": 1
    }