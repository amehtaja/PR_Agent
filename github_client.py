"""
GitHub API helpers for Steps 5, 6, and 8.
"""

import json
import urllib.request
import urllib.error

API = "https://api.github.com"


def _request(method, path, token, body=None):
    url = f"{API}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, method=method, data=data, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"[github] {method} {url} → {e.code}: {e.read().decode()}")
        raise


def get_open_prs(repo, branch, token):
    owner = repo.split("/")[0]
    return _request("GET", f"/repos/{repo}/pulls?state=open&head={owner}:{branch}", token)


def get_diff(repo, base, head, token):
    url = f"{API}/repos/{repo}/compare/{base}...{head}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3.diff",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.read().decode()
    except urllib.error.HTTPError as e:
        print(f"[STEP 6] Diff failed: {e.code}: {e.read().decode()}")
        raise


def create_pr(repo, title, body, head, base, token):
    data = {"title": title, "body": body, "head": head, "base": base}
    result = _request("POST", f"/repos/{repo}/pulls", token, body=data)
    return {"number": result["number"], "html_url": result["html_url"]}


def update_pr(repo, pr_number, title, body, token):
    data = {"title": title, "body": body}
    result = _request("PATCH", f"/repos/{repo}/pulls/{pr_number}", token, body=data)
    return {"number": result["number"], "html_url": result["html_url"]}