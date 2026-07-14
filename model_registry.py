#!/usr/bin/env python3
"""Single source of truth for which Claude model this project uses.

Why this module exists
----------------------
On 2026-07-14 the pinned model (`claude-sonnet-4-20250514`) was retired. Every
API call 404'd, the watcher crash-looped for weeks, and nobody noticed because
`KeepAlive` kept respawning it. Two things made that worse than it had to be:

1. The model ID was hardcoded at four call sites, so it drifted silently.
2. A 404 raised a bare Exception, which the generic handler swallowed — the
   processor just retried the same doomed call forever.

So: every model ID flows through `get_model()` here, and a retired model raises
`ModelUnavailableError`, which the processor handles by *asking the user to pick
a replacement* and persisting that choice via `set_model()`.

`test_model_registry.py` enforces that no other module may name a concrete model.
"""

import json
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.json"

# Fallback only — the live value is config.json `api.model`. Kept so a missing or
# corrupt config still boots. This is the ONE place a model literal may appear
# (alongside CURATED_FALLBACKS below).
DEFAULT_MODEL = "claude-sonnet-5"

# Used only if the Models API itself is unreachable when we need to offer choices.
# Deliberately short: the live API is the real source, this is a life raft.
CURATED_FALLBACKS = [
    "claude-sonnet-5",
    "claude-opus-4-8",
    "claude-haiku-4-5",
]


class ModelUnavailableError(Exception):
    """The configured model was rejected by the API (retired / renamed / no access).

    Retryable in principle — but only after a human picks a replacement, so the
    processor pauses rather than marking the transcript FAILED_.
    """

    def __init__(self, message, model=None):
        super().__init__(message)
        self.model = model


def get_model(config_path=CONFIG_PATH):
    """Resolve the active model ID. THE only way to learn which model to call.

    Precedence: ANTHROPIC_MODEL env var > config.json api.model > DEFAULT_MODEL.
    Never raises — a broken config must not take the processor down.
    """
    env = os.environ.get("ANTHROPIC_MODEL", "").strip()
    if env:
        return env

    try:
        with open(config_path) as f:
            model = json.load(f).get("api", {}).get("model")
        if model and str(model).strip():
            return str(model).strip()
    except (OSError, ValueError, AttributeError):
        pass  # missing/corrupt config → fall through to the default

    return DEFAULT_MODEL


def set_model(model_id, config_path=CONFIG_PATH):
    """Persist the chosen model to config.json so it survives a restart.

    Read-modify-write: preserves every other key in the file.
    """
    model_id = (model_id or "").strip()
    if not model_id:
        raise ValueError("model_id must be a non-empty string")

    try:
        with open(config_path) as f:
            config = json.load(f)
    except (OSError, ValueError):
        config = {}

    config.setdefault("api", {})["model"] = model_id

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
        f.write("\n")

    return model_id


def _family(model_id):
    """'claude-sonnet-4-20250514' -> 'sonnet'. Used to rank like-for-like swaps."""
    for fam in ("fable", "opus", "sonnet", "haiku"):
        if fam in (model_id or ""):
            return fam
    return ""


def list_available_models(client, limit=50):
    """Ask the API which models actually exist right now.

    Deliberately NOT a hardcoded list — a stale hardcoded list is the very thing
    that caused the outage.
    """
    return [m.id for m in client.models.list(limit=limit)]


def suggest_alternatives(client, unavailable_model, limit=50):
    """Rank live models as replacements for `unavailable_model`.

    Same family first (a sonnet user probably wants another sonnet: similar cost
    and latency), then everything else. The dead model is never offered back.
    Degrades to CURATED_FALLBACKS if the Models API is unreachable — we must be
    able to offer *something*, since the whole point is to unblock the pipeline.
    """
    try:
        available = list_available_models(client, limit=limit)
    except Exception:
        available = list(CURATED_FALLBACKS)

    candidates = [m for m in available if m and m != unavailable_model]
    if not candidates:
        candidates = [m for m in CURATED_FALLBACKS if m != unavailable_model]

    want = _family(unavailable_model)
    # stable sort: same-family entries float to the top, original order kept within groups
    candidates.sort(key=lambda m: 0 if want and _family(m) == want else 1)
    return candidates
