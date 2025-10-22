from mcp.server.fastmcp import FastMCP
import os
import json
import base64
from urllib import request, parse
from typing import Optional

app = FastMCP("github-remote-tools")

# --------------------------- Utility: Minimal GitHub REST client ---------------------------
GITHUB_API = "https://api.github.com"

def _gh_headers() -> dict:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "mcp-fastmcp-demo",
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def _gh_get(path: str, params: Optional[dict] = None) -> dict:
    url = f"{GITHUB_API}{path}"
    if params:
        url = f"{url}?{parse.urlencode(params)}"
    req = request.Request(url, headers=_gh_headers())
    with request.urlopen(req) as resp:
        data = resp.read()
    return json.loads(data.decode("utf-8"))

def _decode_base64_text(b64: str, encoding: str = "utf-8") -> str:
    return base64.b64decode(b64).decode(encoding, errors="replace")


# ----------------------------------- GitHub analysis tools --------------------------------
@app.tool(description="Get repository info summary. repo format: 'owner/name'")
def github_repo_info(repo: str) -> str:
    owner, name = repo.split("/", 1)
    info = _gh_get(f"/repos/{owner}/{name}")
    summary = {
        "full_name": info.get("full_name"),
        "description": info.get("description"),
        "default_branch": info.get("default_branch"),
        "stars": info.get("stargazers_count"),
        "forks": info.get("forks_count"),
        "open_issues": info.get("open_issues_count"),
        "language": info.get("language"),
    }
    return json.dumps(summary, ensure_ascii=False, indent=2)

@app.tool(description="Fetch README.md (decoded). repo format: 'owner/name'")
def github_readme(repo: str, ref: Optional[str] = None) -> str:
    owner, name = repo.split("/", 1)
    params = {"ref": ref} if ref else None
    data = _gh_get(f"/repos/{owner}/{name}/readme", params=params)
    content = data.get("content")
    if not content:
        return "(No README content)"
    return _decode_base64_text(content)

@app.tool(description="List files at path in repo. repo: 'owner/name', path default repo root")
def github_list_files(repo: str, path: str = "", ref: Optional[str] = None) -> str:
    owner, name = repo.split("/", 1)
    api_path = f"/repos/{owner}/{name}/contents/{path}" if path else f"/repos/{owner}/{name}/contents"
    params = {"ref": ref} if ref else None
    data = _gh_get(api_path, params=params)
    if isinstance(data, dict) and data.get("type") == "file":
        return json.dumps({"type": "file", "name": data.get("name"), "path": data.get("path")}, indent=2)
    items = []
    for entry in data:
        items.append({"type": entry.get("type"), "name": entry.get("name"), "path": entry.get("path")})
    return json.dumps(items, ensure_ascii=False, indent=2)

@app.tool(description="Get a text file from repo (decoded). repo: 'owner/name', path: file path")
def github_get_file(repo: str, path: str, ref: Optional[str] = None) -> str:
    owner, name = repo.split("/", 1)
    params = {"ref": ref} if ref else None
    data = _gh_get(f"/repos/{owner}/{name}/contents/{path}", params=params)
    if data.get("encoding") == "base64" and data.get("content"):
        return _decode_base64_text(data["content"])
    return json.dumps(data, ensure_ascii=False, indent=2)

@app.tool(description="List issues. repo: 'owner/name', state: open|closed|all")
def github_list_issues(repo: str, state: str = "open") -> str:
    owner, name = repo.split("/", 1)
    issues = _gh_get(f"/repos/{owner}/{name}/issues", params={"state": state, "per_page": 50})
    out = []
    for i in issues:
        if "pull_request" in i:
            continue
        out.append({"number": i.get("number"), "title": i.get("title"), "state": i.get("state")})
    return json.dumps(out, ensure_ascii=False, indent=2)

@app.tool(description="List pull requests. repo: 'owner/name', state: open|closed|all")
def github_list_prs(repo: str, state: str = "open") -> str:
    owner, name = repo.split("/", 1)
    prs = _gh_get(f"/repos/{owner}/{name}/pulls", params={"state": state, "per_page": 50})
    out = []
    for p in prs:
        out.append({"number": p.get("number"), "title": p.get("title"), "state": p.get("state")})
    return json.dumps(out, ensure_ascii=False, indent=2)



if __name__ == "__main__":
    app.run()
