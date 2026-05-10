import streamlit as st
import requests
import json
import time
import uuid

st.set_page_config(page_title="ARIA · War Room", layout="wide", page_icon="⬡", initial_sidebar_state="collapsed")

API_URL = "http://localhost:8000"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Mono', monospace !important; background-color: #07090f !important; color: #c8d6e5 !important; }
.main > div { padding-top: 0 !important; }
section[data-testid="stSidebar"] { display: none; }
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.aria-navbar { display:flex; align-items:center; justify-content:space-between; padding:14px 32px; border-bottom:1px solid rgba(255,255,255,0.06); background:#07090f; }
.aria-logo { font-family:'Syne',sans-serif !important; font-size:18px; font-weight:800; letter-spacing:-0.5px; color:#e8eef5 !important; }
.aria-logo span { color:#38bdf8; }
.aria-nav-pills { display:flex; gap:6px; align-items:center; }
.nav-pill { padding:5px 14px; border-radius:5px; font-size:11px; font-family:'DM Mono',monospace; letter-spacing:0.06em; color:#5a7087; border:1px solid transparent; }
.nav-pill.active { background:rgba(56,189,248,0.08); border-color:rgba(56,189,248,0.2); color:#38bdf8; }
.aria-status { display:flex; align-items:center; gap:7px; font-size:10px; color:#5a7087; font-family:'DM Mono',monospace; }
.pulse-dot { width:7px; height:7px; border-radius:50%; background:#34d399; box-shadow:0 0 6px #34d399; animation:pulse 2s ease-in-out infinite; display:inline-block; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
.hero-section { padding:28px 32px 18px; border-bottom:1px solid rgba(255,255,255,0.05); }
.hero-label { font-family:'Syne',sans-serif !important; font-size:24px; font-weight:700; color:#e8eef5; letter-spacing:-0.5px; margin-bottom:4px; }
.hero-sub { font-size:11px; color:#3d5166; font-family:'DM Mono',monospace; letter-spacing:0.04em; }
.stTextArea textarea { background:#0d1219 !important; border:1px solid rgba(255,255,255,0.08) !important; border-radius:8px !important; color:#c8d6e5 !important; font-family:'DM Mono',monospace !important; font-size:13px !important; padding:14px !important; resize:none !important; }
.stTextArea textarea:focus { border-color:rgba(56,189,248,0.35) !important; }
.stTextInput input { background:#0d1219 !important; border:1px solid rgba(255,255,255,0.08) !important; border-radius:6px !important; color:#c8d6e5 !important; font-family:'DM Mono',monospace !important; font-size:12px !important; }
.stButton > button { border-radius:7px !important; font-family:'DM Mono',monospace !important; font-size:12px !important; font-weight:500 !important; letter-spacing:0.04em !important; padding:10px 24px !important; transition:all 0.15s !important; border:none !important; width:100% !important; }
.stButton > button[kind="primary"] { background:#38bdf8 !important; color:#000 !important; }
.stButton > button[kind="primary"]:hover { background:#7dd3fc !important; }
.stButton > button[kind="secondary"] { background:transparent !important; border:1px solid rgba(255,255,255,0.1) !important; color:#5a7087 !important; }
.stButton > button[kind="secondary"]:hover { border-color:rgba(52,211,153,0.3) !important; color:#34d399 !important; background:rgba(52,211,153,0.05) !important; }
.pipeline-track { display:flex; align-items:center; padding:18px 32px; border-bottom:1px solid rgba(255,255,255,0.05); background:#07090f; overflow-x:auto; }
.pipeline-step { display:flex; flex-direction:column; align-items:center; gap:6px; flex:1; position:relative; min-width:90px; }
.pipeline-step::after { content:''; position:absolute; top:14px; left:55%; width:90%; height:1px; background:rgba(255,255,255,0.08); z-index:0; }
.pipeline-step:last-child::after { display:none; }
.step-node { width:28px; height:28px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:11px; font-family:'DM Mono',monospace; z-index:1; border:1px solid rgba(255,255,255,0.1); background:#0d1219; color:#3d5166; position:relative; }
.step-node.done { background:rgba(52,211,153,0.12); border-color:rgba(52,211,153,0.4); color:#34d399; }
.step-node.active { background:rgba(56,189,248,0.12); border-color:rgba(56,189,248,0.5); color:#38bdf8; box-shadow:0 0 10px rgba(56,189,248,0.2); }
.step-node.paused { background:rgba(251,191,36,0.12); border-color:rgba(251,191,36,0.4); color:#fbbf24; }
.step-label { font-size:9px; font-family:'DM Mono',monospace; color:#3d5166; letter-spacing:0.06em; text-transform:uppercase; text-align:center; }
.step-label.done { color:#34d399; } .step-label.active { color:#38bdf8; } .step-label.paused { color:#fbbf24; }
.log-card { border:1px solid rgba(255,255,255,0.06); border-radius:8px; padding:12px 16px; margin-bottom:8px; background:#0d1219; border-left:3px solid transparent; }
.log-card.researcher { border-left-color:#38bdf8; } .log-card.financial { border-left-color:#34d399; }
.log-card.competitor { border-left-color:#a78bfa; } .log-card.strategist { border-left-color:#fbbf24; }
.log-card.report { border-left-color:#fb923c; } .log-card.supervisor { border-left-color:#334155; }
.log-card-header { display:flex; align-items:center; justify-content:space-between; margin-bottom:5px; }
.log-card-agent { font-size:10px; letter-spacing:0.1em; text-transform:uppercase; font-family:'DM Mono',monospace; }
.log-card-time { font-size:9px; color:#3d5166; font-family:'DM Mono',monospace; }
.log-card-msg { font-size:11px; color:#7a9ab5; line-height:1.5; font-family:'DM Mono',monospace; }
.breakpoint-banner { background:rgba(251,191,36,0.06); border:1px solid rgba(251,191,36,0.25); border-radius:8px; padding:16px 20px; display:flex; align-items:flex-start; gap:14px; margin-bottom:16px; }
.breakpoint-text { font-size:13px; color:#fbbf24; font-family:'DM Mono',monospace; font-weight:500; }
.breakpoint-sub { font-size:10px; color:#78581a; margin-top:4px; font-family:'DM Mono',monospace; line-height:1.6; }
.stProgress > div > div > div { background:linear-gradient(90deg,#38bdf8,#34d399) !important; border-radius:2px !important; }
.stProgress > div > div { background:#0d1219 !important; border-radius:2px !important; height:3px !important; }
hr { border-color:rgba(255,255,255,0.05) !important; }
[data-testid="metric-container"] { background:#0d1219 !important; border:1px solid rgba(255,255,255,0.07) !important; border-radius:8px !important; padding:14px !important; }
[data-testid="metric-container"] label { font-family:'DM Mono',monospace !important; font-size:10px !important; color:#3d5166 !important; text-transform:uppercase; letter-spacing:0.08em; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { font-family:'Syne',sans-serif !important; color:#e8eef5 !important; font-size:22px !important; font-weight:700 !important; }
.report-container { background:#0d1219; border:1px solid rgba(255,255,255,0.07); border-radius:10px; padding:28px 32px; color:#c8d6e5; }
.report-container h1,.report-container h2,.report-container h3 { font-family:'Syne',sans-serif !important; color:#e8eef5 !important; letter-spacing:-0.3px; }
.report-container h2 { border-bottom:1px solid rgba(255,255,255,0.07); padding-bottom:8px; margin-top:24px; }
.report-container p,.report-container li { color:#7a9ab5 !important; font-size:13px; line-height:1.7; font-family:'DM Mono',monospace; }
.thread-info { font-family:'DM Mono',monospace; font-size:9px; color:#3d5166; letter-spacing:0.08em; text-transform:uppercase; margin-top:4px; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
defaults = {
    "run_logs": [], "final_report": None, "pipeline_state": "idle",
    "agents_done": [], "run_count": 0, "last_task": "",
    "thread_id": str(uuid.uuid4())[:8],
    "swot_preview": None,   # Strategist output shown at approval screen
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def markdown_to_pdf_bytes(md_text: str) -> bytes:
    """Convert markdown text to PDF bytes using reportlab."""
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
        from reportlab.lib.enums import TA_LEFT
        import io, re

        buf = io.BytesIO()
        doc = SimpleDocTemplate(
            buf, pagesize=A4,
            leftMargin=20*mm, rightMargin=20*mm,
            topMargin=20*mm, bottomMargin=20*mm
        )

        styles = getSampleStyleSheet()
        # Custom styles
        title_style = ParagraphStyle("Title2", parent=styles["Normal"],
            fontName="Helvetica-Bold", fontSize=18, textColor=colors.HexColor("#e8eef5"),
            spaceAfter=6, backColor=colors.HexColor("#07090f"))
        h2_style = ParagraphStyle("H2", parent=styles["Normal"],
            fontName="Helvetica-Bold", fontSize=13, textColor=colors.HexColor("#38bdf8"),
            spaceBefore=14, spaceAfter=4)
        h3_style = ParagraphStyle("H3", parent=styles["Normal"],
            fontName="Helvetica-Bold", fontSize=11, textColor=colors.HexColor("#34d399"),
            spaceBefore=10, spaceAfter=3)
        body_style = ParagraphStyle("Body2", parent=styles["Normal"],
            fontName="Helvetica", fontSize=10, textColor=colors.HexColor("#c8d6e5"),
            leading=15, spaceAfter=4)
        bullet_style = ParagraphStyle("Bullet2", parent=body_style,
            leftIndent=14, bulletIndent=4, spaceAfter=2)

        story = []
        for line in md_text.split("\n"):
            line = line.rstrip()
            if not line:
                story.append(Spacer(1, 4))
                continue
            # Strip inline markdown (bold/italic)
            clean = re.sub(r'\*\*(.+?)\*\*', r'\1', line)
            clean = re.sub(r'\*(.+?)\*', r'\1', clean)
            clean = re.sub(r'`(.+?)`', r'\1', clean)
            # Escape XML special chars for reportlab
            clean = clean.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

            if line.startswith("# "):
                story.append(Paragraph(clean[2:], title_style))
                story.append(HRFlowable(width="100%", thickness=0.5,
                    color=colors.HexColor("#1e3a5f"), spaceAfter=8))
            elif line.startswith("## "):
                story.append(Paragraph(clean[3:], h2_style))
                story.append(HRFlowable(width="100%", thickness=0.3,
                    color=colors.HexColor("#1e3a5f"), spaceAfter=4))
            elif line.startswith("### "):
                story.append(Paragraph(clean[4:], h3_style))
            elif line.startswith("- ") or line.startswith("* "):
                story.append(Paragraph(f"• {clean[2:]}", bullet_style))
            elif re.match(r'^\d+\. ', line):
                num_text = re.sub(r'^\d+\. ', '', clean)
                story.append(Paragraph(f"  {num_text}", bullet_style))
            else:
                story.append(Paragraph(clean, body_style))

        doc.build(story)
        return buf.getvalue()
    except ImportError:
        # reportlab not installed — return None so caller can fallback
        return None

# ── Constants ──────────────────────────────────────────────────────────────────
AGENTS = [
    {"key": "Researcher",       "label": "Researcher", "icon": "R", "color": "researcher"},
    {"key": "FinancialAnalyst", "label": "Financials", "icon": "F", "color": "financial"},
    {"key": "CompetitorAgent",  "label": "Competitor", "icon": "C", "color": "competitor"},
    {"key": "Strategist",       "label": "Strategist", "icon": "S", "color": "strategist"},
    {"key": "ReportWriter",     "label": "Report",     "icon": "W", "color": "report"},
]
AGENT_KEYS = [a["key"] for a in AGENTS]

# ── Helpers ────────────────────────────────────────────────────────────────────
def agent_color(key):
    for a in AGENTS:
        if a["key"] == key:
            return a["color"]
    return "supervisor"

def step_class(key):
    if key in st.session_state.agents_done:
        return "done"
    if st.session_state.pipeline_state in ("paused", "resuming") and key == "Strategist":
        return "paused"
    return ""

def extract_messages(data):
    """
    Safely extract readable message text from node output.
    Handles: dict with 'messages' key, plain list, string, LangChain message objects.
    """
    try:
        if isinstance(data, dict):
            msgs = data.get("messages", [])
        elif isinstance(data, list):
            msgs = data
        else:
            return str(data)[:200]

        parts = []
        for m in msgs:
            if isinstance(m, str):
                parts.append(m)
            elif isinstance(m, dict):
                parts.append(m.get("content", str(m))[:200])
            elif hasattr(m, "content"):          # LangChain AIMessage / HumanMessage
                parts.append(str(m.content)[:200])
            else:
                parts.append(str(m)[:200])
        return " · ".join(parts) if parts else ""
    except Exception:
        return str(data)[:200]

def extract_report(node, data):
    if node != "ReportWriter":
        return None
    if isinstance(data, dict):
        # final_report is the correct key now; strategy_report is Strategist's SWOT only
        return data.get("final_report") or data.get("strategy_report")
    return None

def _render_logs(placeholder):
    html = ""
    for entry in reversed(st.session_state.run_logs[-30:]):
        html += f"""
        <div class="log-card {entry['color']}">
            <div class="log-card-header">
                <span class="log-card-agent">{entry['agent']}</span>
                <span class="log-card-time">{entry['time']}</span>
            </div>
            <div class="log-card-msg">{entry['msg']}</div>
        </div>"""
    placeholder.markdown(html, unsafe_allow_html=True)

def process_stream(resp, progress_bar, log_placeholder):
    """
    Consume SSE stream. Returns (final_report | None, hit_breakpoint: bool).
    Robust to data being a dict, list, or any other JSON value.
    """
    final_report = None

    for raw_line in resp.iter_lines():
        if not raw_line:
            continue
        line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
        if not line.startswith("data: "):
            continue
        try:
            payload = json.loads(line[6:])
        except json.JSONDecodeError:
            continue

        node = payload.get("node", "unknown")
        data = payload.get("data", {})

        if node in AGENT_KEYS and node not in st.session_state.agents_done:
            st.session_state.agents_done.append(node)

        pct = int(len(st.session_state.agents_done) / 5 * 100)
        progress_bar.progress(min(pct, 100), text=f"Running: {node}…")

        msg = extract_messages(data) or f"Node {node} executed."
        st.session_state.run_logs.append({
            "agent": node, "msg": msg[:300],
            "time": time.strftime("%H:%M:%S"), "color": agent_color(node),
        })
        _render_logs(log_placeholder)

        rep = extract_report(node, data)
        if rep:
            final_report = rep

        # Capture Strategist output for the approval preview screen
        if node == "Strategist" and isinstance(data, dict):
            swot = data.get("strategy_report")
            if swot:
                st.session_state.swot_preview = swot

        # Capture agent outputs for the approval review panel
        if node == "Researcher" and isinstance(data, dict):
            st.session_state["preview_research"] = data.get("research_notes", "")
        if node == "FinancialAnalyst" and isinstance(data, dict):
            st.session_state["preview_financials"] = data.get("financial_stats", "")
        if node == "CompetitorAgent" and isinstance(data, dict):
            st.session_state["preview_competitor"] = data.get("competitor_analysis", "")

    # Breakpoint = stream ended before Strategist ran
    hit_bp = ("Strategist" not in st.session_state.agents_done and
               "ReportWriter" not in st.session_state.agents_done)
    return final_report, hit_bp


# ── Navbar ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="aria-navbar">
    <div class="aria-logo">AR<span>IA</span>
        <span style="font-size:11px;color:#3d5166;font-family:'DM Mono',monospace;font-weight:400"> · War Room</span>
    </div>
    <div class="aria-nav-pills">
        <div class="nav-pill active">Dashboard</div>
        <div class="nav-pill">Reports</div>
        <div class="nav-pill">Sources</div>
        <div class="nav-pill">Settings</div>
    </div>
    <div class="aria-status"><span class="pulse-dot"></span> Backend connected</div>
</div>""", unsafe_allow_html=True)

# ── Stepper ────────────────────────────────────────────────────────────────────
step_html = '<div class="pipeline-track">'
for a in AGENTS:
    s  = step_class(a["key"])
    bp = " ⏸" if a["key"] == "Strategist" and s == "paused" else ""
    step_html += f'<div class="pipeline-step"><div class="step-node {s}">{a["icon"]}</div><div class="step-label {s}">{a["label"]}{bp}</div></div>'
step_html += "</div>"
st.markdown(step_html, unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
    <div class="hero-label">Intelligence Pipeline</div>
    <div class="hero-sub">Multi-agent · Real-time streaming · Human-in-the-loop</div>
</div>""", unsafe_allow_html=True)

col_input, col_side = st.columns([3, 1])
with col_input:
    task = st.text_area("", placeholder="e.g.  Analyze Nvidia's competitive position in the AI chip market for 2025",
                        height=90, label_visibility="collapsed")
with col_side:
    thread_id_input = st.text_input("Thread ID", value=st.session_state.thread_id,
        help="Unique session ID. Same ID = resume existing session. New ID = fresh run.")
    st.markdown('<div class="thread-info">auto-generated · edit to resume old session</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
    run_btn    = st.button("▶  Run Pipeline",     type="primary",   key="run")
    resume_btn = st.button("✓  Approve & Resume", type="secondary", key="resume")
    reset_btn  = st.button("↺  Reset",            type="secondary", key="reset")

# ── Metrics ────────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
m1.metric("Agents Completed", f"{len(st.session_state.agents_done)} / 5")
m2.metric("Pipeline Runs",    st.session_state.run_count)
m3.metric("Status",           st.session_state.pipeline_state.upper())
m4.metric("Thread ID",        st.session_state.thread_id)
st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ── Button logic ───────────────────────────────────────────────────────────────
if reset_btn:
    st.session_state.run_logs       = []
    st.session_state.final_report   = None
    st.session_state.agents_done    = []
    st.session_state.pipeline_state = "idle"
    st.session_state.last_task      = ""
    st.session_state.thread_id      = str(uuid.uuid4())[:8]
    st.session_state.swot_preview       = None
    st.session_state.preview_research   = "Not captured yet."
    st.session_state.preview_financials = "Not captured yet."
    st.session_state.preview_competitor = "Not captured yet."
    st.rerun()

if run_btn:
    if not task.strip():
        st.warning("Enter a research task above.")
    else:
        st.session_state.run_logs       = []
        st.session_state.final_report   = None
        st.session_state.agents_done    = []
        st.session_state.pipeline_state = "running"
        st.session_state.run_count     += 1
        st.session_state.last_task      = task.strip()
        st.session_state.thread_id      = thread_id_input
        st.rerun()

if resume_btn:
    if st.session_state.pipeline_state != "paused":
        st.warning("Pipeline is not paused. Run it first, then approve at the breakpoint.")
    else:
        st.session_state.pipeline_state = "resuming"
        st.rerun()

# ── RUNNING ────────────────────────────────────────────────────────────────────
if st.session_state.pipeline_state == "running":
    st.markdown("---")
    pb  = st.progress(0, text="Initialising pipeline…")
    lph = st.empty()
    try:
        with requests.post(f"{API_URL}/analyze/stream",
                json={"task": st.session_state.last_task, "thread_id": st.session_state.thread_id},
                stream=True, timeout=300) as r:
            r.raise_for_status()
            final, hit_bp = process_stream(r, pb, lph)
        st.session_state.pipeline_state = "complete" if final else ("paused" if hit_bp else "complete")
        if final:
            st.session_state.final_report = final
        st.rerun()
    except requests.exceptions.ConnectionError:
        st.error("❌  Cannot reach backend. Run: uvicorn main:server --port 8000")
        st.session_state.pipeline_state = "idle"
    except Exception as e:
        st.error(f"❌  Error: {e}")
        st.session_state.pipeline_state = "idle"

# ── RESUMING ───────────────────────────────────────────────────────────────────
elif st.session_state.pipeline_state == "resuming":
    st.markdown("---")
    pb  = st.progress(int(len(st.session_state.agents_done)/5*100), text="Resuming from Strategist…")
    lph = st.empty()
    _render_logs(lph)
    try:
        with requests.post(f"{API_URL}/analyze/resume",
                json={"task": st.session_state.last_task, "thread_id": st.session_state.thread_id},
                stream=True, timeout=300) as r:
            r.raise_for_status()
            final, _ = process_stream(r, pb, lph)
        if final:
            st.session_state.final_report = final
        st.session_state.pipeline_state = "complete"
        st.rerun()
    except requests.exceptions.ConnectionError:
        st.error("❌  Cannot reach backend.")
        st.session_state.pipeline_state = "paused"
    except Exception as e:
        st.error(f"❌  Resume error: {e}")
        st.session_state.pipeline_state = "paused"

# ── PAUSED ─────────────────────────────────────────────────────────────────────
elif st.session_state.pipeline_state == "paused":
    st.markdown("""
    <div class="breakpoint-banner">
        <div style="font-size:20px;margin-top:2px">⏸</div>
        <div>
            <div class="breakpoint-text">Human approval required before Strategist runs</div>
            <div class="breakpoint-sub">
                Researcher · FinancialAnalyst · CompetitorAgent have completed.<br>
                Review the intelligence gathered below. Approve to continue with Strategist → ReportWriter,
                or Reset to start over.
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # Split: left = agent logs, right = gathered intelligence for review
    lc, rc = st.columns([1, 1])

    with lc:
        st.markdown('<div style="font-size:9px;letter-spacing:0.12em;color:#3d5166;text-transform:uppercase;font-family:\'DM Mono\',monospace;margin-bottom:10px">Agent Log</div>', unsafe_allow_html=True)
        _render_logs(st.empty())

    with rc:
        st.markdown('<div style="font-size:9px;letter-spacing:0.12em;color:#3d5166;text-transform:uppercase;font-family:\'DM Mono\',monospace;margin-bottom:10px">Intelligence Gathered — Review Before Approving</div>', unsafe_allow_html=True)

        # Pull from session state — set during process_stream
        research   = st.session_state.get("preview_research",   "Not captured yet.")
        financials = st.session_state.get("preview_financials",  "Not captured yet.")
        competitor = st.session_state.get("preview_competitor",  "Not captured yet.")

        with st.expander("🔍 Research Notes", expanded=True):
            st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:11px;color:#7a9ab5;line-height:1.7;white-space:pre-wrap">{research}</div>', unsafe_allow_html=True)
        with st.expander("💰 Financial Data", expanded=False):
            st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:11px;color:#7a9ab5;line-height:1.7;white-space:pre-wrap">{financials}</div>', unsafe_allow_html=True)
        with st.expander("🏆 Competitor Analysis", expanded=False):
            st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:11px;color:#7a9ab5;line-height:1.7;white-space:pre-wrap">{competitor}</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:rgba(56,189,248,0.05);border:1px solid rgba(56,189,248,0.15);
            border-radius:6px;padding:10px 14px;font-family:'DM Mono',monospace;font-size:10px;color:#5a7087">
            ↑ Review the intelligence above, then click
            <strong style="color:#38bdf8">✓ Approve &amp; Resume</strong> in the top-right to proceed.
        </div>""", unsafe_allow_html=True)

# ── COMPLETE ───────────────────────────────────────────────────────────────────
elif st.session_state.pipeline_state == "complete":
    st.markdown('<div style="color:#34d399;font-size:11px;font-family:\'DM Mono\',monospace;letter-spacing:0.1em;padding:10px 0 16px">✓ PIPELINE COMPLETE</div>', unsafe_allow_html=True)
    lc, rc = st.columns([1, 1])
    with lc:
        st.markdown('<div style="font-size:9px;letter-spacing:0.12em;color:#3d5166;text-transform:uppercase;font-family:\'DM Mono\',monospace;margin-bottom:10px">Agent Log</div>', unsafe_allow_html=True)
        _render_logs(st.empty())
    with rc:
        st.markdown('<div style="font-size:9px;letter-spacing:0.12em;color:#3d5166;text-transform:uppercase;font-family:\'DM Mono\',monospace;margin-bottom:10px">Executive Report</div>', unsafe_allow_html=True)
        if st.session_state.final_report:
            st.markdown(f'<div class="report-container">{st.session_state.final_report}</div>', unsafe_allow_html=True)
            # PDF download
            pdf_bytes = markdown_to_pdf_bytes(st.session_state.final_report)
            if pdf_bytes:
                st.download_button(
                    label="⬇  Download Report (.pdf)",
                    data=pdf_bytes,
                    file_name=f"aria_report_{time.strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf"
                )
            else:
                st.warning("Install `reportlab` for PDF export: `pip install reportlab`")
                st.download_button(
                    label="⬇  Download Report (.md)",
                    data=st.session_state.final_report,
                    file_name=f"aria_report_{time.strftime('%Y%m%d_%H%M')}.md",
                    mime="text/markdown"
                )
        else:
            st.info("Pipeline completed but no report captured. Check that `report_writer.py` returns `{'strategy_report': ...}` in its output dict.")

# ── IDLE ───────────────────────────────────────────────────────────────────────
elif st.session_state.pipeline_state == "idle":
    if st.session_state.run_logs:
        _render_logs(st.empty())
    else:
        st.markdown("""
        <div style="padding:60px 32px;text-align:center;color:#3d5166">
            <div style="font-size:32px;margin-bottom:12px">⬡</div>
            <div style="font-family:'Syne',sans-serif;font-size:16px;color:#5a7087;font-weight:600">Ready to run</div>
            <div style="font-size:11px;margin-top:6px;font-family:'DM Mono',monospace">Enter a research task above and click ▶ Run Pipeline</div>
        </div>""", unsafe_allow_html=True)