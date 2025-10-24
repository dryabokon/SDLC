from mcp.server.fastmcp import FastMCP
import os
import json
import base64
import zipfile
from io import BytesIO
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


# ----------------------------------- GitHub Repository tools --------------------------------
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


# ----------------------------------- GitHub Actions tools --------------------------------
@app.tool(description="List workflow runs. repo: 'owner/name', limit: max runs to return (default 10)")
def github_list_runs(repo: str, limit: int = 10) -> str:
    owner, name = repo.split("/", 1)
    runs = _gh_get(
        f"/repos/{owner}/{name}/actions/runs",
        params={"per_page": limit}
    )
    out = []
    for run in runs.get("workflow_runs", []):
        out.append({
            "run_id": run.get("id"),
            "run_number": run.get("run_number"),
            "name": run.get("name"),
            "status": run.get("status"),
            "conclusion": run.get("conclusion"),
            "created_at": run.get("created_at"),
            "updated_at": run.get("updated_at"),
        })
    return json.dumps(out, ensure_ascii=False, indent=2)


@app.tool(description="Get latest workflow run details. repo: 'owner/name'")
def github_get_latest_run(repo: str) -> str:
    owner, name = repo.split("/", 1)
    runs = _gh_get(f"/repos/{owner}/{name}/actions/runs", params={"per_page": 1})
    if not runs.get("workflow_runs"):
        return json.dumps({"error": "No runs found"})
    run = runs["workflow_runs"][0]
    return json.dumps({
        "run_id": run.get("id"),
        "run_number": run.get("run_number"),
        "name": run.get("name"),
        "status": run.get("status"),
        "conclusion": run.get("conclusion"),
        "created_at": run.get("created_at"),
        "head_branch": run.get("head_branch"),
        "head_sha": run.get("head_sha"),
    }, ensure_ascii=False, indent=2)


@app.tool(description="List artifacts from a workflow run. repo: 'owner/name', run_id: workflow run ID")
def github_list_artifacts(repo: str, run_id: str) -> str:
    owner, name = repo.split("/", 1)
    artifacts = _gh_get(f"/repos/{owner}/{name}/actions/runs/{run_id}/artifacts")
    out = []
    for artifact in artifacts.get("artifacts", []):
        out.append({
            "id": artifact.get("id"),
            "name": artifact.get("name"),
            "size_in_bytes": artifact.get("size_in_bytes"),
            "created_at": artifact.get("created_at"),
            "expires_at": artifact.get("expires_at"),
        })
    return json.dumps(out, ensure_ascii=False, indent=2)


@app.tool(description="Download artifact contents as ZIP. repo: 'owner/name', artifact_id: artifact ID")
def github_download_artifact(repo: str, artifact_id: str) -> str:
    owner, name = repo.split("/", 1)
    url = f"{GITHUB_API}/repos/{owner}/{name}/actions/artifacts/{artifact_id}/zip"
    req = request.Request(url, headers=_gh_headers())

    try:
        with request.urlopen(req) as resp:
            zip_data = resp.read()

        # Extract and list contents
        zip_file = zipfile.ZipFile(BytesIO(zip_data))
        files = {}
        for filename in zip_file.namelist():
            try:
                content = zip_file.read(filename).decode('utf-8', errors='replace')
                files[filename] = content
            except:
                files[filename] = f"[Binary file: {filename}]"

        return json.dumps(files, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@app.tool(
    description="Get artifact file content. repo: 'owner/name', run_id: run ID, artifact_name: artifact name, file_path: path in artifact")
def github_get_artifact_file(repo: str, run_id: str, artifact_name: str, file_path: str) -> str:
    owner, name = repo.split("/", 1)

    # List artifacts for this run
    artifacts = _gh_get(f"/repos/{owner}/{name}/actions/runs/{run_id}/artifacts")
    artifact_id = None
    for artifact in artifacts.get("artifacts", []):
        if artifact.get("name") == artifact_name:
            artifact_id = artifact.get("id")
            break

    if not artifact_id:
        return json.dumps({"error": f"Artifact '{artifact_name}' not found"})

    # Download and extract
    url = f"{GITHUB_API}/repos/{owner}/{name}/actions/artifacts/{artifact_id}/zip"
    req = request.Request(url, headers=_gh_headers())

    try:
        with request.urlopen(req) as resp:
            zip_data = resp.read()

        zip_file = zipfile.ZipFile(BytesIO(zip_data))

        # Find the file in the artifact
        for filename in zip_file.namelist():
            if file_path in filename or filename.endswith(file_path):
                content = zip_file.read(filename).decode('utf-8', errors='replace')
                return content

        return json.dumps({"error": f"File '{file_path}' not found in artifact"})
    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    app.run()