from langgraph.graph import StateGraph, END
from state import AgentState
from langgraph.checkpoint.memory import MemorySaver

from agents.researcher import researcher_node
from agents.financial_analyst import financial_analyst_node
from agents.competitor import competitor_node
from agents.strategist import strategist_node
from agents.report_writer import report_writer_node

def supervisor_node(state: AgentState):
    """
    Decides which agent to call next.
    Uses direct Python logic first — only falls back to LLM if genuinely ambiguous.
    This prevents the LLM from hallucinating a repeated agent call.
    """
    research_done   = bool(state.get("research_notes", "").strip())
    financials_done = bool(state.get("financial_stats", "").strip())
    competitors_done= bool(state.get("competitor_analysis", "").strip())
    strategy_done   = bool(state.get("strategy_report", "").strip())
    report_done     = bool(state.get("final_report", "").strip())

    # ── Deterministic routing — no LLM needed ─────────────────────────────────
    if not research_done:
        next_dest = "Researcher"
    elif not financials_done:
        next_dest = "FinancialAnalyst"
    elif not competitors_done:
        next_dest = "CompetitorAgent"
    elif not strategy_done:
        next_dest = "Strategist"
    elif not report_done:
        next_dest = "ReportWriter"
    else:
        next_dest = "FINISH"

    print(
        f"--- SUPERVISOR [iter={state.get('revision_number',0)}]: → {next_dest} | "
        f"research={'✓' if research_done else '✗'} "
        f"financials={'✓' if financials_done else '✗'} "
        f"competitors={'✓' if competitors_done else '✗'} "
        f"strategy={'✓' if strategy_done else '✗'} "
        f"report={'✓' if report_done else '✗'} ---"
    )

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