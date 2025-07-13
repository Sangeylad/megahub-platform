#!/bin/bash
# /var/www/megahub/websites/humari-site/scripts/test-complete.sh

echo "🧪 Testing MEGAHUB Registry Cache System..."

# 1. État initial
echo "📋 Initial registry state:"
INITIAL=$(curl -s "https://humari.fr/api/builder/registry")
INITIAL_CB=$(echo "$INITIAL" | jq -r '.cache_breaker // "none"')
INITIAL_COUNT=$(echo "$INITIAL" | jq -r '.metadata.total_sections // 0')
echo "Cache Breaker: $INITIAL_CB"
echo "Sections Count: $INITIAL_COUNT"

echo ""
echo "🔄 Sending invalidation request..."

# 2. Invalidation avec body correct
INVALIDATE_RESPONSE=$(curl -s -X POST "https://humari.fr/api/builder/registry/invalidate" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "CLI test - Registry update", 
    "website_id": 34,
    "preload": true
  }')

echo "📦 Invalidation response:"
echo "$INVALIDATE_RESPONSE" | jq '{
  success: .success, 
  webhook_sent: .webhook_sent, 
  cache_breaker: .cache_breaker,
  django_status: .django_status
}'

echo ""
echo "⏱️ Waiting 2 seconds for propagation..."
sleep 2

# 3. État après invalidation
echo "📋 Registry after invalidation:"
AFTER=$(curl -s "https://humari.fr/api/builder/registry")
AFTER_CB=$(echo "$AFTER" | jq -r '.cache_breaker // "none"')
AFTER_COUNT=$(echo "$AFTER" | jq -r '.metadata.total_sections // 0')
echo "Cache Breaker: $AFTER_CB"
echo "Sections Count: $AFTER_COUNT"

echo ""
echo "📊 Summary:"
if [ "$INITIAL_CB" != "$AFTER_CB" ]; then
  echo "✅ Cache invalidation SUCCESSFUL"
  echo "   Before: $INITIAL_CB"
  echo "   After:  $AFTER_CB"
else
  echo "❌ Cache invalidation FAILED (same cache_breaker)"
fi

if [ "$INITIAL_COUNT" != "$AFTER_COUNT" ]; then
  echo "🔄 Sections count changed: $INITIAL_COUNT → $AFTER_COUNT"
else
  echo "📋 Sections count stable: $AFTER_COUNT"
fi