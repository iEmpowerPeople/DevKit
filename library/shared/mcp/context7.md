---
description: Up-to-date, version-specific library/API documentation and code examples
---

# Context7 MCP

Context7 provides up-to-date, version-specific library/API documentation and code examples.

## Upstream

- Repo: https://github.com/upstash/context7

## Claude Code

Local (recommended when you have Node available):

```bash
claude mcp add context7 -- npx -y @upstash/context7-mcp --api-key YOUR_CONTEXT7_API_KEY
```

Remote (HTTP transport):

```bash
claude mcp add --header "CONTEXT7_API_KEY: YOUR_CONTEXT7_API_KEY" --transport http context7 https://mcp.context7.com/mcp
```

## Opencode

Local:

```json
{
  "mcp": {
    "context7": {
      "type": "local",
      "command": ["npx", "-y", "@upstash/context7-mcp", "--api-key", "YOUR_CONTEXT7_API_KEY"],
      "enabled": true
    }
  }
}
```

Remote:

```json
{
  "mcp": {
    "context7": {
      "type": "remote",
      "url": "https://mcp.context7.com/mcp",
      "headers": {
        "CONTEXT7_API_KEY": "YOUR_CONTEXT7_API_KEY"
      },
      "enabled": true
    }
  }
}
```

## Config Notes

- API key is recommended for higher rate limits: https://context7.com/dashboard
