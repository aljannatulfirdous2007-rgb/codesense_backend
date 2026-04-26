# CodeSense Backend v2

AI-powered code review API built with FastAPI, SQLAlchemy, and SQLite. Supports OpenAI integration for intelligent code analysis.

![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green?logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-silver)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-brightgreen?logo=openai)

## Features

- 🚀 **RESTful API** - Clean, well-documented endpoints
- 🧠 **AI-Powered Analysis** - OpenAI GPT-4 integration
- 💾 **Persistent Storage** - SQLite database for review history
- 🔄 **Mock Mode** - Works without API key for development
- 📊 **Structured Responses** - Consistent JSON format
- 🔒 **CORS Enabled** - Frontend-friendly from any origin

## API Endpoints

### Health Check
```
GET /
```
Returns service status and configuration.

### Analyze Code
```
POST /review-code
Content-Type: application/json

{
  "code": "function hello() {...}",
  "language": "javascript"
}
```

Returns detailed code analysis with bugs, improvements, and best practices.

### Get History
```
GET /history
```
Returns list of last 10 code reviews (summaries).

### Get Review Details
```
GET /history/{review_id}
```
Returns full details of a specific review.

### Delete Review
```
DELETE /history/{review_id}
```
Deletes a specific review from the database.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip package manager
- OpenAI API Key (optional - works in mock mode without it)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd codesense-backend-v2
```

2. Create a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```env
OPENAI_API_KEY=your-api-key-here
```

5. Run the server:
```bash
uvicorn main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) to see the API health check.

Access interactive API docs at [http://localhost:8000/docs](http://localhost:8000/docs)

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | No | Mock mode enabled |

### Mock Mode vs Real AI

**Mock Mode** (no API key):
- Returns realistic fake reviews
- Perfect for development and testing
- No external dependencies

**Real AI Mode** (with API key):
- Uses GPT-4-mini for analysis
- More accurate and insightful feedback
- Costs money per request

## Database

The application uses SQLite with the following structure:

**Table: `reviews`**
- `id` - Primary key
- `code` - Source code submitted
- `language` - Programming language
- `score` - Quality score (0-10)
- `bugs` - JSON array of identified bugs
- `improvements` - JSON array of suggestions
- `best_practices` - JSON array of best practices
- `created_at` - Timestamp

Database file is automatically created as `codesense.db` in the project directory.

## Project Structure

```
codesense-backend-v2/
├── main.py              # FastAPI application & routes
├── models.py            # SQLAlchemy database models
├── database.py          # Database connection setup
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── codesense.db         # SQLite database (auto-created)
```

## Tech Stack

- **Framework:** FastAPI
- **Database:** SQLite + SQLAlchemy
- **AI:** OpenAI GPT-4-mini (optional)
- **Validation:** Pydantic
- **Server:** Uvicorn ASGI

## Deployment

### Local Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Options

#### 1. Railway (Recommended)
1. Push to GitHub
2. Connect Railway to your repo
3. Set `OPENAI_API_KEY` environment variable
4. Deploy automatically

#### 2. Render
1. Create new Web Service
2. Connect GitHub repository
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### 3. Heroku
Create `Procfile`:
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

Deploy using Git:
```bash
git push heroku main
```

#### 4. DigitalOcean App Platform
1. Connect GitHub
2. Configure build and run commands
3. Set environment variables
4. Deploy

### Docker Deployment

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t codesense-backend .
docker run -p 8000:8000 codesense-backend
```

## Testing

### Using cURL
```bash
curl -X POST http://localhost:8000/review-code \
  -H "Content-Type: application/json" \
  -d '{"code": "function test() { return 1; }", "language": "javascript"}'
```

### Using Python
```python
import requests

response = requests.post(
    "http://localhost:8000/review-code",
    json={"code": "def hello(): return 'world'", "language": "python"}
)
print(response.json())
```

### Interactive Docs
Visit `http://localhost:8000/docs` for Swagger UI interface.

## Frontend Integration

This backend is designed to work with the CodeSense Frontend. Configure your frontend with:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production deployment:
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

## API Response Format

### Success Response
```json
{
  "id": 1,
  "score": 8.5,
  "bugs": [
    "Potential null reference error",
    "Missing error handling"
  ],
  "improvements": [
    "Use const instead of let",
    "Add input validation"
  ],
  "best_practices": [
    "Add JSDoc comments",
    "Use descriptive variable names"
  ],
  "language": "javascript",
  "created_at": "2024-01-15",
  "mock": false
}
```

### Error Response
```json
{
  "detail": "Code cannot be empty."
}
```

## Troubleshooting

### Database not created
- Ensure write permissions in directory
- Check SQLAlchemy installation: `pip install sqlalchemy`

### OpenAI errors
- Verify API key is correct
- Check internet connection
- Ensure `openai` package is installed

### CORS errors
- Backend allows all origins by default
- For production, update `allow_origins` in `main.py`

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.

## License

MIT License - free to use and modify.

## Acknowledgments

Powered by OpenAI's GPT models for intelligent code analysis.
