# Sankore Intelligence Layer - Quick Start Deployment Guide

This guide will get Sankore deployed to Railway in under 10 minutes.

## Prerequisites

- Railway account (sign up at https://railway.app)
- GitHub repository with Sankore code
- OpenAI API key

## Step-by-Step Deployment

### 1. Prepare Environment Variables (5 minutes)

Generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy this value - you'll need it for Railway.

### 2. Deploy to Railway (3 minutes)

**Option A: Via Railway Dashboard (Recommended)**

1. Go to https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Select your repository
4. If monorepo, select the `Sankore` directory
5. Click **"Deploy"**

**Option B: Via Railway CLI**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
cd /Users/cope/EnGardeHQ/Sankore
railway init

# Deploy
railway up
```

### 3. Add PostgreSQL Database (1 minute)

1. In Railway project dashboard
2. Click **"New"** → **"Database"** → **"PostgreSQL"**
3. Wait for provisioning (automatic, takes ~30 seconds)
4. Railway automatically sets `DATABASE_URL` environment variable

### 4. Configure Environment Variables (3 minutes)

In Railway project:
1. Go to **Settings** → **Variables**
2. Click **"New Variable"** and add each:

```env
OPENAI_API_KEY=sk-your-actual-openai-api-key
SECRET_KEY=paste-the-generated-secret-from-step-1
DEBUG=False
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-frontend.railway.app,https://your-backend.railway.app
LOG_LEVEL=INFO
```

**Optional (for trend features):**
```env
META_API_KEY=your-meta-access-token
TIKTOK_ACCESS_TOKEN=your-tiktok-access-token
```

3. Click **"Save"** - Railway automatically redeploys

### 5. Verify Deployment (2 minutes)

Get your deployment URL from Railway dashboard (looks like: `https://sankore-production.up.railway.app`)

Test it:

```bash
# Replace with your actual URL
SANKORE_URL=https://your-deployment.railway.app

# Quick test
curl $SANKORE_URL/health

# Should return:
# {
#   "status": "healthy",
#   "service": "Sankore Intelligence Layer",
#   "version": "0.1.0",
#   "environment": "production"
# }
```

**Or use the verification script:**

```bash
cd /Users/cope/EnGardeHQ/Sankore
./scripts/verify_deployment.sh https://your-deployment.railway.app
```

### 6. Integrate with En Garde Platform (2 minutes)

**Update En Garde Backend:**

1. Go to your En Garde backend project in Railway
2. Add environment variable:
   ```env
   SANKORE_API_URL=https://your-sankore-deployment.railway.app
   ```

**Update Sankore CORS:**

1. Go back to Sankore project in Railway
2. Update `ALLOWED_ORIGINS` variable with your actual URLs:
   ```env
   ALLOWED_ORIGINS=https://production-frontend.railway.app,https://production-backend.railway.app
   ```

## Done!

Your Sankore Intelligence Layer is now deployed and ready to use.

## Test Integration

From your En Garde backend, test the integration:

```python
import httpx

async def test_sankore():
    sankore_url = os.getenv("SANKORE_API_URL")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{sankore_url}/health")
        print(response.json())

# Should print: {'status': 'healthy', ...}
```

## Common Issues & Solutions

### Issue: Deployment Failed

**Solution:**
- Check Railway build logs for specific error
- Verify `requirements.txt` includes all dependencies
- Ensure `railway.json` and `Procfile` are present

### Issue: Database Connection Error

**Solution:**
- Verify PostgreSQL service is running in Railway
- Check `DATABASE_URL` is automatically set
- Wait 1-2 minutes after database provisioning

### Issue: CORS Errors from Frontend

**Solution:**
- Update `ALLOWED_ORIGINS` to include exact frontend URL
- No trailing slashes
- Include protocol (https://)
- Redeploy after changing variables

### Issue: OpenAI API Errors

**Solution:**
- Verify API key is correct (no spaces)
- Check API key has credits
- Test key at https://platform.openai.com/playground

## Monitoring

**View Logs:**
- Railway Dashboard → Your Sankore Project → Logs

**Monitor Health:**
```bash
# Create a simple monitoring script
while true; do
  curl -s https://your-sankore-url.railway.app/health | jq
  sleep 60
done
```

**Railway Metrics:**
- Dashboard shows CPU, Memory, Network usage
- Set up alerts if available in your plan

## Scaling

If you need more performance:

1. **Increase Workers:**
   Edit `/Users/cope/EnGardeHQ/Sankore/railway.json`:
   ```json
   "startCommand": "uvicorn src.main:app --host 0.0.0.0 --port $PORT --workers 4"
   ```

2. **Upgrade Database:**
   Railway → PostgreSQL service → Settings → Scale

3. **Add Redis Caching:**
   Railway → New → Database → Redis

## Cost Estimates

**Railway Free Tier:**
- $5 free credits per month
- Suitable for development/testing

**Production Estimate:**
- Web Service: ~$5-10/month
- PostgreSQL: ~$5-10/month
- Total: ~$10-20/month

**Actual costs depend on:**
- Request volume
- Database size
- Worker count
- Region

## Next Steps

1. **Set up monitoring** - See full README.md
2. **Configure Alembic** - For database migrations
3. **Add Redis caching** - For trend data
4. **Implement rate limiting** - For production security
5. **Set up CI/CD** - Automated testing before deploy

## Support

- **Full Documentation:** `/Users/cope/EnGardeHQ/Sankore/README.md`
- **Deployment Checklist:** `/Users/cope/EnGardeHQ/Sankore/DEPLOYMENT_CHECKLIST.md`
- **Railway Docs:** https://docs.railway.app
- **Railway Support:** https://railway.app/help

---

**Deployment Time:** ~15 minutes total
**Difficulty:** Easy
**Status:** Production Ready
