#!/usr/bin/env python3
"""
gh-portfolio-mcp — an MCP server exposing GitHub user activity as tools.

Tools:
  - list_repos(username, limit=10)
  - get_repo_summary(owner, repo)
  - most_active_repos(username, days=30)
"""
import os
from datetime import datetime, timezone
from typing import Any

import requests
from mcp.server.fastmcp import FastMCP

GITHUB_API = "https://api.github.com"
mcp = FastMCP("gh-portfolio")


def _headers() -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"token {token}"
    return headers


def _get(url: str, params: dict[str, Any] | None = None) -> Any:
    resp = requests.get(url, headers=_headers(), params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


@mcp.tool()
def list_repos(username: str, limit: int = 10) -> list[dict[str, Any]]:
    """List a GitHub user's public repositories, sorted by last push date.

    Args:
        username: GitHub username.
        limit: Maximum number of repos to return (default 10).
    """
    repos = _get(
        f"{GITHUB_API}/users/{username}/repos",
        params={"per_page": 100, "sort": "pushed", "type": "owner"},
    )
    return [
        {
            "name": r["name"],
            "description": r["description"],
            "language": r["language"],
            "stars": r["stargazers_count"],
            "pushed_at": r["pushed_at"],
            "url": r["html_url"],
        }
        for r in repos[:limit]
    ]


@mcp.tool()
def get_repo_summary(owner: str, repo: str) -> dict[str, Any]:
    """Get a repository's description, language, topics, and README excerpt.

    Args:
        owner: Repository owner (user or org).
        repo: Repository name.
    """
    repo_data = _get(f"{GITHUB_API}/repos/{owner}/{repo}")

    readme_text = ""
    try:
        readme = _get(f"{GITHUB_API}/repos/{owner}/{repo}/readme")
        import base64

        readme_text = base64.b64decode(readme["content"]).decode("utf-8", errors="replace")[:2000]
    except requests.HTTPError:
        readme_text = "(no README found)"

    return {
        "name": repo_data["name"],
        "description": repo_data["description"],
        "language": repo_data["language"],
        "topics": repo_data.get("topics", []),
        "stars": repo_data["stargazers_count"],
        "readme_excerpt": readme_text,
        "url": repo_data["html_url"],
    }


@mcp.tool()
def most_active_repos(username: str, days: int = 30) -> list[dict[str, Any]]:
    """Rank a user's repos by recent push activity within a time window.

    Args:
        username: GitHub username.
        days: Look-back window in days (default 30).
    """
    repos = _get(
        f"{GITHUB_API}/users/{username}/repos",
        params={"per_page": 100, "sort": "pushed", "type": "owner"},
    )
    now = datetime.now(timezone.utc)
    active = []
    for r in repos:
        pushed_at = datetime.fromisoformat(r["pushed_at"].replace("Z", "+00:00"))
        age_days = (now - pushed_at).days
        if age_days <= days:
            active.append(
                {
                    "name": r["name"],
                    "language": r["language"],
                    "days_since_push": age_days,
                    "url": r["html_url"],
                }
            )
    return sorted(active, key=lambda r: r["days_since_push"])


if __name__ == "__main__":
    mcp.run()
