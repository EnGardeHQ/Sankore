# Sankore Completion Todo List
**For: Separate Coding Agent**  
**Project**: Sankore Intelligence Layer - Phases 3 & 4  
**Location**: `/Users/cope/EnGardeHQ/Sankore/`

---

## Phase 3: Bug Fixes & Deployment

### 3.1 Fix UUID Serialization Bug ⚠️ CRITICAL
**Problem**: Pydantic schemas expect `id: str` but database returns `UUID` objects, causing 500 errors.

**File**: `/Users/cope/EnGardeHQ/Sankore/src/api/v1/endpoints/trends.py`

**Changes Needed**:
1. Update `AdTrendResponse` schema to use `UUID` type:
   ```python
   from uuid import UUID
   
   class AdTrendResponse(BaseModel):
       id: UUID  # Change from str to UUID
       platform: str
       # ... rest of fields
       
       class Config:
           from_attributes = True
   ```

2. OR add a serializer in the endpoint to convert UUID to string:
   ```python
   @router.post("/fetch", response_model=List[AdTrendResponse])
   async def trigger_fetch_trends(...):
       result = await aggregator.fetch_and_store_trends(industry)
       return [
           {**trend.__dict__, "id": str(trend.id)} 
           for trend in result
       ]
   ```

**Verification**: Run `curl -X POST "http://127.0.0.1:8001/api/v1/trends/fetch?industry=Fashion"` - should return 200 with JSON array.

---

### 3.2 Fix OpenAI Client Error Handling
**Problem**: `CopyAnalyzerService` crashes when `OPENAI_API_KEY` is invalid/missing.

**File**: `/Users/cope/EnGardeHQ/Sankore/src/services/analysis/copy_analyzer.py`

**Changes Needed**:
1. Update `analyze_copy` method to check if client exists:
   ```python
   async def analyze_copy(self, ad_text: str, objective: str) -> CopyAnalysisResult:
       if not self.client:
           # Return mock data immediately
           return CopyAnalysisResult(
               score=75.0,
               hooks=["Detected Hook (Mock)"],
               ctas=["Detected CTA (Mock)"],
               improvements=["Add more urgency"],
               winning_patterns=["Benefit-First"]
           )
       
       try:
           response = await self.client.chat.completions.create(...)
           # ... existing logic
       except Exception as e:
           # Fallback to mock
           return CopyAnalysisResult(...)
   ```

**Verification**: Run `curl -X POST "http://127.0.0.1:8001/api/v1/analysis/audit-copy" -H "Content-Type: application/json" -d '{"text": "Buy now!", "objective": "conversion"}'` - should return 200 with mock data.

---

### 3.3 Add Production Database Configuration
**Problem**: Sankore currently uses SQLite for local dev but needs PostgreSQL for production.

**File**: `/Users/cope/EnGardeHQ/Sankore/.env.example` (CREATE THIS FILE)

**Changes Needed**:
1. Create `.env.example`:
   ```env
   # Database
   DATABASE_URL=postgresql+asyncpg://user:password@host:5432/sankore_db
   
   # API Keys
   OPENAI_API_KEY=sk-your-openai-key
   META_API_KEY=your-meta-access-token
   TIKTOK_ACCESS_TOKEN=your-tiktok-token
   
   # App Config
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   ```

2. Update `/Users/cope/EnGardeHQ/Sankore/README.md` (CREATE THIS FILE):
   ```markdown
   # Sankore Intelligence Layer
   
   ## Setup
   1. Copy `.env.example` to `.env`
   2. Update environment variables
   3. Install dependencies: `pip install -r requirements.txt`
   4. Run: `uvicorn src.main:app --reload`
   
   ## Endpoints
   - `GET /health` - Health check
   - `GET /api/v1/trends/` - List trends
   - `POST /api/v1/trends/fetch?industry={industry}` - Fetch trends
   - `POST /api/v1/analysis/audit-copy` - Analyze ad copy
   ```

---

### 3.4 Create Railway Deployment Configuration
**Problem**: Sankore needs to be deployed as a separate service on Railway.

**File**: `/Users/cope/EnGardeHQ/Sankore/railway.json` (CREATE THIS FILE)

**Changes Needed**:
1. Create Railway config:
   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "uvicorn src.main:app --host 0.0.0.0 --port $PORT",
       "restartPolicyType": "ON_FAILURE",
       "restartPolicyMaxRetries": 10
     }
   }
   ```

2. Create `Procfile`:
   ```
   web: uvicorn src.main:app --host 0.0.0.0 --port $PORT
   ```

3. Ensure `requirements.txt` has all dependencies (already exists).

**Verification**: Deploy to Railway, check logs for "Application startup complete".

---

### 3.5 Update En Garde API Gateway to Proxy Sankore
**Problem**: Frontend needs to access Sankore through the main En Garde backend.

**File**: `/Users/cope/EnGardeHQ/production-backend/app/main.py`

**Changes Needed**:
1. Add Sankore proxy route:
   ```python
   import httpx
   from fastapi import Request
   
   SANKORE_BASE_URL = os.getenv("SANKORE_API_URL", "http://localhost:8001")
   
   @app.api_route("/api/sankore/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
   async def proxy_sankore(request: Request, path: str):
       async with httpx.AsyncClient() as client:
           url = f"{SANKORE_BASE_URL}/{path}"
           response = await client.request(
               method=request.method,
               url=url,
               headers=dict(request.headers),
               content=await request.body()
           )
           return Response(
               content=response.content,
               status_code=response.status_code,
               headers=dict(response.headers)
           )
   ```

2. Add to Railway env vars: `SANKORE_API_URL=https://sankore-production.up.railway.app`

**Verification**: Call `https://your-backend.railway.app/api/sankore/health` - should return Sankore health check.

---

## Phase 4: Paid Ads Agent Integration

### 4.1 Create Sankore Service Client for Langflow
**Problem**: Paid Ads Agent (Langflow) needs to call Sankore for intelligence.

**File**: `/Users/cope/EnGardeHQ/production-backend/app/services/sankore_client.py` (CREATE THIS FILE)

**Changes Needed**:
```python
import httpx
import os
from typing import List, Dict

class SankoreClient:
    def __init__(self):
        self.base_url = os.getenv("SANKORE_API_URL", "http://localhost:8001")
    
    async def fetch_trends(self, industry: str) -> List[Dict]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/trends/fetch",
                params={"industry": industry}
            )
            response.raise_for_status()
            return response.json()
    
    async def analyze_copy(self, text: str, objective: str) -> Dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/analysis/audit-copy",
                json={"text": text, "objective": objective}
            )
            response.raise_for_status()
            return response.json()
```

---

### 4.2 Update Paid Ads Langflow Workflow
**Problem**: Langflow workflow needs to integrate Sankore intelligence.

**File**: `/Users/cope/EnGardeHQ/production-backend/app/services/langflow_workflow_templates.py`

**Changes Needed**:
1. Add Sankore intelligence step to `paid_ads_agent_workflow`:
   ```python
   # Add after campaign analysis, before recommendations
   {
       "id": "sankore_trends",
       "type": "custom_component",
       "data": {
           "name": "Fetch Industry Trends",
           "code": """
   from app.services.sankore_client import SankoreClient
   
   sankore = SankoreClient()
   trends = await sankore.fetch_trends(industry=user_industry)
   return {"trends": trends}
   """
       }
   }
   ```

---

### 4.3 Add Sankore Dashboard Widget
**Problem**: Users need to see Sankore insights in the dashboard.

**File**: `/Users/cope/EnGardeHQ/production-frontend/components/dashboard/SankoreInsightsWidget.tsx` (CREATE THIS FILE)

**Changes Needed**:
```typescript
import { useEffect, useState } from 'react';

interface Trend {
  platform: string;
  trend_name: string;
  trend_score: number;
  description: string;
}

export function SankoreInsightsWidget() {
  const [trends, setTrends] = useState<Trend[]>([]);
  
  useEffect(() => {
    fetch('/api/sankore/api/v1/trends/?limit=5')
      .then(res => res.json())
      .then(setTrends);
  }, []);
  
  return (
    <div className="sankore-widget">
      <h3>🔥 Trending Ad Formats</h3>
      {trends.map(trend => (
        <div key={trend.trend_name} className="trend-card">
          <span className="platform-badge">{trend.platform}</span>
          <h4>{trend.trend_name}</h4>
          <p>{trend.description}</p>
          <span className="score">Score: {trend.trend_score}</span>
        </div>
      ))}
    </div>
  );
}
```

**Integration**: Add to `/Users/cope/EnGardeHQ/production-frontend/components/dashboard/dashboard-preview-client.tsx`

---

## Testing Checklist

### Local Testing
- [ ] Start Sankore: `cd /Users/cope/EnGardeHQ/Sankore && uvicorn src.main:app --port 8001`
- [ ] Test health: `curl http://localhost:8001/health`
- [ ] Test trends fetch: `curl -X POST "http://localhost:8001/api/v1/trends/fetch?industry=Fashion"`
- [ ] Test copy analysis: `curl -X POST "http://localhost:8001/api/v1/analysis/audit-copy" -H "Content-Type: application/json" -d '{"text":"Buy now!","objective":"conversion"}'`

### Production Testing
- [ ] Deploy Sankore to Railway
- [ ] Verify DATABASE_URL connects to PostgreSQL
- [ ] Test proxy through En Garde backend: `curl https://backend.railway.app/api/sankore/health`
- [ ] Verify Langflow can call Sankore
- [ ] Check dashboard widget displays trends

---

## Environment Variables Needed

### Railway - Sankore Service
```
DATABASE_URL=<PostgreSQL connection string from Railway>
OPENAI_API_KEY=<from production-backend>
META_API_KEY=<from production-backend>
TIKTOK_ACCESS_TOKEN=<from production-backend>
SECRET_KEY=<generate new>
DEBUG=False
```

### Railway - Production Backend
```
SANKORE_API_URL=https://sankore-production.up.railway.app
```

---

## Priority Order
1. **3.1** - Fix UUID bug (CRITICAL - API is broken)
2. **3.2** - Fix OpenAI error handling (CRITICAL - API is broken)
3. **3.3** - Add production DB config (REQUIRED for deployment)
4. **3.4** - Create Railway config (REQUIRED for deployment)
5. **3.5** - Update API Gateway (REQUIRED for frontend access)
6. **4.1** - Create Sankore client (REQUIRED for Langflow)
7. **4.2** - Update Langflow workflow (FEATURE)
8. **4.3** - Add dashboard widget (FEATURE)

---

## Notes for Coding Agent
- All file paths are absolute from `/Users/cope/EnGardeHQ/`
- Sankore uses Python 3.9+, FastAPI, SQLAlchemy (async)
- Production backend uses FastAPI
- Frontend uses Next.js 14, TypeScript, React
- Test locally before deploying to Railway
- Verify each step before moving to next
