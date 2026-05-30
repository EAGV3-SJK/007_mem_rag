"""Bridge to llm_gatewayV7.

V7 is V3 plus a single new endpoint, `POST /v1/embed`. The session-version
mapping (V7 for Session 7) lets us evolve the gateway forward without
touching prior versions. V3 remains available for Session 6 agents.

Auto-starts the gateway on port 8107 if it is not already up, then
re-exports the V7 `LLM` client and a module-level `embed()` helper. Every
layer in this agent imports from here so the boot logic lives in one place.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

import httpx

GATEWAY_V7_DIR = Path(__file__).resolve().parents[0] / "llm_gatewayV7"
GATEWAY_URL = "http://localhost:8107"

# Optional provider pin. Set LLM_PROVIDER=g in .env to force Gemini on every
# call, bypassing the auto-router. Leave unset to use auto-routing as normal.
PROVIDER: str | None = os.getenv("LLM_PROVIDER") or None

# Hardcoded fallback chain used when the gateway's /v1/routers is unreachable.
# Overridable via LLM_PROVIDER_FALLBACK env var.
_FALLBACK_CHAIN: list[str] = [
    p.strip()
    for p in os.getenv("LLM_PROVIDER_FALLBACK", "g,gr,c,n").split(",")
    if p.strip()
]

# HTTP status codes that mean "this provider failed, try the next one".
_RETRYABLE_CODES = {404, 502, 503}

# Cache for the gateway's TIER_TO_ORDER so we only fetch it once per process.
_tier_order_cache: list[str] | None = None


def _tier_provider_order(tier: str = "LARGE") -> list[str]:
    """Return the provider order for *tier* from the gateway's /v1/routers.

    Fetched once per process and cached. Falls back to _FALLBACK_CHAIN if the
    gateway is unreachable or the tier key is missing.
    """
    global _tier_order_cache
    if _tier_order_cache is None:
        try:
            resp = httpx.get(f"{GATEWAY_URL}/v1/routers", timeout=3.0)
            order = resp.json().get("tier_to_order", {}).get(tier, [])
            if order:
                _tier_order_cache = order
        except Exception:
            pass
    return _tier_order_cache or _FALLBACK_CHAIN


def _is_up() -> bool:
    try:
        httpx.get(f"{GATEWAY_URL}/v1/routers", timeout=2.0)
        return True
    except Exception:
        return False


def ensure_gateway() -> None:
    """Start V7 if it is not already running. Idempotent."""
    if _is_up():
        return
    if not GATEWAY_V7_DIR.exists():
        raise RuntimeError(
            f"Gateway V7 directory not found at {GATEWAY_V7_DIR}. "
            "Build llm_gatewayV7 (Session 7 prerequisite) before running S7 code."
        )
    print(f"[gateway] launching llm_gatewayV7 from {GATEWAY_V7_DIR}")
    subprocess.Popen(
        ["uv", "run", "main.py"],
        cwd=str(GATEWAY_V7_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(45):
        time.sleep(1)
        if _is_up():
            print(f"[gateway] up on {GATEWAY_URL}")
            return
    raise RuntimeError(f"Gateway V7 failed to start within 45s. Check {GATEWAY_V7_DIR}")


# Load V7's client.py without polluting sys.path. The gateway dir has its
# own `schemas.py`, which would shadow ours if we put it on the path.
import importlib.util as _importlib_util

_client_path = GATEWAY_V7_DIR / "client.py"
if _client_path.exists():
    _spec = _importlib_util.spec_from_file_location("llm_gatewayV7_client", _client_path)
    _mod = _importlib_util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    LLM = _mod.LLM
else:
    LLM = None  # populated once V7 is built; importers should ensure_gateway() first


def embed(text: str, task_type: str = "retrieval_document") -> dict:
    """Compute an embedding for `text` via the gateway's V7 embed endpoint.

    Returns the full response dict: `{embedding, dim, model, provider,
    latency_ms, ...}`. The chosen embedding model is fixed at the gateway
    level. Changing it invalidates every FAISS index built against the old
    vectors, so callers should treat the model as a project-level constant.
    """
    ensure_gateway()
    if LLM is None:
        raise RuntimeError(
            "Gateway V7 client unavailable. Confirm llm_gatewayV7/client.py exists."
        )
    return LLM().embed(text, task_type=task_type)


def chat_with_fallback(**kwargs) -> dict:
    """LLM().chat() with tier-aware provider fallback.

    Builds the fallback chain from the gateway's TIER_TO_ORDER (LARGE tier,
    since all agent calls use structured output). PROVIDER env var leads the
    chain when set. Falls back to _FALLBACK_CHAIN if the gateway is unreachable.
    Always pins a provider explicitly so the HUGE-token classifier is bypassed.
    Retries on 404 (model unavailable), 502 (upstream error), 503 (overloaded).
    """
    tier_order = _tier_provider_order("LARGE")

    if PROVIDER:
        chain = [PROVIDER] + [p for p in tier_order if p != PROVIDER]
    else:
        chain = list(tier_order)

    last_err: Exception = RuntimeError("no providers in fallback chain")
    for provider in chain:
        try:
            return LLM().chat(provider=provider, **kwargs)
        except httpx.HTTPStatusError as e:
            if e.response.status_code in _RETRYABLE_CODES:
                print(f"[gateway] {provider} → {e.response.status_code}, trying next in chain")
                last_err = e
                continue
            raise
    raise last_err


__all__ = ["ensure_gateway", "LLM", "PROVIDER", "chat_with_fallback", "GATEWAY_URL", "GATEWAY_V7_DIR", "embed"]
