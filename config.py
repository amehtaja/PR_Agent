import os

GITHUB_APP_ID = os.environ.get("GITHUB_APP_ID")
GITHUB_PRIVATE_KEY_PATH = os.environ.get("GITHUB_PRIVATE_KEY_PATH", "private-key.pem")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")

PORT = int(os.environ.get("PORT", 5000))
HOST = os.environ.get("HOST", "0.0.0.0")
BASE_BRANCH = os.environ.get("BASE_BRANCH", "main")
