---
description: Research current documentation for LLM proxy, Claude Code, and OpenCode configuration before making changes
---

## Pre-flight Checks

Before researching or editing, verify the current proxy setup:

1. **Read proxy configuration:**
   - Read `~/Dev/tools/LLM-API-Key-Proxy/quota_viewer_config.json` to get:
     - `remotes[].host` and `remotes[].port` → construct `PROXY_URL` as `http://<host>:<port>`
     - `remotes[].api_key` → `PROXY_API_KEY`

2. **Test proxy connectivity:**
   ```bash
   curl -s <PROXY_URL>/
   ```
   Expected: `{"Status":"API Key Proxy is running"}`

---

## Research Topics

Before editing any proxy-related config files (~/.claude/settings.json or ~/.config/opencode/opencode.json), research the latest documentation using Perplexity:

1. Search for "Mirrowel LLM-API-Key-Proxy configuration model format providers" to understand:
   - Model naming format (provider/model_name)
   - Supported providers and their prefixes
   - Proxy endpoints (/v1/chat/completions for OpenAI, /v1/messages for Anthropic)

2. Search for "Claude Code settings.json configuration environment variables" to understand:
   - ANTHROPIC_BASE_URL, ANTHROPIC_AUTH_TOKEN format
   - Model tier variables (OPUS, SONNET, HAIKU)

3. Search for "OpenCode opencode.json provider configuration models" to understand:
   - Provider setup with @ai-sdk/openai-compatible
   - Model definition format (id, name, limit, modalities, reasoning, reasoningEffort)
   - baseURL and apiKey placement

4. If working on provider configuration, query configured providers:
   ```bash
   curl -s <PROXY_URL>/v1/providers -H "Authorization: Bearer <PROXY_API_KEY>"
   ```

---

## Key Format Differences

- Claude Code: ANTHROPIC_BASE_URL without /v1, uses Anthropic API format
- OpenCode: baseURL with /v1, uses OpenAI-compatible format
- Both use the proxy's model format: provider/model_name
