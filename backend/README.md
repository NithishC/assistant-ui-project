# Assistant UI Backend

FastAPI backend for the Assistant UI project, providing chat functionality with OpenAI integration.

## Features

- ✅ FastAPI REST API
- ✅ OpenAI GPT integration (gpt-3.5-turbo by default)
- ✅ Streaming and non-streaming responses
- ✅ CORS configuration for frontend integration
- ✅ Error handling and logging
- ✅ Test endpoint for development
- ✅ Environment-based configuration
- ✅ Auto-generated API documentation

## Setup

### 1. Navigate to backend directory
```bash
cd E:\assistant-ui-project\backend
```

### 2. Create virtual environment (optional but recommended)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
Copy `.env.example` to `.env` and add your OpenAI API key:
```bash
cp .env.example .env
```

Edit `.env`:
```
OPENAI_API_KEY=your-actual-openai-api-key-here
```

### 5. Run the server

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Or manually:**
```bash
python main.py
```

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Health check

### Chat Endpoints
- `POST /chat` - Main chat endpoint (supports streaming)
- `POST /chat/test` - Test endpoint (no OpenAI required)

### API Documentation
- `GET /docs` - Swagger UI documentation
- `GET /redoc` - ReDoc documentation

## Request Format

### Basic Chat Request
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  "model": "gpt-3.5-turbo",
  "temperature": 0.7,
  "max_tokens": 1000,
  "stream": false
}
```

### Streaming Request
Set `"stream": true` to receive Server-Sent Events stream.

## Response Format

### Non-streaming Response
```json
{
  "text": "Hello! How can I help you today?",
  "message": "Hello! How can I help you today?",
  "content": "Hello! How can I help you today?"
}
```

### Streaming Response (SSE)
```
data: {"text": "Hello", "type": "content"}
data: {"text": "!", "type": "content"}
data: {"type": "done"}
```

## Testing

### Test without OpenAI
Use the `/chat/test` endpoint to test the integration without needing an OpenAI API key:

```bash
curl -X POST http://localhost:8000/chat/test \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Test message"}]}'
```

### Test with curl
```bash
# Non-streaming
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello!"}]}'

# Streaming
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello!"}], "stream": true}'
```

## Configuration

Environment variables in `.env`:
- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `PORT` - Server port (default: 8000)
- `DEFAULT_MODEL` - Default model (default: gpt-3.5-turbo)
- `DEFAULT_TEMPERATURE` - Default temperature (default: 0.7)
- `DEFAULT_MAX_TOKENS` - Default max tokens (default: 1000)

## Troubleshooting

### CORS Issues
The backend is configured to accept requests from:
- http://localhost:3000 (default Next.js dev port)
- http://localhost:3001 (alternative port)

Add more origins in `main.py` if needed.

### OpenAI Errors
- **401 Authentication Error**: Check your API key in `.env`
- **429 Rate Limit**: You've exceeded OpenAI's rate limits
- **500 Server Error**: Check server logs for details

### Connection Refused
- Ensure the backend is running on port 8000
- Check if another service is using the port
- Try the test endpoint first: http://localhost:8000/chat/test

## Next Steps

With the backend running, the Assistant UI frontend should now be fully functional. You can:
1. Start conversations in the UI
2. Test streaming responses
3. Implement additional features like tool calling
4. Add authentication if needed
