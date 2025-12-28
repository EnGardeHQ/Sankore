# Sankore Lakehouse Architecture Upgrade Guide

## Overview

This guide upgrades Sankore (Paid Ads Walker Agent microservice) to include the full lakehouse architecture with:
- **Apache Airflow**: ETL processing via DAGs
- **MinIO**: S3-compatible object storage
- **Celery + Redis**: Asynchronous task processing
- **Flower**: Celery monitoring UI

## Current State

✅ **Already Implemented:**
- FastAPI application
- PostgreSQL database
- Redis caching
- Basic docker-compose.yml

❌ **Missing Components:**
- MinIO object storage
- Celery workers and beat scheduler
- Flower monitoring
- Airflow DAG infrastructure

## Files Created

### 1. `/Users/cope/EnGardeHQ/Sankore/dags/paid_ads_walker_dag.py` ✅

Complete Airflow DAG for Paid Ads Walker Agent with:
- Multi-platform data ingestion (Google Ads, Meta, LinkedIn, TikTok)
- ROAS calculation
- Budget optimization recommendations
- Creative performance analysis
- Trend alignment analysis
- Walker Agent notifications

### 2. Update Required: `docker-compose.yml`

Add the following services to your existing `docker-compose.yml`:

```yaml
  # MinIO Object Storage (ADD THIS)
  sankore-minio:
    image: minio/minio:latest
    container_name: sankore-minio
    ports:
      - "9002:9000"   # API
      - "9003:9001"   # Console
    environment:
      - MINIO_ROOT_USER=sankore-minio-key
      - MINIO_ROOT_PASSWORD=sankore-minio-secret-change-in-production
    volumes:
      - minio_data:/data
    networks:
      - sankore-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    command: server /data --console-address ":9001"
    restart: unless-stopped

  # Celery Worker (ADD THIS)
  sankore-celery-worker:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    container_name: sankore-celery-worker
    command: celery -A src.celery_app worker --loglevel=info --concurrency=4 -Q default,ads,trends,analysis
    environment:
      - DATABASE_URL=postgresql+asyncpg://sankore:sankore_password@postgres:5432/sankore_db
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
      - MINIO_ENDPOINT=sankore-minio:9000
      - MINIO_ACCESS_KEY=sankore-minio-key
      - MINIO_SECRET_KEY=sankore-minio-secret-change-in-production
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      sankore-minio:
        condition: service_healthy
    networks:
      - sankore-network
    restart: unless-stopped

  # Celery Beat Scheduler (ADD THIS)
  sankore-celery-beat:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    container_name: sankore-celery-beat
    command: celery -A src.celery_app beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql+asyncpg://sankore:sankore_password@postgres:5432/sankore_db
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - sankore-network
    restart: unless-stopped

  # Flower Monitoring (ADD THIS)
  sankore-flower:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    container_name: sankore-flower
    command: celery -A src.celery_app flower --port=5555
    ports:
      - "5556:5555"
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0
      - FLOWER_BASIC_AUTH=admin:sankore-flower-password
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - sankore-network
    restart: unless-stopped

# Add to volumes section:
volumes:
  postgres_data:
  redis_data:
  minio_data:  # ADD THIS
```

### 3. Update Required: `.env.example`

Add these environment variables:

```bash
# MinIO Object Storage (Bucket Storage)
MINIO_ENDPOINT=sankore-minio:9000
MINIO_ACCESS_KEY=sankore-minio-key
MINIO_SECRET_KEY=sankore-minio-secret-change-in-production

# Celery Configuration
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CELERY_TASK_TRACK_STARTED=true
CELERY_TASK_TIME_LIMIT=1800
CELERY_TASK_SOFT_TIME_LIMIT=1500

# EnGarde Integration (Walker Agent Communication)
ENGARDE_API_URL=https://api.engarde.com
ENGARDE_API_KEY=your-engarde-api-key
ENGARDE_TENANT_UUID=your-tenant-uuid
ENGARDE_API_TIMEOUT=30

# Ad Platform API Keys
GOOGLE_ADS_DEVELOPER_TOKEN=your-token
GOOGLE_ADS_CLIENT_ID=your-client-id
GOOGLE_ADS_CLIENT_SECRET=your-client-secret
GOOGLE_ADS_REFRESH_TOKEN=your-refresh-token

META_APP_ID=your-app-id
META_APP_SECRET=your-app-secret
META_ACCESS_TOKEN=your-access-token

LINKEDIN_CLIENT_ID=your-client-id
LINKEDIN_CLIENT_SECRET=your-client-secret
LINKEDIN_ACCESS_TOKEN=your-access-token

TIKTOK_APP_ID=your-app-id
TIKTOK_APP_SECRET=your-app-secret
TIKTOK_ACCESS_TOKEN=your-access-token
```

### 4. Create: `src/celery_app.py`

```python
"""
Celery application for Sankore async task processing
"""
from celery import Celery
import os

# Initialize Celery
celery_app = Celery(
    'sankore',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes
    task_soft_time_limit=1500,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(['src.services'])
```

### 5. Update: `requirements.txt`

Add these dependencies:

```
celery[redis]==5.3.4
flower==2.0.1
minio==7.2.0
apache-airflow==2.8.0
apache-airflow-providers-celery==3.4.0
```

## Deployment Steps

### Step 1: Backup Current State

```bash
cd /Users/cope/EnGardeHQ/Sankore

# Backup current docker-compose
cp docker-compose.yml docker-compose.yml.backup

# Backup current .env
cp .env .env.backup
```

### Step 2: Update Configuration Files

```bash
# Update docker-compose.yml with new services
# Update .env with MinIO and Celery variables
# Create src/celery_app.py
# Update requirements.txt
```

### Step 3: Rebuild and Deploy

```bash
# Stop existing services
docker-compose down

# Pull new images
docker-compose pull

# Build with new dependencies
docker-compose build --no-cache

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps
```

### Step 4: Verify Lakehouse Components

```bash
# Check MinIO is accessible
curl http://localhost:9003  # MinIO Console

# Check Flower is accessible
curl http://localhost:5556  # Flower Dashboard

# Check Celery workers
docker logs sankore-celery-worker

# Check API still works
curl http://localhost:8001/health
```

### Step 5: Create MinIO Buckets

Access MinIO Console at `http://localhost:9003`:
- Login: `sankore-minio-key` / `sankore-minio-secret-change-in-production`
- Create buckets:
  - `paid-ads-data` (for raw ad platform data)
  - `paid-ads-reports` (for aggregated reports)
  - `paid-ads-recommendations` (for optimization recommendations)
  - `ad-creatives` (for ad creative assets)

### Step 6: Create Database Tables

```sql
-- Ad performance metrics
CREATE TABLE ad_performance_metrics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    campaign_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50) NOT NULL,
    roas DECIMAL(10, 2),
    cpc DECIMAL(10, 2),
    ctr DECIMAL(5, 2),
    efficiency_score DECIMAL(5, 2),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date, campaign_id, platform)
);

CREATE INDEX idx_ad_performance_date ON ad_performance_metrics(date);
CREATE INDEX idx_ad_performance_platform ON ad_performance_metrics(platform);

-- Budget recommendations
CREATE TABLE budget_recommendations (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    campaign_id VARCHAR(255) NOT NULL,
    current_budget DECIMAL(10, 2),
    recommended_budget DECIMAL(10, 2),
    expected_improvement DECIMAL(5, 2),
    rationale TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_budget_recommendations_date ON budget_recommendations(date);
CREATE INDEX idx_budget_recommendations_status ON budget_recommendations(status);

-- Ad creatives
CREATE TABLE ad_creatives (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    campaign_id VARCHAR(255) NOT NULL,
    creative_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50),
    ctr DECIMAL(5, 2),
    conversions INTEGER,
    creative_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(date, creative_id)
);

CREATE INDEX idx_ad_creatives_date ON ad_creatives(date);
CREATE INDEX idx_ad_creatives_campaign ON ad_creatives(campaign_id);
```

## Testing

### Test 1: MinIO Connectivity

```python
from minio import Minio

client = Minio(
    endpoint='localhost:9002',
    access_key='sankore-minio-key',
    secret_key='sankore-minio-secret-change-in-production',
    secure=False
)

# List buckets
buckets = client.list_buckets()
print(buckets)
```

### Test 2: Celery Task

```python
from src.celery_app import celery_app

@celery_app.task
def test_task():
    return "Celery is working!"

# Run task
result = test_task.delay()
print(result.get())
```

### Test 3: Airflow DAG

```bash
# Manually trigger DAG (if Airflow is configured)
# Or test functions individually
cd /Users/cope/EnGardeHQ/Sankore
python dags/paid_ads_walker_dag.py
```

## Monitoring

### Access Points

- **API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **MinIO Console**: http://localhost:9003
- **Flower Dashboard**: http://localhost:5556
- **PostgreSQL**: localhost:5433

### Health Checks

```bash
# API health
curl http://localhost:8001/health

# MinIO health
curl http://localhost:9002/minio/health/live

# Redis health
docker exec sankore-redis redis-cli ping

# PostgreSQL health
docker exec sankore-postgres pg_isready

# Celery workers
docker exec sankore-celery-worker celery -A src.celery_app status
```

## Troubleshooting

### Issue: MinIO won't start

**Solution**: Check port conflicts
```bash
lsof -i :9002
lsof -i :9003
# Kill conflicting processes or change ports
```

### Issue: Celery workers not connecting

**Solution**: Verify Redis connection
```bash
docker exec sankore-celery-worker env | grep CELERY
docker logs sankore-celery-worker
```

### Issue: DAG not executing

**Solution**: Check Airflow configuration
```bash
# Ensure dags/ directory is mounted or accessible
ls -la /Users/cope/EnGardeHQ/Sankore/dags/
```

## Next Steps

1. ✅ DAG created: `paid_ads_walker_dag.py`
2. ⏳ Update `docker-compose.yml` with lakehouse services
3. ⏳ Create `src/celery_app.py`
4. ⏳ Update `requirements.txt`
5. ⏳ Deploy and test lakehouse infrastructure
6. ⏳ Implement ad platform API services
7. ⏳ Connect Walker Agent notification system to En Garde API

## Complete Lakehouse Architecture

Once deployed, Sankore will have:

```
Sankore (Paid Ads Walker Agent)
├── FastAPI (port 8001) ✅
├── PostgreSQL (port 5433) ✅
├── Redis (port 6380) ✅
├── MinIO (ports 9002/9003) ⏳
├── Celery Worker ⏳
├── Celery Beat ⏳
└── Flower (port 5556) ⏳
```

This matches the OnSide lakehouse architecture pattern for consistency across all Walker Agent microservices.
