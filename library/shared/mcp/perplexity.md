---
description: Official MCP server for the Perplexity API Platform (web search + ask/reason/research)
---

# Perplexity MCP

Official MCP server for the Perplexity API Platform (web search + ask/reason/research).

## Upstream

- Repo: https://github.com/perplexityai/modelcontextprotocol

## Claude Code (local stdio)

```bash
claude mcp add perplexity --env PERPLEXITY_API_KEY="YOUR_KEY" -- npx -y @perplexity-ai/mcp-server
```

## Opencode (local)

Add to your Opencode config (typically `~/.config/opencode/config.json`):

```json
{
  "mcp": {
    "perplexity": {
      "type": "local",
      "command": ["npx", "-y", "@perplexity-ai/mcp-server"],
      "env": {
        "PERPLEXITY_API_KEY": "YOUR_KEY"
      },
      "enabled": true
    }
  }
}
```

## Config Notes

- Required env: `PERPLEXITY_API_KEY`
- Optional env: `PERPLEXITY_TIMEOUT_MS`, `PERPLEXITY_LOG_LEVEL`
