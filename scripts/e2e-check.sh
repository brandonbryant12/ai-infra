#!/usr/bin/env bash
set -euo pipefail

echo "🔎 E2E check: starting (this will start services if not up)"
make start >/dev/null

echo "⏳ Waiting for Langfuse ([http://localhost:3100](http://localhost:3100)) ..."
for i in {1..30}; do
if curl -fsS -o /dev/null [http://localhost:3100/](http://localhost:3100/); then
echo "✅ Langfuse up"
break
fi
sleep 2
done

echo "⏳ Waiting for LiteLLM health ([http://localhost:4000/health](http://localhost:4000/health)) ..."
for i in {1..30}; do
if curl -fsS -o /dev/null [http://localhost:4000/health](http://localhost:4000/health); then
echo "✅ LiteLLM up"
break
fi
sleep 2
done

echo "⏳ Waiting for OpenWebUI ([http://localhost:3000](http://localhost:3000)) ..."
for i in {1..30}; do
if curl -fsS -o /dev/null [http://localhost:3000/](http://localhost:3000/); then
echo "✅ OpenWebUI up"
break
fi
sleep 2
done

echo "🧪 Listing models via LiteLLM ..."
curl -fsS [http://localhost:4000/v1/models](http://localhost:4000/v1/models) | jq '.data | length' || true

echo "🧪 Chat completion sanity via LiteLLM ..."
curl -fsS [http://localhost:4000/v1/chat/completions](http://localhost:4000/v1/chat/completions)&#x20;
-H "Content-Type: application/json"&#x20;
-H "Authorization: Bearer \${LITELLM\_MASTER\_KEY:-sk-1234}"&#x20;
-H "X-OpenWebUI-User-Id: e2e-check-user"&#x20;
-d '{
"model": "openrouter/openrouter/auto",
"messages":\[{"role":"user","content":"Say "E2E OK""}],
"max\_tokens": 10
}' | jq '.choices\[0].message.content' || true

# echo "🎯 E2E check complete. Open Langfuse to confirm trace."

```