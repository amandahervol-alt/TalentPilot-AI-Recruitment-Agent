"""Shared helpers for calling Claude and reading its replies."""
import re

DEFAULT_MODEL = "claude-sonnet-5-5"
# Sonnet 5.5 rejects temperature/top_p/top_k; effort controls thinking depth instead.
REQUEST_OPTIONS = {"extra_body": {"output_config": {"effort": "low"}}}


def first_text(response) -> str:
    """Return the first text block; adaptive thinking may put thinking blocks first."""
    for block in getattr(response, "content", None) or []:
        if getattr(block, "type", None) == "text":
            return block.text
    raise ValueError("Claude response contained no text block")


def strip_code_fences(content: str) -> str:
    content = content.strip()
    match = re.match(r"^```[\w-]*\s*\n?(.*?)\n?```\s*$", content, re.DOTALL)
    return match.group(1).strip() if match else content
