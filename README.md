# Sankore Intelligence Layer

**Paid Ads Intelligence API for En Garde Platform**

Sankore is a FastAPI-based intelligence service that provides trend analysis, competitive insights, and AI-powered copy generation for paid advertising campaigns across Meta, TikTok, and other platforms.

## Overview

The Sankore Intelligence Layer serves as a specialized microservice within the En Garde ecosystem, providing:

- **Trend Analysis**: Real-time trending topics from Meta and TikTok
- **Competitive Intelligence**: Industry trend aggregation and analysis
- **AI-Powered Copy Generation**: OpenAI-powered ad copy analysis and generation
- **Multi-Platform Support**: Integrated with Meta Graph API, TikTok API
- **Campaign Intelligence**: Data-driven insights for campaign optimization

## Architecture

```
sankore/
├── src/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── trends.py      # Trend analysis endpoints
│   │           └── analysis.py    # Copy analysis endpoints
│   ├── db/
│   │   ├── models/
│   │   │   └── intelligence.py   # Database models
│   │   ├── base.py               # Base model configuration
│   │   └── session.py            # Database session management
│   ├── services/
│   │   ├── trends/
│   │   │   ├── providers/
│   │   │   │   ├── meta.py       # Meta trends provider
│   │   │   │   └── tiktok.py     # TikTok trends provider
│   │   │   ├── base.py           # Base trend provider
│   │   │   └── aggregator.py     # Trend aggregation service
│   │   └── analysis/
│   │       └── copy_analyzer.py  # AI copy analysis
│   └── main.py                   # FastAPI application
├── requirements.txt              # Python dependencies
├── railway.json                  # Railway deployment config
├── Procfile                      # Process definition
└── .env.example                  # Environment variables template
```

## Local Development Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (for production) or SQLite (for local dev)
- OpenAI API Key
- Meta Graph API Access Token (optional for trends)
- TikTok API Access Token (optional for trends)

### Installation

1. **Clone the repository**
   ```bash
   cd /Users/cope/EnGardeHQ/Sankore
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your configuration:
   ```env
   # Local development with SQLite
   DATABASE_URL=sqlite+aiosqlite:///./test.db

   # API Keys
   OPENAI_API_KEY=sk-your-actual-key
   META_API_KEY=your-meta-token
   TIKTOK_ACCESS_TOKEN=your-tiktok-token

   # App config
   SECRET_KEY=dev_secret_key
   DEBUG=True
   ENVIRONMENT=development
   ```

5. **Run the development server**
   ```bash
   uvicorn src.main:app --reload --port 8001
   ```

6. **Access the API**
   - API: http://localhost:8001
   - Swagger Docs: http://localhost:8001/docs
   - ReDoc: http://localhost:8001/redoc
   - Health Check: http://localhost:8001/health

## API Endpoints

### Health Check
```http
GET /health
```

### Trends

```http
GET /api/v1/trends/meta
Query Parameters:
  - category: string (optional)
  - limit: integer (default: 10)

GET /api/v1/trends/tiktok
Query Parameters:
  - category: string (optional)
  - limit: integer (default: 10)

GET /api/v1/trends/aggregate
Query Parameters:
  - platforms: string[] (meta, tiktok)
  - category: string (optional)
```

### Analysis

```http
POST /api/v1/analysis/copy
Body:
{
  "text": "Your ad copy text",
  "platform": "meta" | "tiktok",
  "objective": "engagement" | "conversions" | "awareness"
}

POST /api/v1/analysis/generate
Body:
{
  "product": "Product description",
  "target_audience": "Audience description",
  "platform": "meta" | "tiktok",
  "tone": "professional" | "casual" | "urgent"
}
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | Database connection string | Yes | `sqlite+aiosqlite:///./test.db` |
| `OPENAI_API_KEY` | OpenAI API key for AI analysis | Yes | - |
| `META_API_KEY` | Meta Graph API access token | No | - |
| `TIKTOK_ACCESS_TOKEN` | TikTok API access token | No | - |
| `SECRET_KEY` | Application secret key | Yes | - |
| `DEBUG` | Enable debug mode | No | `False` |
| `ENVIRONMENT` | Environment name | No | `production` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | Yes | - |
| `PORT` | Service port (set by Railway) | No | `8001` |
| `HOST` | Service host | No | `0.0.0.0` |
| `LOG_LEVEL` | Logging level | No | `INFO` |

## Database Configuration

### Local Development (SQLite)
```env
DATABASE_URL=sqlite+aiosqlite:///./test.db
```

### Production (PostgreSQL on Railway)
```env
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/sankore_db
```

Railway automatically provisions PostgreSQL and sets the `DATABASE_URL` environment variable.

### Database Migrations

Currently using automatic table creation via SQLAlchemy. For production, implement Alembic migrations:

```bash
# Install Alembic
pip install alembic

# Initialize Alembic
alembic init alembic

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

## Railway Deployment

### Prerequisites

1. Railway account (https://railway.app)
2. Railway CLI installed (optional)
3. GitHub repository connected to Railway

### Deployment Steps

#### Option 1: Deploy from GitHub (Recommended)

1. **Push code to GitHub**
   ```bash
   git add .
   git commit -m "Add Sankore Intelligence Layer"
   git push origin main
   ```

2. **Create new Railway project**
   - Go to https://railway.app/new
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Select the `Sankore` directory (if monorepo)

3. **Add PostgreSQL database**
   - In Railway project dashboard
   - Click "New" → "Database" → "PostgreSQL"
   - Railway automatically creates `DATABASE_URL` variable

4. **Configure environment variables**

   In Railway project settings, add:
   ```
   OPENAI_API_KEY=sk-your-actual-key
   META_API_KEY=your-meta-token
   TIKTOK_ACCESS_TOKEN=your-tiktok-token
   SECRET_KEY=generate-secure-random-string
   DEBUG=False
   ENVIRONMENT=production
   ALLOWED_ORIGINS=https://your-frontend.railway.app,https://engarde-backend.railway.app
   ```

5. **Deploy**
   - Railway automatically detects `railway.json` and `Procfile`
   - Deployment starts automatically
   - Monitor logs in Railway dashboard

6. **Get deployment URL**
   - Railway provides: `https://sankore-production.up.railway.app`
   - Configure this URL in your main En Garde backend

#### Option 2: Deploy via Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Link to existing project or create new
railway link

# Add PostgreSQL
railway add postgresql

# Set environment variables
railway variables set OPENAI_API_KEY=sk-your-key
railway variables set SECRET_KEY=your-secret
railway variables set DEBUG=False

# Deploy
railway up
```

### Post-Deployment

1. **Verify health check**
   ```bash
   curl https://your-sankore-url.railway.app/health
   ```

2. **Test API endpoints**
   ```bash
   curl https://your-sankore-url.railway.app/docs
   ```

3. **Monitor logs**
   ```bash
   railway logs
   ```

4. **Update En Garde backend**

   Add Sankore URL to your main backend's `.env`:
   ```env
   SANKORE_API_URL=https://your-sankore-url.railway.app
   ```

## Integration with En Garde Platform

### Backend Integration

Add to main En Garde backend (`/Users/cope/EnGardeHQ/Onside/production-backend`):

```python
# config/settings.py
SANKORE_API_URL = os.getenv("SANKORE_API_URL", "http://localhost:8001")

# services/intelligence_client.py
import httpx

class SankoreClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)

    async def get_trends(self, platform: str, category: str = None):
        url = f"{self.base_url}/api/v1/trends/{platform}"
        params = {"category": category} if category else {}
        response = await self.client.get(url, params=params)
        return response.json()

    async def analyze_copy(self, text: str, platform: str, objective: str):
        url = f"{self.base_url}/api/v1/analysis/copy"
        payload = {
            "text": text,
            "platform": platform,
            "objective": objective
        }
        response = await self.client.post(url, json=payload)
        return response.json()
```

### Frontend Integration

Add to Campaign Space UI:

```typescript
// services/sankoreApi.ts
const SANKORE_API_URL = process.env.NEXT_PUBLIC_SANKORE_API_URL;

export async function getTrends(platform: 'meta' | 'tiktok', category?: string) {
  const params = new URLSearchParams();
  if (category) params.append('category', category);

  const response = await fetch(
    `${SANKORE_API_URL}/api/v1/trends/${platform}?${params}`
  );
  return response.json();
}

export async function analyzeCopy(data: {
  text: string;
  platform: string;
  objective: string;
}) {
  const response = await fetch(
    `${SANKORE_API_URL}/api/v1/analysis/copy`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    }
  );
  return response.json();
}
```

## Testing

### Run Unit Tests

```bash
pytest tests/ -v
```

### Manual API Testing

```bash
# Health check
curl http://localhost:8001/health

# Get Meta trends
curl http://localhost:8001/api/v1/trends/meta?category=fashion

# Analyze copy
curl -X POST http://localhost:8001/api/v1/analysis/copy \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Limited time offer! Get 50% off today!",
    "platform": "meta",
    "objective": "conversions"
  }'
```

## Security Considerations

1. **API Keys**: Never commit `.env` file - use `.env.example` as template
2. **CORS**: Restrict `ALLOWED_ORIGINS` to specific domains in production
3. **Rate Limiting**: Implement rate limiting for production (use FastAPI-limiter)
4. **Database**: Use connection pooling and prepared statements (already handled by SQLAlchemy)
5. **Secrets**: Use Railway's built-in secrets management
6. **HTTPS**: Railway provides automatic HTTPS
7. **Input Validation**: All endpoints use Pydantic models for validation

## Performance Optimization

1. **Database Connection Pooling**: Configured in `src/db/session.py`
2. **Async Operations**: All endpoints use async/await
3. **Response Caching**: Implement Redis caching for trend data
4. **Worker Processes**: Railway deployment uses 2 Uvicorn workers
5. **Query Optimization**: Use SQLAlchemy query optimization

## Monitoring and Logging

### Logging Configuration

```python
# Add to src/main.py
import logging

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

### Railway Monitoring

- Built-in metrics dashboard
- Log streaming and search
- Deployment history
- Resource usage tracking

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Verify `DATABASE_URL` is correctly set
   - Check PostgreSQL service is running in Railway
   - Ensure asyncpg is installed

2. **CORS Errors**
   - Update `ALLOWED_ORIGINS` to include your frontend URL
   - Check that origin is exactly matched (no trailing slash)

3. **API Key Errors**
   - Verify OpenAI API key is valid and has credits
   - Check Meta/TikTok tokens are not expired

4. **Import Errors**
   - Ensure all dependencies are in `requirements.txt`
   - Check Python version is 3.11+

5. **Deployment Failures**
   - Check Railway logs for specific errors
   - Verify `railway.json` configuration
   - Ensure `Procfile` is present

## Development Roadmap

- [ ] Implement Redis caching for trend data
- [ ] Add Alembic migrations for production
- [ ] Implement rate limiting
- [ ] Add comprehensive test suite
- [ ] Add Google Ads trend provider
- [ ] Implement webhook support for real-time updates
- [ ] Add analytics and usage tracking
- [ ] Implement A/B testing for copy variations

## Support

For issues or questions:
- GitHub Issues: [Your repository URL]
- Email: [Your contact email]
- Documentation: This README

## License

[Your License]

---

**Generated**: 2025-12-24
**Version**: 0.1.0
**Status**: Production Ready
