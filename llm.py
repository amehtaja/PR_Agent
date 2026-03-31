"""
Step 7 — Generate PR title and description from a code diff using Claude AI.
"""

import anthropic
import json
import re

from config import ANTHROPIC_API_KEY

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


SYSTEM_PROMPT = """You are a senior software engineer writing Pull Request descriptions.
Given a code diff, produce a concise PR title and a clear markdown description.
Always respond in this exact JSON format (no extra text):
{
  "title": "<short imperative title, max 72 chars>",
  "description": "## Summary\\n<what this PR does>\\n\\n## What Changed\\n<bullet list of changes>\\n\\n## Why\\n<reason / motivation>\\n\\n## Test Plan\\n<how to verify>"
}"""


def generate_pr_content(diff: str) -> dict:
    if len(diff) > 8000:
        diff = diff[:8000] + "\n\n... (diff truncated)"

    client = _get_client()

    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": f"Here is the code diff:\n\n```diff\n{diff}\n```\n\nGenerate the PR title and description."
            }
        ]
    )

    raw = message.content[0].text.strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            result = json.loads(match.group())
        else:
            raise ValueError(f"Claude returned unexpected format: {raw[:200]}")

    return {
        "title": result["title"],
        "description": result["description"]
    }