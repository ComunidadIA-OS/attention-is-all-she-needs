# SPDX-FileCopyrightText: 2026 Equipo 1: Attention Is All She Needs (Alba Camiña García, Pilar de la Fuente Diez, Rocío Jiménez Villén)
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import sys
import types

import pytest

from aiasn import langfuse_client
from aiasn.settings import LangfuseSettings

ON = dict(enabled=True, public_key="pk-lf-test", secret_key="sk-lf-test", base_url="http://langfuse.test")


@pytest.fixture
def fakes(monkeypatch):
    """Fake litellm and langfuse modules: no server, no SDK needed. `auth` is what auth_check answers."""
    litellm = types.SimpleNamespace(callbacks=[])
    state = {"auth": True, "clients": []}

    class Langfuse:
        def __init__(self, **kwargs):
            state["clients"].append(kwargs)

        def auth_check(self):
            if isinstance(state["auth"], Exception):
                raise state["auth"]
            return state["auth"]

    monkeypatch.setitem(sys.modules, "litellm", litellm)
    monkeypatch.setitem(sys.modules, "langfuse", types.SimpleNamespace(Langfuse=Langfuse))
    monkeypatch.setattr(langfuse_client, "_session", None)
    for var in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_OTEL_HOST"):   # restored as they were
        monkeypatch.setenv(var, "")
        monkeypatch.delenv(var)
    return litellm, state


def test_disabled_loads_nothing(monkeypatch, caplog):
    monkeypatch.setitem(sys.modules, "langfuse", None)   # importing it would fail
    with caplog.at_level(logging.INFO):
        assert not langfuse_client.init_langfuse(LangfuseSettings(enabled=False))
    assert "disabled" in caplog.text
    assert langfuse_client.metadata("Topics") == {"generation_name": "Topics"}


@pytest.mark.parametrize("auth", [False, ConnectionError("down")])
def test_failed_auth_warns_and_goes_on_without_traces(fakes, caplog, auth):
    litellm, state = fakes
    state["auth"] = auth
    assert not langfuse_client.init_langfuse(LangfuseSettings(**ON), session="v1")
    assert "LANGFUSE_PUBLIC_KEY" in caplog.text and caplog.records[-1].levelno == logging.WARNING
    assert litellm.callbacks == [] and langfuse_client.metadata("Topics") == {"generation_name": "Topics"}


def test_valid_keys_turn_on_litellm_callback_with_the_session(fakes):
    litellm, state = fakes
    assert langfuse_client.init_langfuse(LangfuseSettings(**ON), session="v1")
    assert state["clients"][0]["tracing_enabled"] is False   # the SDK only checks the keys
    assert litellm.callbacks == ["langfuse_otel"]
    assert os.environ["LANGFUSE_OTEL_HOST"] == "http://langfuse.test"
    assert langfuse_client.metadata("Topics") == {"generation_name": "Topics", "session_id": "v1"}
    langfuse_client.init_langfuse(LangfuseSettings(**ON), session="v1")
    assert litellm.callbacks == ["langfuse_otel"]   # not twice
