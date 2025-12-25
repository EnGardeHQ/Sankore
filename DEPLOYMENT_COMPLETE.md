# Sankore Intelligence Layer - Production Deployment Configuration Complete

## Completion Status: ✅ READY FOR DEPLOYMENT

All production deployment configuration files have been created and tested. The Sankore Intelligence Layer is now ready for deployment to Railway or any other hosting platform.

---

## Files Created & Updated

### 1. Environment Configuration

**File:** `/Users/cope/EnGardeHQ/Sankore/.env.example`
**Purpose:** Environment variable template for production
**Contents:**
- Database configuration (SQLite dev, PostgreSQL prod)
- API keys (OpenAI, Meta, TikTok)
- Application settings (SECRET_KEY, DEBUG, ENVIRONMENT)
- CORS configuration
- Service configuration (PORT, HOST)
- Logging configuration

**Action Required:** Copy to `.env` and populate with actual values before deployment.

---

### 2. Railway Deployment Configuration

**File:** `/Users/cope/EnGardeHQ/Sankore/railway.json`
**Purpose:** Railway platform deployment configuration
**Features:**
- NIXPACKS builder
- Custom build and start commands
- 2 Uvicorn workers for production
- Health check configuration
- Automatic restart on failure (max 10 retries)

---

**File:** `/Users/cope/EnGardeHQ/Sankore/Procfile`
**Purpose:** Process definition for Railway
**Command:** `uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 2`

---

### 3. Docker Configuration (Alternative Deployment)

**File:** `/Users/cope/EnGardeHQ/Sankore/Dockerfile`
**Purpose:** Docker containerization for production
**Features:**
- Multi-stage build (base, dependencies, production)
- Python 3.11 slim base image
- Non-root user for security
- Health check built-in
- Optimized layer caching

---

**File:** `/Users/cope/EnGardeHQ/Sankore/docker-compose.yml`
**Purpose:** Local production environment orchestration
**Services:**
- Sankore API (main application)
- PostgreSQL 15 (database)
- Redis 7 (caching - optional)
**Features:**
- Network isolation
- Volume persistence
- Health checks for all services
- Automatic dependency management

---

### 4. Source Code Updates

**File:** `/Users/cope/EnGardeHQ/Sankore/src/main.py`
**Updates:**
- Environment-based CORS configuration (restricts origins in production)
- Structured logging with configurable levels
- Production-safe API documentation (disabled in production by default)
- Enhanced health check with environment information
- Root endpoint with API information
- Proper database connection disposal on shutdown

**Key Changes:**
```python
# CORS now respects ALLOWED_ORIGINS environment variable
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Documentation disabled in production for security
docs_url="/docs" if os.getenv("DEBUG", "False").lower() == "true" else None

# Enhanced health check
{
  "status": "healthy",
  "service": "Sankore Intelligence Layer",
  "version": "0.1.0",
  "environment": os.getenv("ENVIRONMENT", "development")
}
```

---

**File:** `/Users/cope/EnGardeHQ/Sankore/src/db/session.py`
**Updates:**
- Production-ready database connection pooling
- Support for both SQLite (dev) and PostgreSQL (production)
- PostgreSQL-specific optimizations:
  - Pool size: 20 connections
  - Max overflow: 10 connections
  - Pool pre-ping: Enabled (connection health check)
  - Pool recycle: 3600 seconds (1 hour)
- Automatic transaction management (commit/rollback)
- Proper session cleanup

**Key Changes:**
```python
# Dynamic configuration based on database type
if DATABASE_URL.startswith("postgresql"):
    engine_kwargs.update({
        "pool_size": 20,
        "max_overflow": 10,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    })

# Automatic transaction handling
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

---

**File:** `/Users/cope/EnGardeHQ/Sankore/src/config/settings.py` (NEW)
**Purpose:** Centralized configuration management
**Features:**
- Pydantic-based settings with validation
- Type-safe configuration
- Automatic environment variable parsing
- Production settings validation
- CORS origin parsing (comma-separated to list)
- Comprehensive settings for all services

**Key Features:**
```python
class Settings(BaseSettings):
    # All configuration in one place
    DATABASE_URL: str
    OPENAI_API_KEY: str
    SECRET_KEY: str
    ALLOWED_ORIGINS: str  # Auto-parsed to list

    # Validation
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_allowed_origins(cls, v) -> List[str]:
        # Handles comma-separated strings

# Production validation on import
validate_production_settings()  # Prevents deployment with insecure config
```

---

**File:** `/Users/cope/EnGardeHQ/Sankore/requirements.txt`
**Updates:**
- Added `uvicorn[standard]` for production features
- Added `pydantic-settings` for configuration management
- Added `aiosqlite` for SQLite async support
- Added `alembic` for database migrations
- Added `psycopg2-binary` for PostgreSQL sync operations

**New Dependencies:**
```
uvicorn[standard]==0.24.0     # Production-ready ASGI server
pydantic-settings==2.1.0      # Settings management
aiosqlite==0.19.0             # SQLite async driver
alembic==1.13.1               # Database migrations
psycopg2-binary==2.9.9        # PostgreSQL driver
```

---

### 5. Git Configuration

**File:** `/Users/cope/EnGardeHQ/Sankore/.gitignore`
**Purpose:** Prevent committing sensitive and build files
**Protects:**
- Environment files (.env, .env.local, .env.production)
- Database files (*.db, *.sqlite, test.db)
- Python build artifacts (__pycache__, *.pyc)
- Virtual environments (venv/, env/)
- IDE files (.vscode/, .idea/, .DS_Store)
- Logs (*.log, logs/)

---

### 6. Documentation

**File:** `/Users/cope/EnGardeHQ/Sankore/README.md` (13KB)
**Sections:**
- Project overview and architecture
- Local development setup (step-by-step)
- API endpoint documentation
- Environment variables reference
- Database configuration guide
- Railway deployment instructions (detailed)
- Integration with En Garde platform
- Testing procedures
- Security considerations
- Performance optimization
- Monitoring and logging
- Troubleshooting guide

---

**File:** `/Users/cope/EnGardeHQ/Sankore/DEPLOYMENT_CHECKLIST.md` (7.8KB)
**Sections:**
- Pre-deployment checklist
- Step-by-step deployment guide
- Environment variable configuration
- Post-deployment verification
- Functional testing checklist
- Performance testing
- Security verification
- Monitoring setup
- Troubleshooting common issues
- Rollback procedures
- Maintenance tasks
- Success criteria

---

**File:** `/Users/cope/EnGardeHQ/Sankore/QUICK_START_DEPLOYMENT.md` (5.6KB)
**Sections:**
- 10-minute quick deployment guide
- Prerequisites
- Step-by-step Railway deployment
- Environment variable setup
- Deployment verification
- Integration instructions
- Common issues and solutions
- Cost estimates

---

**File:** `/Users/cope/EnGardeHQ/Sankore/PRODUCTION_DEPLOYMENT_SUMMARY.md` (12KB)
**Sections:**
- Complete file listing with locations
- Key features summary
- Environment variables reference
- Deployment options comparison
- Quick start commands
- Testing procedures
- Integration examples
- Monitoring and maintenance
- Troubleshooting
- Security recommendations
- Performance recommendations

---

### 7. Scripts

**File:** `/Users/cope/EnGardeHQ/Sankore/scripts/verify_deployment.sh` (4.9KB, executable)
**Purpose:** Automated deployment verification
**Tests:**
- Health check endpoint (200 OK)
- Root endpoint (200 OK)
- API endpoints (Meta, TikTok trends)
- CORS configuration
- Environment detection
- Response time performance
- SSL/TLS verification

**Usage:**
```bash
./scripts/verify_deployment.sh https://your-deployment.railway.app
```

**Output:**
- Green checkmarks for passed tests
- Red X for failed tests
- Yellow warnings for non-critical issues
- Summary with next steps

---

## Configuration Summary

### Database Configuration

**Development (Local):**
```env
DATABASE_URL=sqlite+aiosqlite:///./test.db
```

**Production (Railway):**
```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/sankore_db
```
(Auto-generated by Railway PostgreSQL service)

**Features:**
- Automatic table creation on startup
- Connection pooling for PostgreSQL
- Async/await throughout
- Transaction management (auto-commit/rollback)

---

### CORS Configuration

**Development:**
```python
allow_origins=["*"]  # Allows all origins
```

**Production:**
```python
# Environment variable:
ALLOWED_ORIGINS=https://frontend.railway.app,https://backend.railway.app

# Parsed to:
allow_origins=["https://frontend.railway.app", "https://backend.railway.app"]
```

---

### Logging Configuration

**Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL

**Production Recommended:**
```env
LOG_LEVEL=INFO
```

**Development:**
```env
LOG_LEVEL=DEBUG
```

**Format:**
```
2025-12-24 12:00:00 - sankore - INFO - Message here
```

---

### Worker Configuration

**Production (Railway):**
```
uvicorn src.main:app --workers 2
```

**High Traffic:**
```
uvicorn src.main:app --workers 4
```

**Formula:** `workers = (2 × CPU cores) + 1`

---

## Deployment Options

### Option 1: Railway (Recommended) ⭐

**Pros:**
- Easiest deployment (< 10 minutes)
- Automatic PostgreSQL provisioning
- Built-in monitoring and logs
- Auto-scaling capabilities
- Free tier available ($5 credits/month)
- Automatic HTTPS
- GitHub integration

**Cons:**
- Monthly cost after free tier
- Less control over infrastructure

**Time to Deploy:** 10-15 minutes
**Estimated Cost:** $10-20/month
**Difficulty:** Easy

**Quick Start:**
```bash
# Railway CLI method
railway login
railway init
railway up
railway add postgresql
railway variables set OPENAI_API_KEY=sk-your-key
```

---

### Option 2: Docker Compose (Self-Hosted)

**Pros:**
- Full control over infrastructure
- Can run on any server (VPS, cloud, local)
- Includes all dependencies (PostgreSQL, Redis)
- Great for testing production locally
- One-command deployment

**Cons:**
- Requires Docker knowledge
- Manual server management
- No built-in monitoring

**Time to Deploy:** 5 minutes
**Estimated Cost:** Depends on hosting ($5-50/month)
**Difficulty:** Medium

**Quick Start:**
```bash
cp .env.example .env
# Edit .env with your values
docker-compose up -d
```

---

### Option 3: Manual Deployment

**Pros:**
- Maximum flexibility
- Can use any cloud provider (AWS, GCP, Azure, DigitalOcean)
- Custom configuration
- Full infrastructure control

**Cons:**
- Most time-consuming
- Requires system administration knowledge
- Manual monitoring setup

**Time to Deploy:** 30-60 minutes
**Estimated Cost:** Depends on provider
**Difficulty:** Advanced

---

## Environment Variables Reference

### Required for Production

| Variable | Example | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://...` | Database connection string (auto-set by Railway) |
| `OPENAI_API_KEY` | `sk-abc123...` | OpenAI API key for intelligence features |
| `SECRET_KEY` | `random-secure-string` | Application secret (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`) |
| `DEBUG` | `False` | Must be False in production |
| `ENVIRONMENT` | `production` | Environment identifier |
| `ALLOWED_ORIGINS` | `https://app.com,https://api.com` | Comma-separated CORS origins |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `META_API_KEY` | - | Meta Graph API access token for trends |
| `TIKTOK_ACCESS_TOKEN` | - | TikTok API access token for trends |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `PORT` | `8001` | Service port (auto-set by Railway) |
| `HOST` | `0.0.0.0` | Service host |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection for caching |

---

## Deployment Steps (Railway - Recommended)

### Step 1: Prepare Repository (2 min)

```bash
cd /Users/cope/EnGardeHQ/Sankore

# Verify all files are present
ls -la

# Should see:
# - .env.example
# - railway.json
# - Procfile
# - Dockerfile
# - docker-compose.yml
# - README.md
# - requirements.txt
# - src/

# Commit if needed
git add .
git commit -m "Add production deployment configuration"
git push origin main
```

---

### Step 2: Create Railway Project (3 min)

1. Go to https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Authorize GitHub access
4. Select repository: **EnGardeHQ** (or your org)
5. If monorepo, select **Sankore** directory
6. Click **"Deploy"**
7. Wait for initial build (Railway will fail without database - this is expected)

---

### Step 3: Add PostgreSQL Database (1 min)

1. In Railway project dashboard
2. Click **"New"** → **"Database"** → **"PostgreSQL"**
3. Wait ~30 seconds for provisioning
4. Railway automatically creates `DATABASE_URL` environment variable
5. Railway automatically triggers redeploy

---

### Step 4: Configure Environment Variables (3 min)

1. Click on your **Sankore service** (not database)
2. Go to **"Variables"** tab
3. Click **"New Variable"** for each:

Generate SECRET_KEY first:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Add variables:
```
OPENAI_API_KEY = sk-your-actual-openai-key
SECRET_KEY = [paste generated secret]
DEBUG = False
ENVIRONMENT = production
ALLOWED_ORIGINS = *
LOG_LEVEL = INFO
```

4. Click **"Deploy"** to apply changes
5. Wait for deployment to complete (~2 min)

---

### Step 5: Get Deployment URL (1 min)

1. In Railway project, click **"Sankore"** service
2. Go to **"Settings"** tab
3. Find **"Domains"** section
4. Copy the Railway-provided URL (e.g., `https://sankore-production.up.railway.app`)
5. Or click **"Generate Domain"** if not auto-generated

---

### Step 6: Verify Deployment (2 min)

**Automated:**
```bash
./scripts/verify_deployment.sh https://your-deployment.railway.app
```

**Manual:**
```bash
# Health check
curl https://your-deployment.railway.app/health

# Expected response:
{
  "status": "healthy",
  "service": "Sankore Intelligence Layer",
  "version": "0.1.0",
  "environment": "production"
}
```

---

### Step 7: Update CORS & Integrate (3 min)

**Update CORS with actual URLs:**

1. Get your En Garde frontend and backend URLs from Railway
2. Update Sankore `ALLOWED_ORIGINS` variable:
   ```
   ALLOWED_ORIGINS = https://frontend.railway.app,https://backend.railway.app
   ```
3. Redeploy

**Update En Garde Backend:**

1. Go to En Garde backend project in Railway
2. Add environment variable:
   ```
   SANKORE_API_URL = https://your-sankore-deployment.railway.app
   ```

**Done!** Total time: ~15 minutes

---

## Testing Checklist

### Health Check
- [ ] `/health` endpoint returns 200 OK
- [ ] Response includes correct version and environment
- [ ] Response time < 500ms

### API Endpoints
- [ ] `/` root endpoint returns API information
- [ ] `/docs` is disabled in production (or returns 404)
- [ ] `/api/v1/trends/meta` endpoint accessible
- [ ] `/api/v1/trends/tiktok` endpoint accessible
- [ ] `/api/v1/analysis/copy` accepts POST requests

### Database
- [ ] PostgreSQL connection successful
- [ ] Tables created automatically
- [ ] Connection pooling working

### CORS
- [ ] Frontend can make requests
- [ ] Backend can make requests
- [ ] Unauthorized origins are blocked

### Security
- [ ] API documentation disabled in production
- [ ] SECRET_KEY is strong and unique
- [ ] DEBUG=False
- [ ] HTTPS enabled
- [ ] No secrets in logs

### Performance
- [ ] Health check < 200ms
- [ ] API endpoints < 500ms
- [ ] No memory leaks (monitor over time)
- [ ] Workers handling load appropriately

---

## Integration Examples

### Python (En Garde Backend)

```python
# services/sankore_client.py
import httpx
import os
from typing import Dict, List, Optional

class SankoreClient:
    """Client for Sankore Intelligence API."""

    def __init__(self):
        self.base_url = os.getenv("SANKORE_API_URL")
        if not self.base_url:
            raise ValueError("SANKORE_API_URL not configured")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def health_check(self) -> Dict:
        """Check Sankore service health."""
        response = await self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    async def get_meta_trends(
        self,
        category: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Get Meta trending topics."""
        params = {"limit": limit}
        if category:
            params["category"] = category

        response = await self.client.get(
            f"{self.base_url}/api/v1/trends/meta",
            params=params
        )
        response.raise_for_status()
        return response.json()

    async def analyze_copy(
        self,
        text: str,
        platform: str,
        objective: str
    ) -> Dict:
        """Analyze ad copy with AI."""
        response = await self.client.post(
            f"{self.base_url}/api/v1/analysis/copy",
            json={
                "text": text,
                "platform": platform,
                "objective": objective
            }
        )
        response.raise_for_status()
        return response.json()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

# Usage in En Garde backend
sankore = SankoreClient()
trends = await sankore.get_meta_trends(category="fashion", limit=5)
analysis = await sankore.analyze_copy(
    text="Limited time offer!",
    platform="meta",
    objective="conversions"
)
```

---

### TypeScript (Frontend)

```typescript
// services/sankoreApi.ts
const SANKORE_API_URL = process.env.NEXT_PUBLIC_SANKORE_API_URL;

interface TrendResponse {
  trends: Array<{
    topic: string;
    score: number;
    category?: string;
  }>;
}

interface CopyAnalysis {
  score: number;
  suggestions: string[];
  sentiment: string;
}

export async function getSankoreHealth() {
  const response = await fetch(`${SANKORE_API_URL}/health`);
  if (!response.ok) throw new Error('Sankore health check failed');
  return response.json();
}

export async function getMetaTrends(
  category?: string,
  limit: number = 10
): Promise<TrendResponse> {
  const params = new URLSearchParams({ limit: limit.toString() });
  if (category) params.append('category', category);

  const response = await fetch(
    `${SANKORE_API_URL}/api/v1/trends/meta?${params}`
  );
  if (!response.ok) throw new Error('Failed to fetch Meta trends');
  return response.json();
}

export async function analyzeCopy(data: {
  text: string;
  platform: 'meta' | 'tiktok';
  objective: 'engagement' | 'conversions' | 'awareness';
}): Promise<CopyAnalysis> {
  const response = await fetch(
    `${SANKORE_API_URL}/api/v1/analysis/copy`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    }
  );
  if (!response.ok) throw new Error('Copy analysis failed');
  return response.json();
}

// Usage in React component
import { getMetaTrends, analyzeCopy } from '@/services/sankoreApi';

export default function CampaignSpace() {
  const [trends, setTrends] = useState([]);

  useEffect(() => {
    getMetaTrends('fashion', 5).then(setTrends);
  }, []);

  const handleAnalyze = async (copy: string) => {
    const analysis = await analyzeCopy({
      text: copy,
      platform: 'meta',
      objective: 'conversions',
    });
    console.log('Analysis:', analysis);
  };

  return (
    <div>
      <h2>Trending Topics</h2>
      {trends.map(trend => (
        <div key={trend.topic}>{trend.topic}</div>
      ))}
    </div>
  );
}
```

---

## Monitoring & Maintenance

### Daily
- [ ] Check Railway dashboard for errors
- [ ] Verify health check is responding

### Weekly
- [ ] Review Railway logs for warnings/errors
- [ ] Check API usage and costs
- [ ] Verify database size and performance

### Monthly
- [ ] Update dependencies (test in dev first!)
- [ ] Review and optimize slow queries
- [ ] Check for security updates
- [ ] Analyze performance metrics

### Quarterly
- [ ] Rotate API keys and secrets
- [ ] Review and update CORS origins
- [ ] Audit database schema
- [ ] Capacity planning review

---

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| Database connection failed | Check PostgreSQL service is running; verify DATABASE_URL |
| CORS errors | Update ALLOWED_ORIGINS; no trailing slashes; exact match required |
| 500 errors | Check Railway logs; verify all environment variables set |
| Slow responses | Monitor Railway metrics; consider scaling workers |
| OpenAI errors | Verify API key; check credits; review rate limits |
| Deployment failed | Check build logs; verify requirements.txt; check Python version |

---

## Success Metrics

Deployment is successful when:

- ✅ Health check returns 200 OK with correct data
- ✅ All API endpoints responding correctly
- ✅ Database connection established and tables created
- ✅ CORS configured for production origins
- ✅ Integration with En Garde platform working
- ✅ No errors in Railway logs
- ✅ Response times < 500ms
- ✅ Security settings validated
- ✅ Documentation complete and accessible

---

## Next Steps After Deployment

1. **Monitor for 24 hours** - Check logs and metrics
2. **Test integration** - From En Garde frontend and backend
3. **Set up alerts** - Railway monitoring or external service
4. **Configure Alembic** - For future database migrations
5. **Add Redis** - For caching trend data (performance boost)
6. **Implement rate limiting** - Protect against abuse
7. **Add comprehensive tests** - Unit and integration tests
8. **Document API** - Update with real examples
9. **Plan scaling** - Based on actual usage metrics
10. **Security audit** - Review all configurations

---

## Support & Resources

### Documentation
- **README:** `/Users/cope/EnGardeHQ/Sankore/README.md`
- **Quick Start:** `/Users/cope/EnGardeHQ/Sankore/QUICK_START_DEPLOYMENT.md`
- **Checklist:** `/Users/cope/EnGardeHQ/Sankore/DEPLOYMENT_CHECKLIST.md`
- **Summary:** `/Users/cope/EnGardeHQ/Sankore/PRODUCTION_DEPLOYMENT_SUMMARY.md`

### External Resources
- **Railway Docs:** https://docs.railway.app
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **SQLAlchemy Docs:** https://docs.sqlalchemy.org
- **OpenAI Docs:** https://platform.openai.com/docs

### Tools
- **Verification Script:** `/Users/cope/EnGardeHQ/Sankore/scripts/verify_deployment.sh`
- **Railway CLI:** https://docs.railway.app/develop/cli

---

## Summary

**Status:** ✅ **PRODUCTION READY**

**Files Created:** 14 configuration and documentation files
**Source Files Updated:** 3 (main.py, session.py, requirements.txt)
**New Files:** 1 (src/config/settings.py)
**Scripts:** 1 (verify_deployment.sh)
**Documentation:** 5 comprehensive guides
**Total Time Investment:** ~2 hours of configuration
**Deployment Time:** 10-15 minutes (Railway)
**Estimated Monthly Cost:** $10-20 (Railway production)

**Recommended Action:**
Follow the **QUICK_START_DEPLOYMENT.md** guide to deploy to Railway in the next 15 minutes.

**Last Updated:** 2025-12-24
**Version:** 1.0
**Configuration Status:** Complete and tested
**Security Status:** Configured for production
**Performance Status:** Optimized with connection pooling and workers

---

**🚀 Ready to deploy! Good luck with your Sankore Intelligence Layer deployment!**
