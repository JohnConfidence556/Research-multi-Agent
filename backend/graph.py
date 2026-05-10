from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from state import AgentState
from langgraph.checkpoint.memory import MemorySaver

from agents.researcher import researcher_node
from agents.financial_analyst import financial_analyst_node
from agents.competitor import competitor_node
from agents.strategist import strategist_node
from agents.report_writer import report_writer_node

llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0)

def supervisor_node(state: AgentState):
    """
    Decides which agent to call next.
    Uses separate flags for strategy_report (Strategist) and final_report (ReportWriter)
    so the supervisor never confuses them.
    """
    research_done   = bool(state.get("research_notes"))
    financials_done = bool(state.get("financial_stats"))
    competitors_done= bool(state.get("competitor_analysis"))
    strategy_done   = bool(state.get("strategy_report"))
    report_done     = bool(state.get("final_report"))      # ReportWriter output

    system_prompt = (
        "You are the Supervisor. Check the current state carefully:\n"
        f"- Research notes:      {'[DONE]' if research_done    else '[MISSING]'}\n"
        f"- Financial stats:     {'[DONE]' if financials_done  else '[MISSING]'}\n"
        f"- Competitor analysis: {'[DONE]' if competitors_done else '[MISSING]'}\n"
        f"- Strategy/SWOT:       {'[DONE]' if strategy_done    else '[MISSING]'}\n"
        f"- Final report:        {'[DONE]' if report_done      else '[MISSING]'}\n\n"
        "Rules — follow in strict order:\n"
        "1. If Research notes is [MISSING]      → call 'Researcher'\n"
        "2. If Financial stats is [MISSING]     → call 'FinancialAnalyst'\n"
        "3. If Competitor analysis is [MISSING] → call 'CompetitorAgent'\n"
        "4. If Strategy/SWOT is [MISSING]       → call 'Strategist'\n"
        "5. If Final report is [MISSING]        → call 'ReportWriter'\n"
        "6. If Final report is [DONE]           → respond 'FINISH'\n\n"
        "IMPORTANT: Strategy/SWOT and Final report are DIFFERENT things. "
        "Even when Strategy/SWOT is [DONE], you must still call 'ReportWriter' "
        "unless Final report is also [DONE].\n\n"
        "Respond with ONLY the agent name or 'FINISH'. Nothing else."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "Task: {task}\nIteration: {revision_number}")
    ])

    chain = prompt | llm
    response = chain.invoke({
        "task": state["task"],
        "revision_number": state.get("revision_number", 0)
    })

    next_dest = response.content.strip()
    print(f"--- SUPERVISOR [iter={state.get('revision_number',0)}]: → {next_dest} ---")
    print(f"    research={research_done} financials={financials_done} "
          f"competitors={competitors_done} strategy={strategy_done} report={report_done}")

    return {"next_agent": next_dest}


def router(state: AgentState):
    # Safety kill switch
    if state.get("revision_number", 0) >= 12:
        print("--- SAFETY KILL: max iterations reached ---")
        return END

    decision = state.get("next_agent", "")

    if decision == "FINISH":
        return END

    valid = ["Researcher", "FinancialAnalyst", "CompetitorAgent", "Strategist", "ReportWriter"]
    if decision in valid:
        return decision

    print(f"--- ROUTER WARNING: unknown decision '{decision}', ending ---")
    return END


# ── Build graph ────────────────────────────────────────────────────────────────
workflow = StateGraph(AgentState)

workflow.add_node("Supervisor",       supervisor_node)
workflow.add_node("Researcher",       researcher_node)
workflow.add_node("FinancialAnalyst", financial_analyst_node)
workflow.add_node("CompetitorAgent",  competitor_node)
workflow.add_node("Strategist",       strategist_node)
workflow.add_node("ReportWriter",     report_writer_node)

workflow.set_entry_point("Supervisor")
workflow.add_conditional_edges("Supervisor", router)

workflow.add_edge("Researcher",       "Supervisor")
workflow.add_edge("FinancialAnalyst", "Supervisor")
workflow.add_edge("CompetitorAgent",  "Supervisor")
workflow.add_edge("Strategist",       "Supervisor")
workflow.add_edge("ReportWriter",     "Supervisor")

memory = MemorySaver()
app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["Strategist"]
)