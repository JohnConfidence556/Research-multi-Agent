import json
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from graph import app
import uvicorn

server = FastAPI(title="ARIA – AI BI War Room")
server.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class AnalysisRequest(BaseModel):
    task: str
    thread_id: str = "1"

def _serialize(obj):
    """Make any LangChain/Pydantic object JSON-safe."""
    if hasattr(obj, "dict"):
        return obj.dict()
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)

def _collect_stream(inputs, config):
    """Run app.stream() synchronously and collect all events."""
    events = []
    for event in app.stream(inputs, config=config, stream_mode="updates"):
        events.append(event)
    return events

@server.post("/analyze/stream")
async def stream_analysis(request: AnalysisRequest):
    """Start a fresh pipeline run and stream every node update as SSE."""
    async def event_generator():
        inputs = {"task": request.task, "messages": [], "revision_number": 0}
        config = {"configurable": {"thread_id": request.thread_id}}
        loop   = asyncio.get_event_loop()
        events = await loop.run_in_executor(None, _collect_stream, inputs, config)
        for event in events:
            for node, output in event.items():
                try:
                    yield f"data: {json.dumps({'node': node, 'data': output}, default=_serialize)}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'node': node, 'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@server.post("/analyze/resume")
async def resume_analysis(request: AnalysisRequest):
    """
    Resume the pipeline from the Strategist breakpoint.
    inputs=None tells LangGraph to continue from the last checkpoint.
    Streams Strategist + ReportWriter output back to the UI.
    """
    async def event_generator():
        config = {"configurable": {"thread_id": request.thread_id}}
        loop   = asyncio.get_event_loop()
        # None = resume from last checkpoint
        events = await loop.run_in_executor(None, _collect_stream, None, config)
        for event in events:
            for node, output in event.items():
                try:
                    yield f"data: {json.dumps({'node': node, 'data': output}, default=_serialize)}\n\n"
                except Exception as e:
                    yield f"data: {json.dumps({'node': node, 'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@server.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(server, host="0.0.0.0", port=8000, reload=False)