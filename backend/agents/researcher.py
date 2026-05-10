from langchain_groq import ChatGroq
from tools.search_tools import get_web_search_tool
from state import AgentState

llm = ChatGroq(model="meta-llama/llama-4-scout-17b-16e-instruct", temperature=0)

def researcher_node(state: AgentState):
    """
    Researcher Agent.
    - Runs a web search for the task
    - Extracts readable text from results (not raw JSON)
    - Summarizes into clean research notes using the LLM
    - Writes a concise summary to research_notes so the Supervisor
      clearly sees research as [DONE] and moves on
    """

    search_tool = get_web_search_tool()
    query = state["task"]

    # Run the search
    raw_results = search_tool.invoke({"query": query})

    # ── Extract readable text from results ─────────────────────────────────────
    # search_tool can return a list of dicts or a string
    readable_chunks = []

    if isinstance(raw_results, list):
        for item in raw_results[:5]:   # take top 5 results
            if isinstance(item, dict):
                title   = item.get("title", "")
                content = item.get("content", item.get("snippet", ""))
                url     = item.get("url", item.get("link", ""))
                if content:
                    readable_chunks.append(f"SOURCE: {title}\nURL: {url}\n{content[:600]}")
            elif isinstance(item, str):
                readable_chunks.append(item[:600])
    elif isinstance(raw_results, str):
        readable_chunks.append(raw_results[:3000])
    else:
        readable_chunks.append(str(raw_results)[:3000])

    raw_text = "\n\n---\n\n".join(readable_chunks) if readable_chunks else "No results found."

    # ── Use LLM to turn raw search results into clean research notes ───────────
    summary_prompt = (
        f"You are a research analyst. Below are raw web search results for the query:\n"
        f'"{query}"\n\n'
        f"Search Results:\n{raw_text}\n\n"
        f"Write a concise, structured research summary (3-5 bullet points) covering:\n"
        f"- Key facts and figures\n"
        f"- Recent developments\n"
        f"- Market context\n\n"
        f"Write in plain text, no JSON, no URLs. Be factual and concise."
    )

    response = llm.invoke(summary_prompt)
    summary  = response.content.strip()

    # Fallback: if LLM returns empty, use truncated raw text
    if not summary:
        summary = raw_text[:1500]

    print(f"--- RESEARCHER: Summary generated ({len(summary)} chars) ---")

    return {
        "research_notes": summary,
        "messages": [f"Researcher: Research complete. Summary: {summary[:120]}..."],
        "revision_number": 1,
    }