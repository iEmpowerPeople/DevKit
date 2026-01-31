---
description: Start the LLM API Key Proxy server
---

# Start LLM API Key Proxy

Start the proxy server for LLM API key management.

## Pre-flight Check

Ensure Docker is running. If not, start Docker Desktop:

```bash
docker info >/dev/null 2>&1 || open -a Docker
```

If Docker Desktop is starting, wait until it finishes before continuing.

Verify Docker is available and the image exists:

```bash
docker image inspect llm-api-key-proxy:arm64 >/dev/null
```

If missing, build it first from the project directory.

## Start Server

```bash
cd /Users/xandru_industries/Dev/tools/LLM-API-Key-Proxy
docker run -d \
  --name llm-api-proxy \
  --restart unless-stopped \
  -p 8000:8000 \
  -v $(pwd)/.env:/app/.env:ro \
  -v $(pwd)/oauth_creds:/app/oauth_creds \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/key_usage.json:/app/key_usage.json \
  -e SKIP_OAUTH_INIT_CHECK=true \
  -e PYTHONUNBUFFERED=1 \
  llm-api-key-proxy:arm64
```

## Notes

- Binds to `0.0.0.0:8000` (accessible from local network)
- Test with: `curl -s http://localhost:8000/`
- Expected response: `{"Status":"API Key Proxy is running"}`
