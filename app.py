"""
Webhook server — STEPS 1, 2, 3

STEP 1: User installs GitHub App → store installation_id
STEP 2: Developer pushes code (external — nothing happens here yet)
STEP 3: GitHub sends push webhook → extract repo, branch, installation_id → call run_agent()
"""

import hashlib
import hmac
import json
import threading

from flask import Flask, request, jsonify

from config import WEBHOOK_SECRET, HOST, PORT
from agent import run_agent

app = Flask(__name__)

# ─────────────────────────────────────────────────────────────────────
# STEP 1 — Store installations
#
# When user installs the App, we receive:
#   { "installation": {"id": 123456}, "account": {"login": "user123"} }
#
# We store:  installations["user123"] = 123456
# ─────────────────────────────────────────────────────────────────────
installations = {}  # account_login → installation_id


def verify_signature(payload_body, signature):
    if not WEBHOOK_SECRET:
        return True
    expected = "sha256=" + hmac.new(
        WEBHOOK_SECRET.encode(), payload_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@app.route("/webhook", methods=["POST"])
def webhook():
    # Verify signature
    sig = request.headers.get("X-Hub-Signature-256", "")
    if not verify_signature(request.data, sig):
        return jsonify({"error": "Invalid signature"}), 401

    event = request.headers.get("X-GitHub-Event", "")
    payload = request.json

    # ── STEP 1: App installed ────────────────────────────────────────
    if event == "installation":
        action = payload.get("action")
        installation_id = payload["installation"]["id"]
        account = payload["installation"]["account"]["login"]

        if action == "created":
            installations[account] = installation_id
            print(f"[STEP 1] Installed for {account} → installation_id={installation_id}")
            return jsonify({"status": "installed", "installation_id": installation_id}), 200

        if action == "deleted":
            installations.pop(account, None)
            print(f"[STEP 1] Uninstalled for {account}")
            return jsonify({"status": "uninstalled"}), 200

    # ── STEP 3: Push webhook received ────────────────────────────────
    #
    # Payload:
    #   ref: "refs/heads/feature-login"
    #   repository.full_name: "user/repo"
    #   installation.id: 123456
    #
    # Extract → repo, branch, installation_id
    # Then call → run_agent(repo, branch, installation_id)
    # ─────────────────────────────────────────────────────────────────
    if event == "push":
        ref = payload.get("ref", "")
        repo = payload["repository"]["full_name"]
        installation_id = payload["installation"]["id"]

        # Only handle branch pushes
        if not ref.startswith("refs/heads/"):
            return jsonify({"status": "ignored", "reason": "not a branch"}), 200

        branch = ref.replace("refs/heads/", "")

        # Skip pushes to main/master
        if branch in ("main", "master"):
            return jsonify({"status": "ignored", "reason": "base branch"}), 200

        print(f"[STEP 3] Push received → repo={repo}, branch={branch}, installation_id={installation_id}")

        # Run agent in background so we respond to GitHub quickly
        thread = threading.Thread(
            target=run_agent, args=(repo, branch, installation_id), daemon=True
        )
        thread.start()

        return jsonify({"status": "processing"}), 202

    return jsonify({"status": "ignored", "event": event}), 200


if __name__ == "__main__":
    print(f"[app] Webhook server starting on {HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=True)
