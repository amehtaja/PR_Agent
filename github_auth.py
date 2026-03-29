"""
STEP 4 — Authenticate with GitHub

Input:  installation_id = 123456
Action: get_installation_token(installation_id)
Output: token = "ghs_xxxxx"  → used for all GitHub API calls
"""

import json
import time
import urllib.request
import urllib.error

import jwt
import config


def _read_private_key():
    with open(config.GITHUB_PRIVATE_KEY_PATH, "r") as f:
        return f.read()


def _generate_jwt():
    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + (10 * 60),
        "iss": config.GITHUB_APP_ID,
    }
    return jwt.encode(payload, _read_private_key(), algorithm="RS256")


def get_installation_token(installation_id):
    """
    Input:  installation_id = 123456
    Output: token = "ghs_xxxxx"
    """
    token_jwt = _generate_jwt()
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"

    req = urllib.request.Request(url, method="POST", headers={
        "Authorization": f"Bearer {token_jwt}",
        "Accept": "application/vnd.github+json",
    })

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            return data["token"]
    except urllib.error.HTTPError as e:
        print(f"[STEP 4] Auth failed: {e.code} {e.read().decode()}")
        raise
