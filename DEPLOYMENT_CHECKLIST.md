# Sankore Intelligence Layer - Production Deployment Checklist

## Pre-Deployment Checklist

### 1. Code Preparation
- [ ] All code committed to Git repository
- [ ] `.env` file is in `.gitignore` (never commit secrets)
- [ ] `.env.example` is up to date with all required variables
- [ ] All dependencies are in `requirements.txt`
- [ ] Code reviewed and tested locally
- [ ] All tests passing (if tests exist)

### 2. Environment Configuration
- [ ] `DATABASE_URL` configured (Railway auto-generates)
- [ ] `OPENAI_API_KEY` set with valid API key
- [ ] `SECRET_KEY` generated (use cryptographically secure random string)
- [ ] `DEBUG=False` for production
- [ ] `ENVIRONMENT=production` set
- [ ] `ALLOWED_ORIGINS` configured with actual frontend/backend URLs
- [ ] `LOG_LEVEL=INFO` or `WARNING` for production

### 3. Database Setup
- [ ] PostgreSQL database provisioned in Railway
- [ ] Database connection tested
- [ ] Initial schema created (automatic on first run)
- [ ] Consider Alembic migrations for future schema changes

### 4. Railway Configuration
- [ ] `railway.json` present in repository
- [ ] `Procfile` present in repository
- [ ] `.gitignore` configured properly
- [ ] GitHub repository connected to Railway
- [ ] Auto-deploy enabled (optional)

## Deployment Steps

### Step 1: Prepare Repository
```bash
cd /Users/cope/EnGardeHQ/Sankore
git add .
git commit -m "Add production deployment configuration"
git push origin main
```

### Step 2: Create Railway Project
1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your repository
4. Select the `Sankore` directory (if monorepo)

### Step 3: Add PostgreSQL Database
1. In Railway project dashboard
2. Click "New" → "Database" → "PostgreSQL"
3. Wait for provisioning (Railway auto-creates `DATABASE_URL`)

### Step 4: Configure Environment Variables

In Railway project Settings → Variables, add:

```env
OPENAI_API_KEY=sk-your-actual-openai-key
META_API_KEY=your-meta-access-token
TIKTOK_ACCESS_TOKEN=your-tiktok-access-token
SECRET_KEY=generate-a-secure-random-string-here
DEBUG=False
ENVIRONMENT=production
ALLOWED_ORIGINS=https://your-frontend.railway.app,https://engarde-backend.railway.app
LOG_LEVEL=INFO
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Step 5: Deploy
1. Railway automatically detects configuration and deploys
2. Monitor deployment logs in Railway dashboard
3. Wait for "Build successful" and "Deployment live"

### Step 6: Verify Deployment

```bash
# Get your Railway deployment URL
SANKORE_URL=https://your-sankore-url.railway.app

# Test health check
curl $SANKORE_URL/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "Sankore Intelligence Layer",
#   "version": "0.1.0",
#   "environment": "production"
# }

# Test root endpoint
curl $SANKORE_URL/

# Test API documentation (if DEBUG=True)
open $SANKORE_URL/docs
```

### Step 7: Integration with En Garde Platform

1. **Update En Garde Backend** (`/Users/cope/EnGardeHQ/Onside/production-backend`)

   Add to `.env`:
   ```env
   SANKORE_API_URL=https://your-sankore-url.railway.app
   ```

2. **Update Frontend** (if direct integration needed)

   Add to `.env.local`:
   ```env
   NEXT_PUBLIC_SANKORE_API_URL=https://your-sankore-url.railway.app
   ```

3. **Update CORS settings**

   Go back to Railway → Sankore → Variables and update:
   ```env
   ALLOWED_ORIGINS=https://production-frontend.railway.app,https://production-backend.railway.app
   ```

## Post-Deployment Verification

### Functional Testing
- [ ] Health check endpoint responding
- [ ] Root endpoint responding
- [ ] API documentation accessible (if DEBUG=True)
- [ ] Database connection working
- [ ] Trends endpoints responding
- [ ] Analysis endpoints responding
- [ ] CORS working from frontend
- [ ] Error logging visible in Railway logs

### Performance Testing
- [ ] Response times acceptable (<500ms for most endpoints)
- [ ] Database queries optimized
- [ ] No memory leaks (monitor Railway metrics)
- [ ] Worker processes handling load (2 workers configured)

### Security Verification
- [ ] API keys not exposed in logs
- [ ] CORS restricted to specific origins
- [ ] HTTPS enabled (Railway default)
- [ ] No sensitive data in error messages
- [ ] Database credentials secured
- [ ] API documentation disabled in production (or protected)

## Monitoring Setup

### Railway Monitoring
- [ ] Enable Railway metrics dashboard
- [ ] Set up log retention
- [ ] Configure alerting (if available)
- [ ] Monitor resource usage (CPU, memory, database)

### Application Logging
- [ ] Verify logs appearing in Railway dashboard
- [ ] Check log levels appropriate for production
- [ ] Ensure no sensitive data in logs
- [ ] Set up log aggregation (optional)

### Health Checks
```bash
# Create monitoring script
#!/bin/bash
SANKORE_URL=https://your-sankore-url.railway.app

while true; do
  STATUS=$(curl -s $SANKORE_URL/health | jq -r '.status')
  if [ "$STATUS" != "healthy" ]; then
    echo "ALERT: Sankore service unhealthy!"
    # Send alert (email, Slack, etc.)
  fi
  sleep 300  # Check every 5 minutes
done
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check `DATABASE_URL` is set correctly
   - Verify PostgreSQL service is running
   - Check Railway logs for connection errors

2. **Deployment Failed**
   - Check Railway build logs
   - Verify `requirements.txt` has all dependencies
   - Check Python version compatibility
   - Ensure `railway.json` and `Procfile` are correct

3. **CORS Errors**
   - Verify `ALLOWED_ORIGINS` includes exact frontend URL
   - Check for trailing slashes in URLs
   - Ensure protocol (https://) is correct

4. **API Key Errors**
   - Verify OpenAI API key is valid
   - Check API key has sufficient credits
   - Ensure no extra spaces in environment variables

5. **500 Internal Server Errors**
   - Check Railway application logs
   - Verify database migrations ran
   - Check for missing environment variables

### Debug Mode (Emergency Only)

If you need to enable debug mode temporarily:

```bash
# Railway CLI
railway variables set DEBUG=True
railway up

# After debugging, disable immediately:
railway variables set DEBUG=False
```

**WARNING:** Never leave DEBUG=True in production!

## Rollback Procedure

If deployment fails or issues arise:

1. **Via Railway Dashboard:**
   - Go to Deployments
   - Find last working deployment
   - Click "Redeploy"

2. **Via Git:**
   ```bash
   git revert HEAD
   git push origin main
   # Railway auto-deploys previous version
   ```

3. **Via Railway CLI:**
   ```bash
   railway rollback
   ```

## Maintenance

### Regular Tasks
- [ ] Monitor Railway logs weekly
- [ ] Check database size and performance
- [ ] Review and rotate API keys quarterly
- [ ] Update dependencies monthly (test first!)
- [ ] Review and optimize slow queries
- [ ] Monitor costs and resource usage

### Scaling
- [ ] Monitor request rates
- [ ] Increase workers if needed (edit `railway.json`)
- [ ] Consider database connection pooling adjustments
- [ ] Implement caching (Redis) for frequently accessed data

### Backup Strategy
- [ ] Railway PostgreSQL has automatic backups
- [ ] Test restore procedure periodically
- [ ] Export critical data regularly
- [ ] Document recovery procedures

## Success Criteria

Deployment is successful when:

- [ ] Health check returns 200 OK
- [ ] All API endpoints responding correctly
- [ ] Integration with En Garde platform working
- [ ] No errors in Railway logs
- [ ] CORS configured correctly
- [ ] Performance metrics acceptable
- [ ] Security scan passes
- [ ] Documentation updated with deployment URL

## Support Contacts

- **Railway Support:** https://railway.app/help
- **OpenAI Support:** https://platform.openai.com/support
- **Project Repository:** [Your GitHub URL]
- **Team Lead:** [Contact info]

---

**Last Updated:** 2025-12-24
**Version:** 1.0
**Next Review:** After first production deployment
