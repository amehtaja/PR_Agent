"""
Agent Flow — Steps 4, 5, 6 (called by webhook handler after Step 3)
"""

import os

from config import BASE_BRANCH
from github_auth import get_installation_token
from github_client import get_open_prs, get_diff


def run_agent(repo, branch, installation_id):
    """
    Called from app.py after a push webhook is received.

    Input: repo="user/repo", branch="feature-login", installation_id=123456
    """

    print(f"\n{'='*50}")
    print(f"[AGENT] Starting for {repo} @ {branch}")
    print(f"{'='*50}")

    # ── STEP 4: Authenticate with GitHub ─────────────────────────────
    #
    # Input:  installation_id = 123456
    # Action: get_installation_token(installation_id)
    # Output: token = "ghs_xxxxx"
    # ─────────────────────────────────────────────────────────────────
    test_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if test_token:
        # TEST MODE: use personal token instead of App auth
        print(f"\n[STEP 4] TEST MODE — using GITHUB_TOKEN from env")
        token = test_token
    else:
        # PRODUCTION: use GitHub App installation token
        print(f"\n[STEP 4] Authenticating with installation_id={installation_id}...")
        token = get_installation_token(installation_id)
    print(f"[STEP 4] ✓ Got token: {token[:10]}...")

    # ── STEP 5: Check if PR exists ───────────────────────────────────
    #
    # Input:  repo, branch, token
    # Call:   get_open_prs(repo, branch, token)
    # Output:
    #   Case 1 (no PR):     []
    #   Case 2 (PR exists): [{"number": 12, "title": "Old PR"}]
    # ─────────────────────────────────────────────────────────────────
    print(f"\n[STEP 5] Checking for open PRs on branch '{branch}'...")
    open_prs = get_open_prs(repo, branch, token)

    if len(open_prs) == 0:
        print(f"[STEP 5] ✓ No PR exists → will CREATE new PR")
        pr_exists = False
        pr_number = None
    else:
        pr_number = open_prs[0]["number"]
        pr_title = open_prs[0]["title"]
        print(f"[STEP 5] ✓ PR exists → #{pr_number} \"{pr_title}\" → will UPDATE")
        pr_exists = True

    # ── STEP 6: Get code diff ────────────────────────────────────────
    #
    # Input:  repo, base="main", head=branch, token
    # Call:   get_diff(repo, base, head, token)
    # Output: "+ def login():\n+     return \"success\""
    # ─────────────────────────────────────────────────────────────────
    base = BASE_BRANCH
    print(f"\n[STEP 6] Getting diff: {base}...{branch}...")
    diff = get_diff(repo, base, branch, token)
    print(f"[STEP 6] ✓ Got diff ({len(diff)} chars)")
    print(f"[STEP 6] Preview:\n{diff[:500]}")

    if not diff.strip():
        print("[STEP 6] Empty diff — nothing to do")
        return

    # ── STEPS 7-8: TODO (LLM generation + PR create/update) ─────────
    print(f"\n[DONE] Steps 4-6 complete.")
    print(f"  repo            = {repo}")
    print(f"  branch          = {branch}")
    print(f"  pr_exists       = {pr_exists}")
    print(f"  pr_number       = {pr_number}")
    print(f"  diff_length     = {len(diff)} chars")
    print(f"  Next: Step 7 (LLM) → Step 8 (Create/Update PR)")
