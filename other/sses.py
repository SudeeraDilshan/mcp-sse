from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

async def event_stream():
    """Sends a new event every 2 seconds."""
    counter = 0
    while True:
        counter += 1
        yield f"data: Message {counter}\n\n"  # SSE format
        await asyncio.sleep(2)

@app.get("/sse")
async def sse_endpoint():
    """SSE endpoint that streams real-time events."""
    return StreamingResponse(event_stream(), media_type="text/event-stream")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
