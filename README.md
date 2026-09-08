# gh-portfolio-mcp

A small [Model Context Protocol](https://modelcontextprotocol.io) server that exposes a GitHub user's public activity — repositories, languages, commit recency, and README content — as tools an LLM can call directly.

Built to go deeper than "read the MCP spec": this is a working server with three tools, real error handling, and no framework beyond the official `mcp` Python SDK.

## Why

Most MCP examples wrap a single API call. This one is intentionally a bit richer — it aggregates and ranks data (e.g. "most active repos in the last N days") rather than just proxying a single endpoint, since that's closer to what a real internal MCP server looks like.

## Tools exposed

### `list_repos`
List a user's public repositories, sorted by last push date, with language and star count.

| param | type | description |
|---|---|---|
| `username` | string | GitHub username |
| `limit` | int (optional, default 10) | Max repos to return |

### `get_repo_summary`
Fetch a single repo's description, primary language, topics, and README (first 2000 chars).

| param | type | description |
|---|---|---|
| `owner` | string | Repo owner |
| `repo` | string | Repo name |

### `most_active_repos`
Rank a user's repos by recent push activity — useful for "what has this person actually been working on lately" instead of a flat alphabetical list.

| param | type | description |
|---|---|---|
| `username` | string | GitHub username |
| `days` | int (optional, default 30) | Activity window |

## Running it

```bash
pip install -r requirements.txt
export GITHUB_TOKEN=your-token-here   # optional, raises the rate limit from 60/hr to 5000/hr
python server.py
```

Then point any MCP-compatible client (Claude Desktop, Claude Code, etc.) at it via stdio. Example Claude Desktop config:

```json
{
  "mcpServers": {
    "gh-portfolio": {
      "command": "python",
      "args": ["/absolute/path/to/server.py"],
      "env": { "GITHUB_TOKEN": "your-token-here" }
    }
  }
}
```

## License

MIT
