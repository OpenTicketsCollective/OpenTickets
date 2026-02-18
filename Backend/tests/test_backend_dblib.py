from __future__ import annotations

import importlib

import pytest


@pytest.fixture
def db_module():
    import Backend_dblib as module

    return importlib.reload(module)


def test_db_heartbeat(db_module):
    assert db_module.test_connection() is True
