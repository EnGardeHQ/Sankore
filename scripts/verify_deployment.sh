#!/bin/bash

# Sankore Intelligence Layer - Deployment Verification Script
# Usage: ./scripts/verify_deployment.sh <DEPLOYMENT_URL>

set -e

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if URL provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: Deployment URL required${NC}"
    echo "Usage: $0 <DEPLOYMENT_URL>"
    echo "Example: $0 https://sankore-production.up.railway.app"
    exit 1
fi

DEPLOYMENT_URL=$1

echo "=========================================="
echo "Sankore Deployment Verification"
echo "=========================================="
echo "Testing URL: $DEPLOYMENT_URL"
echo ""

# Function to test endpoint
test_endpoint() {
    local endpoint=$1
    local expected_status=$2
    local description=$3

    echo -n "Testing $description... "

    response=$(curl -s -w "\n%{http_code}" "$DEPLOYMENT_URL$endpoint")
    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$status_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $status_code)"
        if [ -n "$body" ]; then
            echo "  Response: $(echo $body | jq -c '.' 2>/dev/null || echo $body)"
        fi
        return 0
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $status_code, expected $expected_status)"
        echo "  Response: $body"
        return 1
    fi
}

# Track failures
failures=0

# Test 1: Health Check
test_endpoint "/health" 200 "Health Check Endpoint" || ((failures++))
echo ""

# Test 2: Root Endpoint
test_endpoint "/" 200 "Root Endpoint" || ((failures++))
echo ""

# Test 3: API Endpoints (expect 200 or 422 for validation)
echo "Testing API endpoints..."

# Trends endpoints (may return empty data or errors if API keys not configured)
test_endpoint "/api/v1/trends/meta" 200 "Meta Trends Endpoint (no params)" || echo -e "  ${YELLOW}Note: May fail if META_API_KEY not configured${NC}"
echo ""

test_endpoint "/api/v1/trends/tiktok" 200 "TikTok Trends Endpoint (no params)" || echo -e "  ${YELLOW}Note: May fail if TIKTOK_ACCESS_TOKEN not configured${NC}"
echo ""

# Test 4: CORS Headers
echo -n "Testing CORS configuration... "
cors_response=$(curl -s -I -H "Origin: https://example.com" "$DEPLOYMENT_URL/health")
if echo "$cors_response" | grep -q "access-control-allow-origin"; then
    echo -e "${GREEN}✓ PASS${NC}"
    echo "  CORS headers present"
else
    echo -e "${YELLOW}⚠ WARNING${NC}"
    echo "  CORS headers not found (may be intended for production)"
    ((failures++))
fi
echo ""

# Test 5: Check Environment
echo "Checking deployment environment..."
health_response=$(curl -s "$DEPLOYMENT_URL/health")
environment=$(echo $health_response | jq -r '.environment' 2>/dev/null || echo "unknown")
version=$(echo $health_response | jq -r '.version' 2>/dev/null || echo "unknown")

echo "  Environment: $environment"
echo "  Version: $version"

if [ "$environment" = "production" ]; then
    echo -e "  ${GREEN}✓ Running in production mode${NC}"
else
    echo -e "  ${YELLOW}⚠ Not running in production mode${NC}"
fi
echo ""

# Test 6: Response Time
echo -n "Testing response time... "
start_time=$(date +%s%N)
curl -s -o /dev/null "$DEPLOYMENT_URL/health"
end_time=$(date +%s%N)
elapsed_ms=$(( ($end_time - $start_time) / 1000000 ))

if [ $elapsed_ms -lt 1000 ]; then
    echo -e "${GREEN}✓ PASS${NC} (${elapsed_ms}ms)"
else
    echo -e "${YELLOW}⚠ SLOW${NC} (${elapsed_ms}ms)"
fi
echo ""

# Test 7: Check SSL/TLS
echo -n "Checking SSL/TLS... "
if [[ $DEPLOYMENT_URL == https://* ]]; then
    ssl_check=$(curl -s -I "$DEPLOYMENT_URL/health" | head -n1)
    if [[ $ssl_check == *"200"* ]] || [[ $ssl_check == *"301"* ]] || [[ $ssl_check == *"302"* ]]; then
        echo -e "${GREEN}✓ PASS${NC}"
        echo "  HTTPS enabled and working"
    else
        echo -e "${RED}✗ FAIL${NC}"
        echo "  HTTPS connection failed"
        ((failures++))
    fi
else
    echo -e "${YELLOW}⚠ WARNING${NC}"
    echo "  Not using HTTPS (strongly recommended for production)"
fi
echo ""

# Summary
echo "=========================================="
echo "Verification Summary"
echo "=========================================="

if [ $failures -eq 0 ]; then
    echo -e "${GREEN}All critical tests passed!${NC}"
    echo ""
    echo "Deployment URL: $DEPLOYMENT_URL"
    echo "Status: Ready for integration"
    echo ""
    echo "Next steps:"
    echo "1. Update En Garde backend .env with:"
    echo "   SANKORE_API_URL=$DEPLOYMENT_URL"
    echo ""
    echo "2. Update Railway Sankore ALLOWED_ORIGINS with actual frontend/backend URLs"
    echo ""
    echo "3. Test integration from En Garde platform"
    exit 0
else
    echo -e "${RED}$failures test(s) failed${NC}"
    echo ""
    echo "Please review the failures above and:"
    echo "1. Check Railway logs for errors"
    echo "2. Verify environment variables are set correctly"
    echo "3. Ensure database is provisioned and connected"
    echo "4. Verify API keys are valid (OpenAI, Meta, TikTok)"
    exit 1
fi
