"""Shared pytest fixtures for the Hexagonal Fastapi test suite."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Return a FastAPI ``TestClient`` bound to the application.

    Scoped to the session so the app is created only once, matching the
    behaviour of a real server.

    Returns:
        TestClient: HTTP test client for the FastAPI app.
    """
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_repository() -> None:
    """Reset the ``repository`` singleton before every test.

    Resetting the ``providers.Singleton`` forces ``dependency_injector``
    to create a fresh ``InMemoryRepository`` on the next resolution,
    giving each test a clean, empty store.
    """
    app.container.repository.reset()  # type: ignore[attr-defined]
