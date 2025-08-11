import os
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from agno.agent import Agent, RunResponse, RunResponseEvent
from agno.models.google import Gemini
from dotenv import load_dotenv
from typing import Iterator
import json
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.wikipedia import WikipediaTools

load_dotenv()

app = FastAPI(title="AI Agent API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


api_key = os.getenv("GOOGLE_API_KEY")
agent = Agent(
    model=Gemini(id="gemini-2.0-flash-exp", api_key=api_key),
    markdown=True,
    tools=[WikipediaTools()],
    show_tool_calls=True,
)


def stream_agent_response(prompt: str) -> Iterator[str]:
    """Stream agent responses as Server-Sent Events"""
    try:
        response_stream: Iterator[RunResponseEvent] = agent.run(
            prompt, stream=True, stream_intermediate_steps=True
        )

        for event in response_stream:
            if event.event == "RunResponseContent":
                yield f"data: {json.dumps({'type': 'content', 'content': event.content})}\n\n"
            elif event.event == "RunResponseEnd":
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
                break

    except Exception as e:
        error_data = json.dumps({"type": "error", "error": str(e)})
        yield f"data: {error_data}\n\n"


@app.get("/")
async def root():
    return {"message": "AI Agent API is running"}


@app.post("/stream")
async def stream_response(request: Request):
    """Stream AI agent response"""
    body = await request.json()
    prompt = body.get("prompt", "Tell me a story about space exploration")

    return StreamingResponse(
        stream_agent_response(prompt),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        },
    )


@app.post("/chat")
async def chat(request: Request):
    """Simple chat endpoint that returns the full response"""
    body = await request.json()
    prompt = body.get("prompt", "Tell me a story about space exploration")

    try:
        response_stream: Iterator[RunResponseEvent] = agent.run(
            prompt, stream=False, stream_intermediate_steps=False  # Get full response
        )

        # Get the final response
        final_response = None
        for event in response_stream:
            if event.event == "RunResponseContent":
                final_response = event.content
                break

        return {"response": final_response}

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
