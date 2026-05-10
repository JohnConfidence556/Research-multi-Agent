from langchain_groq import ChatGroq
from state import AgentState

llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0.1)

def report_writer_node(state: AgentState):
    """
    Final formatting agent. Takes all state data and creates a clean Markdown report.
    Writes to 'final_report' (not 'strategy_report') so the Supervisor can
    distinguish it from the Strategist's SWOT output.
    """
    context = f"""
RESEARCH NOTES:
{state.get('research_notes', 'N/A')}

FINANCIAL DATA:
{state.get('financial_stats', 'N/A')}

COMPETITOR ANALYSIS:
{state.get('competitor_analysis', 'N/A')}

STRATEGIC SWOT & RECOMMENDATIONS:
{state.get('strategy_report', 'N/A')}
"""

    prompt = (
        "You are a senior Business Intelligence Consultant. "
        "Using the research context below, write a comprehensive Executive Report in Markdown. "
        "Structure it with these sections:\n"
        "## Executive Summary\n"
        "## Market Research Findings\n"
        "## Financial Overview\n"
        "## Competitive Landscape\n"
        "## SWOT Analysis\n"
        "## Strategic Recommendations\n"
        "## Conclusion\n\n"
        "Use professional language, bullet points where appropriate, and be concise but thorough.\n\n"
        f"Context:\n{context}"
    )

    response = llm.invoke(prompt)

    return {
        "final_report": response.content,          # <-- separate key from strategy_report
        "messages": ["Report Writer: Executive report compiled successfully."],
        "revision_number": 1,
    }