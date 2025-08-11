# AI Agent Streaming API

A FastAPI-based streaming API for AI agent responses using the Agno framework with Google's Gemini model.

## Features

- 🚀 **Real-time streaming** of AI agent responses
- 🔄 **Server-Sent Events (SSE)** for efficient streaming
- 🎯 **Multiple endpoints** for different use cases
- 🌐 **CORS enabled** for frontend integration
- 📱 **Responsive HTML demo** included

## Quick Start

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file in the project root:

```bash
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Run the Server

```bash
python main.py
```

The server will start on `http://localhost:8000`

### 4. Test the API

```bash
python test_api.py
```

### 5. Open the Demo Frontend

Open `index.html` in your browser to see the streaming in action!

## API Endpoints

### GET `/`

Health check endpoint that returns a simple message.

**Response:**

```json
{
  "message": "AI Agent API is running"
}
```

### POST `/chat`

Non-streaming endpoint that returns the complete AI response.

**Request:**

```json
{
  "prompt": "Tell me a story about space exploration"
}
```

**Response:**

```json
{
  "response": "Once upon a time, in the vast expanse of space..."
}
```

### POST `/stream`

Streaming endpoint that returns Server-Sent Events (SSE) for real-time updates.

**Request:**

```json
{
  "prompt": "Tell me a story about space exploration"
}
```

**Response:** Server-Sent Events stream with the following event types:

- `content`: AI-generated content
- `tool_call`: Tool usage information
- `reasoning`: AI reasoning steps
- `end`: Stream completion signal
- `error`: Error information

## Frontend Integration

### Using Server-Sent Events (SSE)

```javascript
const eventSource = new EventSource("/stream?prompt=Your prompt here");

eventSource.onmessage = function (event) {
  const data = JSON.parse(event.data);

  switch (data.type) {
    case "content":
      console.log("Content:", data.content);
      break;
    case "tool_call":
      console.log("Tool call:", data.tool);
      break;
    case "reasoning":
      console.log("Reasoning:", data.content);
      break;
    case "end":
      console.log("Stream completed");
      eventSource.close();
      break;
    case "error":
      console.error("Error:", data.error);
      break;
  }
};

eventSource.onerror = function (error) {
  console.error("EventSource error:", error);
};
```

### Using Fetch API

```javascript
const response = await fetch("/stream", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    prompt: "Your prompt here",
  }),
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const lines = chunk.split("\n");

  for (const line of lines) {
    if (line.startsWith("data: ")) {
      try {
        const data = JSON.parse(line.slice(6));
        console.log("Event:", data);
      } catch (e) {
        console.error("Parse error:", e);
      }
    }
  }
}
```

## Project Structure

```
ai/
├── main.py              # FastAPI server with streaming endpoints
├── index.html           # Demo frontend with SSE integration
├── test_api.py          # API testing script
├── pyproject.toml       # Project dependencies
├── uv.lock             # Lock file for dependencies
└── README.md            # This file
```

## Dependencies

- **FastAPI**: Modern web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **Agno**: AI agent framework
- **Google GenAI**: Google's Gemini model integration
- **Requests**: HTTP library for testing

## Development

### Adding New Endpoints

To add new streaming endpoints, follow this pattern:

```python
@app.post("/custom-stream")
async def custom_stream(request: Request):
    body = await request.json()
    # Your custom logic here

    return StreamingResponse(
        your_streaming_function(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream",
        }
    )
```

### Customizing the AI Agent

Modify the agent configuration in `main.py`:

```python
# Change model
agent = Agent(model=Gemini(id="gemini-2.0-flash-exp", api_key=api_key), markdown=True)

# Add custom tools, memory, or other configurations
```

## Troubleshooting

### Common Issues

1. **Connection refused**: Make sure the server is running on port 8000
2. **CORS errors**: The API includes CORS middleware, but you may need to configure origins for production
3. **API key errors**: Ensure your Google API key is set in the `.env` file
4. **Streaming stops**: Check browser console for errors and ensure the connection is stable

### Debug Mode

To run with debug logging:

```bash
uvicorn main:app --reload --log-level debug
```

## Production Considerations

- Configure CORS origins properly for production
- Add authentication and rate limiting
- Use environment variables for all sensitive configuration
- Consider using a reverse proxy like Nginx
- Implement proper error handling and logging
- Add health checks and monitoring

## License

This project is open source. Feel free to modify and distribute as needed.
