# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

"""Traces of the LLM calls in Langfuse (LANGFUSE_ENABLED). LiteLLM sends each call itself (its `langfuse_otel`
callback); this module checks the keys, turns the callback on and groups the calls of a video in one session."""

import logging
import os

from aiasn.settings import LangfuseSettings

log = logging.getLogger(__name__)
_session: str | None = None


def init_langfuse(cfg: LangfuseSettings, session: str | None = None) -> bool:
    """Send LiteLLM's calls to Langfuse, under `session`, if it is enabled and its keys are valid; True if so.
    With wrong keys or the server down it only warns: the video is analysed all the same, without traces."""
    global _session
    if not cfg.enabled:
        log.info("Langfuse disabled (LANGFUSE_ENABLED=false)")
        return False
    import litellm
    from langfuse import Langfuse

    secret = cfg.secret_key.get_secret_value()
    # only to check the keys: tracing off, so that it does not set up OpenTelemetry next to LiteLLM's
    client = Langfuse(public_key=cfg.public_key, secret_key=secret, base_url=cfg.base_url, tracing_enabled=False)
    try:
        ok = client.auth_check()
    except Exception as e:   # server unreachable, wrong host...
        log.debug("Langfuse auth check failed: %r", e)
        ok = False
    if not ok:
        log.warning("Langfuse: authentication failed at %s. Check LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY and "
                    "LANGFUSE_BASE_URL in .env; going on without traces", cfg.base_url)
        return False
    # what LiteLLM's callback reads (.env values are not in the environment when running outside Docker)
    os.environ.update(LANGFUSE_PUBLIC_KEY=cfg.public_key, LANGFUSE_SECRET_KEY=secret, LANGFUSE_OTEL_HOST=cfg.base_url)
    if "langfuse_otel" not in litellm.callbacks:
        litellm.callbacks.append("langfuse_otel")
    _session = session
    log.info("Langfuse: tracing the LLM calls at %s", cfg.base_url)
    return True


def metadata(name: str) -> dict:
    """Langfuse fields of a LiteLLM call: its name and the session (video) it belongs to."""
    return {"generation_name": name} | ({"session_id": _session} if _session else {})


def flush() -> None:
    """Send the traces still pending before the process exits."""
    try:
        from opentelemetry import trace
    except ImportError:
        return
    provider = trace.get_tracer_provider()
    if hasattr(provider, "force_flush"):
        provider.force_flush()
