from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from tools.finance_tools import get_financial_data
from state import AgentState

llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0)

def financial_analyst_node(state: AgentState):
    """
    Analyzes financial health. Extracts ticker from context then fetches data.
    """
    context = f"User Task: {state['task']}\n\nResearch Findings: {state.get('research_notes', '')}"

    extraction_prompt = ChatPromptTemplate.from_template(
        "You are a financial expert. Based on the User Task and Research Findings below, "
        "identify the primary public company stock ticker symbol mentioned.\n\n"
        "Context: {context}\n\n"
        "Return ONLY the ticker symbol (e.g., TSLA). "
        "If no public company is identified, return 'NONE'."
    )

    chain = extraction_prompt | llm
    response = chain.invoke({"context": context})
    ticker = response.content.strip().upper()

    if ticker != "NONE":
        print(f"---- ANALYST: Fetching data for {ticker} ----")
        data = get_financial_data(ticker)
    else:
        data = "No specific public company ticker identified for financial analysis."

    return {
        "financial_stats": data,
        "messages": [f"Financial Analyst: Processed data for {ticker}."],
        "revision_number": 1
    }