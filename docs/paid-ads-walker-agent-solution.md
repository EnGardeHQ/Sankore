# Sankore: Paid Ads Walker Agent Solution

## Executive Summary

Sankore is En Garde's intelligent paid advertising optimization microservice, powered by a Walker Agent that autonomously monitors, analyzes, and optimizes multi-platform advertising campaigns. The system provides real-time ROAS tracking, budget optimization recommendations, creative performance analysis, and trend alignment insights across Google Ads, Meta (Facebook/Instagram), LinkedIn, and TikTok advertising platforms.

## Problem Statement

### Current Challenges in Paid Advertising

1. **Multi-Platform Complexity**: Managing campaigns across Google Ads, Meta, LinkedIn, and TikTok requires constant context-switching and platform-specific expertise
2. **Budget Inefficiency**: Without real-time optimization, ad spend is often allocated to underperforming campaigns
3. **Creative Fatigue**: Ad creatives lose effectiveness over time, but identifying when to refresh is manual and reactive
4. **Delayed Insights**: Platform dashboards provide lagging indicators, missing optimization opportunities
5. **Trend Misalignment**: Campaigns often fail to capitalize on emerging trends and viral content opportunities

### Business Impact

- **Wasted Ad Spend**: 30-40% of ad budgets typically go to underperforming campaigns
- **Missed Opportunities**: Delayed optimization means lost conversions and revenue
- **Resource Intensive**: Marketing teams spend 60%+ of time on manual campaign monitoring
- **Inconsistent Performance**: Without unified visibility, campaign performance varies wildly across platforms

## Solution Overview

### Sankore Paid Ads Walker Agent

An autonomous AI agent that:

1. **Monitors** all paid advertising campaigns across platforms 24/7
2. **Analyzes** performance metrics, budget efficiency, and creative effectiveness
3. **Optimizes** budget allocation based on real-time ROAS calculations
4. **Recommends** creative refreshes, audience targeting adjustments, and campaign strategy changes
5. **Aligns** campaigns with trending content and viral opportunities
6. **Notifies** marketing teams via email, WhatsApp, and in-platform chat with actionable insights

### Key Capabilities

#### Multi-Platform Data Ingestion
- **Google Ads API Integration**: Campaign metrics, keyword performance, conversion tracking
- **Meta Ads API Integration**: Ad set performance, audience insights, creative metrics
- **LinkedIn Ads API Integration**: Sponsored content, InMail campaigns, lead gen forms
- **TikTok Ads API Integration**: Video ad performance, trending sounds, audience engagement

#### Intelligent Analysis
- **ROAS Calculation**: Real-time return on ad spend across all platforms
- **Budget Optimization**: ML-powered recommendations for budget reallocation
- **Creative Performance Scoring**: Identifies top-performing ad creatives and fatigue patterns
- **Trend Alignment Analysis**: Matches campaign themes with trending topics and viral content
- **Competitive Intelligence**: Benchmarks performance against industry standards

#### Proactive Notifications
- **Campaign Suggestions**: Daily personalized recommendations via email, WhatsApp, and chat
- **Alert System**: Immediate notifications for underperforming campaigns or budget overspend
- **Opportunity Identification**: Alerts for trending topics to capitalize on
- **Performance Reports**: Automated weekly/monthly summaries with actionable insights

## Architecture

### Technology Stack

```
┌─────────────────────────────────────────────────────────────┐
│                     Sankore Microservice                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  FastAPI     │  │  Celery      │  │  Airflow     │      │
│  │  Application │  │  Workers     │  │  DAGs        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Paid Ads Walker Agent Engine               │   │
│  │  - Multi-platform data ingestion                     │   │
│  │  - ROAS calculation & optimization                   │   │
│  │  - Creative performance analysis                     │   │
│  │  - Trend alignment scoring                           │   │
│  │  - Budget recommendation engine                      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  PostgreSQL  │  │  MinIO       │  │  Redis       │      │
│  │  Lakehouse   │  │  Storage     │  │  Cache       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Walker Agent Notifications
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              En Garde Production Backend API                 │
│  - Campaign suggestion endpoint                              │
│  - Walker Agent webhook receiver                             │
│  - Multi-channel notification dispatcher                     │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │    Email     │  │   WhatsApp   │  │  In-Platform │
    │   (Brevo)    │  │   (Twilio)   │  │     Chat     │
    └──────────────┘  └──────────────┘  └──────────────┘
```

### Core Components

#### 1. Ad Platform Connectors
**Location**: `src/services/ad_platforms/`

- **Google Ads Service** (`google_ads.py`)
  - Campaign data extraction
  - Conversion tracking
  - Keyword performance metrics

- **Meta Ads Service** (`meta_ads.py`)
  - Ad set and creative performance
  - Audience insights
  - Placement optimization data

- **LinkedIn Ads Service** (`linkedin_ads.py`)
  - Sponsored content metrics
  - Lead generation performance
  - Audience targeting data

- **TikTok Ads Service** (`tiktok_ads.py`)
  - Video ad performance
  - Trending sound alignment
  - Hashtag performance

#### 2. Walker Agent Pipeline
**Location**: `dags/paid_ads_walker_dag.py`

Daily execution at 6 AM:

1. **Data Ingestion Phase** (Parallel)
   - Fetch Google Ads data → Store in MinIO
   - Fetch Meta Ads data → Store in MinIO
   - Fetch LinkedIn Ads data → Store in MinIO
   - Fetch TikTok Ads data → Store in MinIO

2. **Analysis Phase**
   - Calculate platform-specific ROAS
   - Aggregate cross-platform metrics
   - Identify optimization opportunities

3. **Optimization Phase** (Parallel)
   - Budget reallocation recommendations
   - Creative performance scoring
   - Trend alignment analysis
   - Competitive benchmarking

4. **Notification Phase**
   - Generate campaign suggestions
   - Send to En Garde API
   - Dispatch via email, WhatsApp, chat

#### 3. Data Lakehouse
**PostgreSQL Schema**: `sankore_analytics`

```sql
-- Campaign Performance Table
CREATE TABLE campaign_performance (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    campaign_id VARCHAR(255) NOT NULL,
    campaign_name VARCHAR(500),
    date DATE NOT NULL,
    impressions BIGINT,
    clicks BIGINT,
    conversions INTEGER,
    spend DECIMAL(12,2),
    revenue DECIMAL(12,2),
    roas DECIMAL(8,2),
    ctr DECIMAL(5,2),
    cpc DECIMAL(8,2),
    cpa DECIMAL(8,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform, campaign_id, date)
);

-- Creative Performance Table
CREATE TABLE creative_performance (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    creative_id VARCHAR(255) NOT NULL,
    creative_type VARCHAR(50),
    creative_url TEXT,
    campaign_id VARCHAR(255),
    date DATE NOT NULL,
    impressions BIGINT,
    clicks BIGINT,
    conversions INTEGER,
    engagement_rate DECIMAL(5,2),
    performance_score DECIMAL(5,2),
    fatigue_index DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform, creative_id, date)
);

-- Budget Recommendations Table
CREATE TABLE budget_recommendations (
    id SERIAL PRIMARY KEY,
    recommendation_date DATE NOT NULL,
    platform VARCHAR(50) NOT NULL,
    campaign_id VARCHAR(255) NOT NULL,
    current_budget DECIMAL(12,2),
    recommended_budget DECIMAL(12,2),
    expected_roas DECIMAL(8,2),
    confidence_score DECIMAL(5,2),
    reason TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    applied_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trend Alignment Table
CREATE TABLE trend_alignment (
    id SERIAL PRIMARY KEY,
    analysis_date DATE NOT NULL,
    trend_topic VARCHAR(500) NOT NULL,
    trend_score DECIMAL(5,2),
    campaign_id VARCHAR(255),
    alignment_score DECIMAL(5,2),
    recommendation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**MinIO Bucket Structure**:
```
sankore-ads-data/
├── google-ads/
│   ├── YYYYMMDD/
│   │   ├── campaigns.json
│   │   ├── ad-groups.json
│   │   └── keywords.json
├── meta-ads/
│   ├── YYYYMMDD/
│   │   ├── campaigns.json
│   │   ├── ad-sets.json
│   │   └── creatives.json
├── linkedin-ads/
│   ├── YYYYMMDD/
│   │   ├── campaigns.json
│   │   └── sponsored-content.json
└── tiktok-ads/
    ├── YYYYMMDD/
    │   ├── campaigns.json
    │   ├── ad-groups.json
    │   └── creatives.json
```

## Walker Agent Features

### 1. Real-Time ROAS Optimization

**How it works**:
1. Pulls spend and revenue data from all platforms every 6 hours
2. Calculates ROAS for each campaign, ad set, and creative
3. Identifies campaigns with ROAS below target threshold
4. Generates budget reallocation recommendations
5. Sends actionable alerts to marketing team

**Example Notification** (Email/WhatsApp/Chat):
```
🎯 Paid Ads Walker Agent Alert

Campaign Performance Update:

⚠️ Underperforming:
- Google Ads "Summer Sale 2024": ROAS 1.2x (Target: 3x)
  Recommendation: Reduce budget by $500/day, reallocate to top performers

✅ Top Performers:
- Meta Ads "Product Launch": ROAS 5.8x
  Recommendation: Increase budget by $300/day for max impact

- TikTok Ads "Viral Challenge": ROAS 4.2x
  Recommendation: Maintain current spend, refresh creative in 5 days

Total Potential Savings: $2,400/week
Expected Revenue Increase: $8,500/week

👉 View detailed recommendations: [Dashboard Link]
```

### 2. Creative Fatigue Detection

**Algorithm**:
1. Tracks creative performance over 7, 14, and 30-day windows
2. Calculates engagement decline rate
3. Identifies creatives showing >15% performance drop
4. Recommends refresh timeline based on platform benchmarks

**Fatigue Index Calculation**:
```python
fatigue_index = (
    (recent_7d_engagement - historical_avg_engagement) / historical_avg_engagement
) * -1

if fatigue_index > 0.15:
    status = "HIGH_FATIGUE"
    recommendation = "Refresh creative immediately"
elif fatigue_index > 0.10:
    status = "MEDIUM_FATIGUE"
    recommendation = "Plan creative refresh within 3 days"
```

### 3. Trend Alignment Analysis

**Data Sources**:
- Google Trends API
- Twitter Trending Topics
- TikTok Discover Feed
- Reddit Hot Topics
- Industry news aggregators

**Process**:
1. Identifies trending topics relevant to business vertical
2. Analyzes current campaign themes and messaging
3. Calculates alignment score (0-100)
4. Suggests campaign adjustments to capitalize on trends

**Example Alert**:
```
🔥 Trend Opportunity Detected

Trending Topic: "Sustainable Fashion Week"
Trend Score: 92/100
Peak Window: Next 3-5 days

Your Campaigns:
❌ "Eco-Friendly Collection" - Alignment: 45/100
   Current: Generic sustainability messaging
   Recommendation: Update ad copy to reference Fashion Week,
   use hashtag #SustainableFashionWeek

Estimated Impact: +40% engagement, +25% conversions
Quick Action Templates: [View Creative Suggestions]
```

### 4. Budget Optimization Engine

**ML Model**: Gradient Boosting Regressor trained on:
- Historical campaign performance data
- Seasonal trends
- Day-of-week patterns
- Platform-specific benchmarks
- Competitive spend levels

**Output**:
- Daily budget recommendations per campaign
- Expected ROAS for each recommendation
- Confidence score (0-100%)
- Risk assessment

**Optimization Strategies**:
1. **Aggressive Growth**: Maximize conversions, accept lower ROAS
2. **Balanced**: Optimize for target ROAS with growth
3. **Conservative**: Maintain ROAS floor, limit spend variance

### 5. Competitive Intelligence

**Data Collection**:
- Ad library scraping (Meta, LinkedIn, TikTok)
- Estimated competitor spend analysis
- Creative strategy pattern recognition
- Audience targeting insights

**Deliverables**:
- Weekly competitive landscape report
- Share-of-voice analysis
- Creative gap identification
- Opportunity recommendations

## Campaign Suggestion System

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Sankore Walker Agent (Suggestion Engine)         │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │ POST /walker-agent/suggestions
                      │ {
                      │   "agent_type": "paid_ads",
                      │   "suggestions": [...],
                      │   "priority": "high",
                      │   "tenant_id": "uuid"
                      │ }
                      ▼
┌─────────────────────────────────────────────────────────┐
│     En Garde Production Backend - Walker Agent API      │
│                                                          │
│  POST /api/v1/walker-agents/campaign-suggestions        │
│  - Validates Walker Agent request                        │
│  - Stores suggestion in database                        │
│  - Triggers multi-channel notification                  │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬─────────────┐
        ▼             ▼             ▼             ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │  Email   │  │ WhatsApp │  │   Chat   │  │   Push   │
  │ Service  │  │ Service  │  │ Service  │  │ Notif.   │
  └──────────┘  └──────────┘  └──────────┘  └──────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                      │
                      ▼
              ┌────────────────┐
              │  End User      │
              │  - Email inbox │
              │  - WhatsApp    │
              │  - Platform UI │
              └────────────────┘
```

### Suggestion Payload Format

```json
{
  "agent_type": "paid_ads",
  "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2025-12-28T06:00:00Z",
  "priority": "high",
  "suggestions": [
    {
      "id": "sg_12345",
      "type": "budget_optimization",
      "title": "Reallocate Budget to High-ROAS Campaigns",
      "description": "Your Meta Ads 'Product Launch' campaign is achieving 5.8x ROAS. Consider increasing daily budget by $300.",
      "impact": {
        "estimated_revenue_increase": 8500,
        "estimated_cost_savings": 2400,
        "confidence_score": 0.89
      },
      "actions": [
        {
          "action_type": "increase_budget",
          "platform": "meta",
          "campaign_id": "23849394830",
          "current_value": 1000,
          "recommended_value": 1300,
          "unit": "USD/day"
        },
        {
          "action_type": "decrease_budget",
          "platform": "google",
          "campaign_id": "98765432",
          "current_value": 1500,
          "recommended_value": 1000,
          "unit": "USD/day"
        }
      ],
      "cta_url": "https://app.engarde.media/campaigns/budget-optimizer?suggestion=sg_12345"
    },
    {
      "id": "sg_12346",
      "type": "creative_refresh",
      "title": "Update TikTok Ad Creative - Performance Declining",
      "description": "Your 'Viral Challenge' ad creative shows 18% engagement drop over past 7 days. Refresh recommended.",
      "impact": {
        "estimated_engagement_increase": 0.40,
        "confidence_score": 0.76
      },
      "actions": [
        {
          "action_type": "refresh_creative",
          "platform": "tiktok",
          "creative_id": "cr_98765",
          "fatigue_index": 0.18,
          "recommended_timeline": "immediate"
        }
      ],
      "creative_suggestions": [
        {
          "template": "trending_sound_overlay",
          "description": "Use trending sound 'Summer Vibes Mix' (viral score: 94/100)",
          "preview_url": "https://cdn.engarde.media/creative-templates/ts_001.mp4"
        }
      ],
      "cta_url": "https://app.engarde.media/creatives/refresh?suggestion=sg_12346"
    },
    {
      "id": "sg_12347",
      "type": "trend_opportunity",
      "title": "Capitalize on 'Sustainable Fashion Week' Trend",
      "description": "High relevance trend detected. Update messaging to align with trending topic for +25% conversion boost.",
      "impact": {
        "estimated_conversion_increase": 0.25,
        "trend_peak_window": "3-5 days",
        "confidence_score": 0.82
      },
      "actions": [
        {
          "action_type": "update_messaging",
          "platform": "meta",
          "campaign_id": "23849394831",
          "current_theme": "Eco-Friendly Collection",
          "recommended_theme": "Sustainable Fashion Week Exclusive",
          "hashtag_recommendations": ["#SustainableFashionWeek", "#EcoFashion2025"]
        }
      ],
      "copy_templates": [
        {
          "headline": "Join Sustainable Fashion Week with Our Eco Collection",
          "body": "Exclusive designs for conscious consumers. Limited time offer.",
          "cta": "Shop the Collection"
        }
      ],
      "cta_url": "https://app.engarde.media/campaigns/trend-optimizer?suggestion=sg_12347"
    }
  ],
  "summary": {
    "total_suggestions": 3,
    "high_priority": 2,
    "medium_priority": 1,
    "total_estimated_impact": {
      "revenue_increase": 8500,
      "cost_savings": 2400,
      "engagement_increase": 0.40
    }
  }
}
```

### Notification Templates

#### Email Template
**Subject**: `🎯 3 Paid Ads Opportunities from Your Walker Agent`

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        .suggestion-card {
            border-left: 4px solid #4CAF50;
            padding: 16px;
            margin: 16px 0;
            background: #f9f9f9;
        }
        .high-priority { border-left-color: #f44336; }
        .impact-metric {
            display: inline-block;
            margin: 8px 12px 8px 0;
            color: #2196F3;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <h2>Your Daily Paid Ads Insights</h2>
    <p>Hi there! Your Walker Agent has analyzed your campaigns and found 3 opportunities:</p>

    <div class="suggestion-card high-priority">
        <h3>🚀 Reallocate Budget to High-ROAS Campaigns</h3>
        <p>Your Meta Ads 'Product Launch' campaign is achieving 5.8x ROAS. Consider increasing daily budget by $300.</p>

        <div class="impact">
            <span class="impact-metric">💰 +$8,500 revenue/week</span>
            <span class="impact-metric">💡 89% confidence</span>
        </div>

        <p><strong>Quick Actions:</strong></p>
        <ul>
            <li>Increase Meta 'Product Launch' budget: $1,000 → $1,300/day</li>
            <li>Decrease Google 'Summer Sale' budget: $1,500 → $1,000/day</li>
        </ul>

        <a href="https://app.engarde.media/campaigns/budget-optimizer?suggestion=sg_12345"
           style="display:inline-block; padding:12px 24px; background:#4CAF50; color:white; text-decoration:none; border-radius:4px;">
            Optimize Budget
        </a>
    </div>

    <div class="suggestion-card high-priority">
        <h3>🎨 Update TikTok Ad Creative - Performance Declining</h3>
        <p>Your 'Viral Challenge' ad creative shows 18% engagement drop over past 7 days.</p>

        <div class="impact">
            <span class="impact-metric">📈 +40% engagement potential</span>
            <span class="impact-metric">💡 76% confidence</span>
        </div>

        <p><strong>Recommendation:</strong> Use trending sound "Summer Vibes Mix" (viral score: 94/100)</p>

        <a href="https://app.engarde.media/creatives/refresh?suggestion=sg_12346">
            View Creative Templates
        </a>
    </div>

    <div class="suggestion-card">
        <h3>🔥 Capitalize on 'Sustainable Fashion Week' Trend</h3>
        <p>High relevance trend detected. Peak window: next 3-5 days.</p>

        <div class="impact">
            <span class="impact-metric">🎯 +25% conversions</span>
            <span class="impact-metric">💡 82% confidence</span>
        </div>

        <p><strong>Suggested Messaging:</strong> "Join Sustainable Fashion Week with Our Eco Collection"</p>

        <a href="https://app.engarde.media/campaigns/trend-optimizer?suggestion=sg_12347">
            Update Campaign
        </a>
    </div>

    <hr>
    <p><strong>Summary:</strong> 3 opportunities with potential for +$8,500 revenue/week</p>
    <p><a href="https://app.engarde.media/walker-agents/paid-ads">View Full Dashboard</a></p>
</body>
</html>
```

#### WhatsApp Template

```
🎯 *Paid Ads Walker Agent - Daily Brief*

Hi! Found 3 opportunities in your campaigns:

━━━━━━━━━━━━━━━━

🚀 *HIGH PRIORITY*
*Reallocate Budget to High-ROAS Campaigns*

Meta 'Product Launch': 5.8x ROAS
💰 Potential: +$8.5K revenue/week

*Quick Action:*
• ⬆️ Meta budget: $1K → $1.3K/day
• ⬇️ Google budget: $1.5K → $1K/day

👉 Optimize: engarde.media/budget-sg12345

━━━━━━━━━━━━━━━━

🎨 *HIGH PRIORITY*
*TikTok Creative Needs Refresh*

'Viral Challenge' engagement ⬇️ 18%
📈 Potential: +40% engagement

*Recommended:* Use trending sound "Summer Vibes Mix"

👉 Refresh: engarde.media/creative-sg12346

━━━━━━━━━━━━━━━━

🔥 *Trend Opportunity*
*Sustainable Fashion Week*

Peak window: 3-5 days
🎯 Potential: +25% conversions

👉 Update: engarde.media/trend-sg12347

━━━━━━━━━━━━━━━━

*Total Impact:* +$8.5K revenue, +40% engagement

View dashboard: engarde.media/walker-agents
```

#### In-Platform Chat Widget

```javascript
// Chat notification payload
{
  "notification_type": "walker_agent_suggestion",
  "agent": "paid_ads",
  "message": {
    "type": "interactive_card",
    "content": {
      "header": {
        "icon": "🎯",
        "title": "Paid Ads Walker Agent",
        "subtitle": "3 new opportunities detected"
      },
      "summary": {
        "total_impact": "+$8,500 revenue/week",
        "priority_level": "high",
        "suggestions_count": 3
      },
      "quick_actions": [
        {
          "label": "Optimize Budget",
          "action": "open_suggestion",
          "suggestion_id": "sg_12345",
          "badge": "🚀 High Impact"
        },
        {
          "label": "Refresh Creative",
          "action": "open_suggestion",
          "suggestion_id": "sg_12346",
          "badge": "⚠️ Urgent"
        },
        {
          "label": "View All",
          "action": "open_dashboard",
          "url": "/walker-agents/paid-ads"
        }
      ],
      "preview_suggestions": [
        {
          "id": "sg_12345",
          "title": "Reallocate Budget to High-ROAS Campaigns",
          "impact": "$8.5K revenue/week",
          "confidence": "89%"
        },
        {
          "id": "sg_12346",
          "title": "Update TikTok Creative",
          "impact": "+40% engagement",
          "confidence": "76%"
        }
      ]
    }
  },
  "timestamp": "2025-12-28T06:00:00Z",
  "read": false,
  "actions_available": true
}
```

## Implementation Guide

### Prerequisites

1. **Ad Platform API Access**
   - Google Ads Developer Token
   - Meta Business Manager Admin Access
   - LinkedIn Campaign Manager API credentials
   - TikTok Ads Manager API access

2. **Infrastructure**
   - PostgreSQL 15+ database
   - MinIO or S3-compatible object storage
   - Redis 6+ for caching and Celery
   - Docker and Docker Compose

3. **En Garde Integration**
   - Walker Agent API endpoint configured
   - Notification service credentials (Brevo, Twilio)
   - Webhook authentication tokens

### Setup Steps

#### 1. Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit with your credentials
nano .env
```

**Required Variables**:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5433/sankore

# Redis & Celery
CELERY_BROKER_URL=redis://localhost:6380/0
CELERY_RESULT_BACKEND=redis://localhost:6380/0

# MinIO
MINIO_ENDPOINT=localhost:9002
MINIO_ACCESS_KEY=sankore-minio-key
MINIO_SECRET_KEY=your-secure-secret-key

# Google Ads API
GOOGLE_ADS_DEVELOPER_TOKEN=your-developer-token
GOOGLE_ADS_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_ADS_CLIENT_SECRET=your-client-secret
GOOGLE_ADS_REFRESH_TOKEN=your-refresh-token

# Meta Ads API
META_APP_ID=your-app-id
META_APP_SECRET=your-app-secret
META_ACCESS_TOKEN=your-long-lived-access-token

# LinkedIn Ads API
LINKEDIN_CLIENT_ID=your-client-id
LINKEDIN_CLIENT_SECRET=your-client-secret
LINKEDIN_ACCESS_TOKEN=your-access-token

# TikTok Ads API
TIKTOK_APP_ID=your-app-id
TIKTOK_APP_SECRET=your-app-secret
TIKTOK_ACCESS_TOKEN=your-access-token

# En Garde Integration
ENGARDE_API_URL=https://api.engarde.media
ENGARDE_API_KEY=your-walker-agent-api-key
ENGARDE_WEBHOOK_SECRET=your-webhook-secret
```

#### 2. Deploy with Docker Compose

```bash
# Build containers
docker-compose build --no-cache

# Start all services
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs
docker-compose logs -f sankore-api
docker-compose logs -f sankore-celery-worker
```

#### 3. Initialize Database

```bash
# Run migrations
docker exec sankore-api alembic upgrade head

# Verify tables created
docker exec sankore-db psql -U postgres -d sankore -c "\dt"
```

#### 4. Configure MinIO Buckets

```bash
# Access MinIO console at http://localhost:9003
# Login with credentials from .env

# Create bucket via CLI
docker exec sankore-minio mc mb minio/sankore-ads-data
docker exec sankore-minio mc policy set download minio/sankore-ads-data
```

#### 5. Configure Airflow DAGs

```bash
# Copy DAG to Airflow DAGs directory
# DAG is already in dags/paid_ads_walker_dag.py

# Verify DAG is loaded (access Airflow UI at configured port)
# Enable the paid_ads_walker_agent_pipeline DAG

# Trigger test run
docker exec sankore-airflow-scheduler airflow dags test paid_ads_walker_agent_pipeline 2025-12-28
```

#### 6. Test Walker Agent Integration

```bash
# Test suggestion endpoint
curl -X POST http://localhost:8001/api/v1/walker-agent/test-suggestion \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${ENGARDE_API_KEY}" \
  -d '{
    "type": "budget_optimization",
    "test_mode": true
  }'

# Verify notification sent
# Check email inbox, WhatsApp, and platform chat
```

### Monitoring & Maintenance

#### Health Checks

```bash
# API health
curl http://localhost:8001/health

# Celery workers
docker exec sankore-flower curl http://localhost:5556/api/workers

# Database connections
docker exec sankore-db psql -U postgres -d sankore -c "SELECT count(*) FROM pg_stat_activity;"

# MinIO storage
docker exec sankore-minio mc du minio/sankore-ads-data
```

#### Performance Metrics

Key metrics to monitor:
- **API Response Time**: < 200ms for 95th percentile
- **DAG Execution Time**: < 15 minutes for daily pipeline
- **ROAS Calculation Accuracy**: ±2% of platform reporting
- **Notification Delivery Rate**: > 99%
- **Data Freshness**: < 6 hours lag from ad platforms

#### Scaling Considerations

**When to scale**:
- Processing > 100 campaigns per platform
- > 10,000 ad creatives tracked
- > 100 GB daily data ingestion

**Scaling strategies**:
1. **Horizontal Celery Workers**: Add more worker containers
   ```bash
   docker-compose up -d --scale sankore-celery-worker=4
   ```

2. **Database Read Replicas**: For analytics queries

3. **MinIO Distributed Mode**: For > 1TB storage

4. **Redis Cluster**: For > 10GB cache data

## ROI & Business Impact

### Expected Outcomes

**Month 1**:
- 15-20% reduction in wasted ad spend
- 10-15% improvement in overall ROAS
- 30% reduction in manual campaign monitoring time

**Month 3**:
- 25-35% reduction in wasted ad spend
- 20-30% improvement in overall ROAS
- 60% reduction in manual campaign monitoring time
- 40% faster response to trend opportunities

**Month 6**:
- 35-45% reduction in wasted ad spend
- 30-40% improvement in overall ROAS
- 80% reduction in manual campaign monitoring time
- 3x faster creative refresh cycles

### Success Metrics

**Performance KPIs**:
- **Blended ROAS**: Target 4.0x (from typical 2.5x)
- **Budget Efficiency**: < 10% spend on underperforming campaigns
- **Creative Refresh Rate**: Every 14 days (from 30-45 days)
- **Trend Capitalization**: Participate in 80% of relevant trends

**Operational KPIs**:
- **Time to Optimization**: < 4 hours from alert to action
- **Alert Accuracy**: > 85% of suggestions implemented
- **Notification Engagement**: > 60% open rate for emails
- **Platform Adoption**: > 70% weekly active usage

## Support & Troubleshooting

### Common Issues

**1. Ad Platform API Rate Limits**
- **Symptom**: Data ingestion fails with 429 errors
- **Solution**: Implement exponential backoff, adjust DAG schedule to spread requests

**2. ROAS Calculation Mismatches**
- **Symptom**: Walker Agent ROAS differs from platform reporting
- **Solution**: Verify attribution window settings, check conversion tracking implementation

**3. Notification Delivery Failures**
- **Symptom**: Users not receiving campaign suggestions
- **Solution**: Check En Garde API connectivity, verify Brevo/Twilio credentials

**4. MinIO Storage Full**
- **Symptom**: Data ingestion fails with storage errors
- **Solution**: Implement data retention policy, archive old data to cold storage

### Getting Help

- **Documentation**: https://docs.engarde.media/sankore
- **API Reference**: https://api.engarde.media/docs#walker-agents
- **Community**: https://community.engarde.media
- **Support**: walker-agents@engarde.media

## Conclusion

Sankore's Paid Ads Walker Agent transforms paid advertising from a reactive, manual process into a proactive, AI-powered optimization engine. By continuously monitoring multi-platform campaigns, identifying optimization opportunities, and delivering actionable insights via email, WhatsApp, and in-platform chat, Sankore empowers marketing teams to maximize ROAS while minimizing wasted spend.

The system's intelligent budget allocation, creative fatigue detection, and trend alignment capabilities ensure campaigns stay relevant and high-performing in today's fast-paced digital advertising landscape.

**Next Steps**:
1. Complete ad platform API setup
2. Deploy Sankore microservice
3. Configure Walker Agent notification preferences
4. Monitor first week of suggestions
5. Iterate on recommendation thresholds based on team feedback

---

**Document Version**: 1.0
**Last Updated**: December 28, 2025
**Maintained By**: En Garde Engineering Team
