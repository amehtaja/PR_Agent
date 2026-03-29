"""
GitHub API helpers for Steps 5 and 6.
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
    """
    STEP 5 — Check if PR exists

    Input:  repo, branch, token
    Call:   get_open_prs(repo, branch, token)
    Output:
      Case 1 (no PR):     []
      Case 2 (PR exists): [{"number": 12, "title": "Old PR"}]
    """
    owner = repo.split("/")[0]
    return _request("GET", f"/repos/{repo}/pulls?state=open&head={owner}:{branch}", token)


def get_diff(repo, base, head, token):
    """
    STEP 6 — Get code diff

    Input:  repo, base="main", head=branch, token
    Call:   get_diff(repo, base, head, token)
    Output: "+ def login():\\n+     return \\"success\\""
    """
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
