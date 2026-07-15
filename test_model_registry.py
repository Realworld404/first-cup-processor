#!/usr/bin/env python3
"""Regression tests for model resolution + deprecation fallback.

Run: python3 test_model_registry.py

Covers the failure that took the service down on 2026-07-14: the model ID
`claude-sonnet-4-20250514` was retired, every API call 404'd, and the watcher
crash-looped for weeks. These tests lock in (a) a single source of truth for the
model ID, (b) graceful handling when a model disappears, and (c) a structural
guarantee that no call site can reintroduce a hardcoded model literal.
"""

import json
import os
import re
import sys
import tempfile
from pathlib import Path

import model_registry
from model_registry import (
    DEFAULT_MODEL,
    ModelUnavailableError,
    get_model,
    set_model,
    suggest_alternatives,
)

REPO = Path(__file__).parent
passed = failed = 0


def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"✓ {name} PASSED")
    else:
        failed += 1
        print(f"✗ {name} FAILED {detail}")


def _tmp_config(api_block):
    """Write a throwaway config.json so tests never touch the real one."""
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    cfg = {"directories": {"transcripts": "./t"}, "slack": {"enabled": True}}
    if api_block is not None:
        cfg["api"] = api_block
    Path(path).write_text(json.dumps(cfg, indent=2))
    return Path(path)


# --- Resolution: one source of truth -----------------------------------------

def test_get_model_reads_config():
    p = _tmp_config({"model": "claude-opus-4-8"})
    check("get_model reads config.json api.model",
          get_model(config_path=p) == "claude-opus-4-8")
    p.unlink()


def test_get_model_falls_back_when_key_missing():
    p = _tmp_config(None)  # no api block at all
    check("get_model falls back to DEFAULT_MODEL when api.model absent",
          get_model(config_path=p) == DEFAULT_MODEL)
    p.unlink()


def test_get_model_survives_corrupt_config():
    fd, path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    Path(path).write_text("{ this is not json")
    check("get_model falls back to DEFAULT_MODEL on corrupt config (no crash)",
          get_model(config_path=Path(path)) == DEFAULT_MODEL)
    Path(path).unlink()


def test_env_var_overrides_config():
    p = _tmp_config({"model": "claude-opus-4-8"})
    os.environ["ANTHROPIC_MODEL"] = "claude-haiku-4-5"
    try:
        check("ANTHROPIC_MODEL env var wins over config (escape hatch)",
              get_model(config_path=p) == "claude-haiku-4-5")
    finally:
        del os.environ["ANTHROPIC_MODEL"]
    p.unlink()


# --- Persistence: the selection must survive a restart ------------------------

def test_set_model_persists_and_roundtrips():
    p = _tmp_config({"model": "dead-model", "watch_interval": 10})
    set_model("claude-opus-4-8", config_path=p)
    check("set_model round-trips through get_model",
          get_model(config_path=p) == "claude-opus-4-8")
    p.unlink()


def test_set_model_preserves_other_keys():
    p = _tmp_config({"model": "dead-model", "watch_interval": 10})
    set_model("claude-opus-4-8", config_path=p)
    cfg = json.loads(p.read_text())
    ok = (cfg["api"]["watch_interval"] == 10
          and cfg["directories"]["transcripts"] == "./t"
          and cfg["slack"]["enabled"] is True)
    check("set_model preserves unrelated config keys (read-modify-write)", ok,
          f"got {cfg}")
    p.unlink()


def test_set_model_rejects_empty():
    p = _tmp_config({"model": "claude-sonnet-5"})
    try:
        set_model("", config_path=p)
        check("set_model rejects empty model id", False, "no exception raised")
    except ValueError:
        check("set_model rejects empty model id", True)
    p.unlink()


# --- Fallback: offering alternatives -----------------------------------------

class _FakeModels:
    def __init__(self, ids):
        self._ids = ids

    def list(self, limit=50):
        return [type("M", (), {"id": i}) for i in self._ids]


class _FakeClient:
    def __init__(self, ids):
        self.models = _FakeModels(ids)


def test_suggest_alternatives_excludes_dead_model():
    client = _FakeClient(["claude-sonnet-5", "claude-opus-4-8", "claude-sonnet-4-20250514"])
    alts = suggest_alternatives(client, "claude-sonnet-4-20250514")
    check("suggest_alternatives never offers the dead model back",
          "claude-sonnet-4-20250514" not in alts, f"got {alts}")


def test_suggest_alternatives_prefers_same_family():
    client = _FakeClient(["claude-haiku-4-5", "claude-opus-4-8", "claude-sonnet-5"])
    alts = suggest_alternatives(client, "claude-sonnet-4-20250514")
    check("suggest_alternatives ranks same-family (sonnet) first",
          alts and alts[0].startswith("claude-sonnet"), f"got {alts}")


def test_suggest_alternatives_handles_api_failure():
    class Boom:
        class models:
            @staticmethod
            def list(limit=50):
                raise RuntimeError("network down")
    alts = suggest_alternatives(Boom(), "claude-sonnet-4-20250514")
    check("suggest_alternatives degrades to curated fallback if Models API fails",
          isinstance(alts, list) and len(alts) > 0, f"got {alts}")


def test_model_unavailable_error_carries_model_id():
    e = ModelUnavailableError("gone", model="claude-sonnet-4-20250514")
    check("ModelUnavailableError carries the offending model id",
          e.model == "claude-sonnet-4-20250514")


# --- Structural invariant (principle #7) -------------------------------------

def test_no_hardcoded_model_literals_at_call_sites():
    """THE anti-drift test.

    A hardcoded model string at a messages.create() call site is exactly what
    went stale and took the service down. Only model_registry.py may name a
    concrete model (as DEFAULT_MODEL / the curated fallback list). If this test
    fails, someone reintroduced the bug class.
    """
    offenders = []
    for py in REPO.glob("*.py"):
        if py.name in ("model_registry.py", "test_model_registry.py"):
            continue
        for i, line in enumerate(py.read_text().splitlines(), 1):
            if re.search(r'model\s*=\s*["\']claude-', line):
                offenders.append(f"{py.name}:{i}: {line.strip()}")
    check("no hardcoded claude-* model literal outside model_registry.py",
          not offenders,
          "\n    " + "\n    ".join(offenders) if offenders else "")


def test_call_claude_api_raises_model_unavailable_on_404():
    """A retired model must raise ModelUnavailableError, NOT a bare Exception.

    Bare Exception => the generic handler swallows it and the watcher retries
    forever (the actual outage). ModelUnavailableError => we pause and ask.
    """
    import anthropic
    import httpx
    import youtube_processor

    # A real httpx.Response — the SDK's error classes read .request off it.
    _resp = httpx.Response(
        404,
        request=httpx.Request("POST", "https://api.anthropic.com/v1/messages"),
    )

    class Dead:
        class messages:
            @staticmethod
            def create(**kw):
                raise anthropic.NotFoundError(
                    message="model: claude-sonnet-4-20250514",
                    response=_resp,
                    body=None,
                )

    try:
        youtube_processor.call_claude_api(Dead(), "hi", max_tokens=10)
        check("call_claude_api raises ModelUnavailableError on 404", False,
              "no exception raised")
    except ModelUnavailableError as e:
        check("call_claude_api raises ModelUnavailableError on 404",
              "claude-" in (e.model or ""), f"model={e.model!r}")
    except Exception as e:
        check("call_claude_api raises ModelUnavailableError on 404", False,
              f"raised {type(e).__name__} instead: {e}")


def test_handler_reaches_slack_without_nameerror():
    """Regression: the ModelUnavailableError handler referenced an undefined
    `client`, raising NameError before it ever notified Slack — so the watcher
    hot-looped instead of pausing (observed in live testing 2026-07-14).

    The earlier tests only checked that call_claude_api *raises* the error; none
    exercised the *handler*. This drives process_transcript_file end-to-end with
    fakes and asserts it notifies Slack and persists the choice — no NameError.
    """
    import youtube_processor as yp

    calls = {}

    class FakeSlack:
        def is_enabled(self):
            return True

        def start_new_thread(self):
            pass

        def notify_processing_start(self, f):
            pass

        def notify_model_unavailable(self, model, alts, filename):
            calls["notified"] = (model, list(alts), filename)

        def poll_for_model_choice(self, alts):
            calls["polled"] = list(alts)
            return alts[0]

        def notify_model_selected(self, model):
            calls["selected"] = model

    def boom(*a, **k):
        raise ModelUnavailableError("gone", model="claude-sonnet-4-20250514")

    saved = {}
    orig = {
        "title": yp.interactive_title_selection,
        "suggest": yp.suggest_alternatives,
        "set_model": yp.set_model,
    }
    yp.interactive_title_selection = boom
    yp.suggest_alternatives = lambda client, model: ["claude-sonnet-5", "claude-opus-4-8"]
    yp.set_model = lambda m: saved.__setitem__("model", m)

    tdir = Path(tempfile.mkdtemp())
    tf = tdir / "ep.txt"
    tf.write_text("transcript body")

    try:
        result = yp.process_transcript_file(
            tf, str(tdir), "sk-fake-key",
            Path("nonexistent-template.txt"), Path("nonexistent-examples.md"),
            slack=FakeSlack(),
        )
        ok = (
            "notified" in calls
            and "polled" in calls
            and saved.get("model") == "claude-sonnet-5"
            and result is None
        )
        check("ModelUnavailableError handler notifies Slack + persists choice "
              "(no NameError)", ok, f"calls={calls} saved={saved}")
    except NameError as e:
        check("ModelUnavailableError handler notifies Slack + persists choice "
              "(no NameError)", False, f"NameError: {e}")
    finally:
        yp.interactive_title_selection = orig["title"]
        yp.suggest_alternatives = orig["suggest"]
        yp.set_model = orig["set_model"]
        tf.unlink()
        tdir.rmdir()


def test_load_config_executes():
    """Regression: load_config() referenced the removed MODEL constant.

    Importing youtube_processor was not enough to catch it — the NameError only
    fired when load_config() actually ran, i.e. at service startup. Call it.
    """
    import youtube_processor
    try:
        cfg = youtube_processor.load_config()
        check("load_config() runs without NameError (startup path)",
              bool(cfg.get("api", {}).get("model")), f"got {cfg.get('api')}")
    except NameError as e:
        check("load_config() runs without NameError (startup path)", False, str(e))


def main():
    print("=" * 60)
    print("MODEL REGISTRY / DEPRECATION FALLBACK TESTS")
    print("=" * 60)
    for fn in [
        test_handler_reaches_slack_without_nameerror,
        test_load_config_executes,
        test_get_model_reads_config,
        test_get_model_falls_back_when_key_missing,
        test_get_model_survives_corrupt_config,
        test_env_var_overrides_config,
        test_set_model_persists_and_roundtrips,
        test_set_model_preserves_other_keys,
        test_set_model_rejects_empty,
        test_suggest_alternatives_excludes_dead_model,
        test_suggest_alternatives_prefers_same_family,
        test_suggest_alternatives_handles_api_failure,
        test_model_unavailable_error_carries_model_id,
        test_no_hardcoded_model_literals_at_call_sites,
        test_call_claude_api_raises_model_unavailable_on_404,
    ]:
        try:
            fn()
        except Exception as e:
            global failed
            failed += 1
            print(f"✗ {fn.__name__} ERRORED: {type(e).__name__}: {e}")

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
