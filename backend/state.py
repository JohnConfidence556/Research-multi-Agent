from typing import TypedDict, Annotated, List
import operator

class AgentState(TypedDict):
    task: str
    messages: Annotated[List[str], operator.add]
    research_notes: str
    financial_stats: str
    competitor_analysis: str
    strategy_report: str       # Written by Strategist (SWOT summary)
    final_report: str          # Written by ReportWriter (full executive report) — NEW
    next_agent: str
    revision_number: Annotated[int, operator.add]