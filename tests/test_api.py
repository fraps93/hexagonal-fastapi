"""Integration tests for the notes HTTP API.

Each test exercises the full stack: FastAPI router → DI container →
use-case → adapters.  The ``reset_repository`` fixture (defined in
``conftest.py``) resets the in-memory store before every test so each
runs in isolation.

The final test demonstrates the DI container override capability:
the ``ShoutingGenerator`` is swapped in at runtime via
``container.generator.override()``, which is the ``dependency_injector``
mechanism for replacing a provider without modifying any other code.
"""

from dependency_injector import providers
from fastapi.testclient import TestClient

from adapters.outbound.generators.shouting_generator import ShoutingGenerator
from main import app

# ---------------------------------------------------------------------------
# POST /notes/
# ---------------------------------------------------------------------------


def test_create_note_returns_201_with_correct_shape(client: TestClient) -> None:
    """A valid prompt creates a note and returns HTTP 201 with all fields."""
    response = client.post("/notes/", json={"prompt": "hello"})

    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Echo: hello"
    assert data["id"]
    assert data["created_at"]


def test_create_note_empty_prompt_returns_422(client: TestClient) -> None:
    """An empty prompt string is rejected by Pydantic's ``min_length=1``."""
    response = client.post("/notes/", json={"prompt": ""})

    assert response.status_code == 422


def test_create_note_missing_prompt_returns_422(client: TestClient) -> None:
    """A request body without the ``prompt`` key is rejected."""
    response = client.post("/notes/", json={})

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# GET /notes/
# ---------------------------------------------------------------------------


def test_list_notes_returns_empty_list_on_fresh_store(client: TestClient) -> None:
    """Listing notes on an empty store returns an empty JSON array."""
    response = client.get("/notes/")

    assert response.status_code == 200
    assert response.json() == []


def test_list_notes_returns_all_created_notes(client: TestClient) -> None:
    """All notes created in a session are returned by the list endpoint."""
    client.post("/notes/", json={"prompt": "first"})
    client.post("/notes/", json={"prompt": "second"})

    response = client.get("/notes/")

    assert response.status_code == 200
    assert len(response.json()) == 2


# ---------------------------------------------------------------------------
# GET /notes/{note_id}
# ---------------------------------------------------------------------------


def test_get_note_by_id_returns_correct_note(client: TestClient) -> None:
    """A note can be retrieved by its ID after creation."""
    created = client.post("/notes/", json={"prompt": "get me"}).json()

    response = client.get(f"/notes/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["content"] == "Echo: get me"


def test_get_note_unknown_id_returns_404(client: TestClient) -> None:
    """Requesting a non-existent note ID returns HTTP 404."""
    response = client.get("/notes/does-not-exist")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DELETE /notes/{note_id}
# ---------------------------------------------------------------------------


def test_delete_note_returns_204_and_removes_it(client: TestClient) -> None:
    """Deleting a note returns HTTP 204 and makes it unretrievable."""
    created = client.post("/notes/", json={"prompt": "delete me"}).json()

    delete_response = client.delete(f"/notes/{created['id']}")
    get_response = client.get(f"/notes/{created['id']}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_delete_unknown_id_returns_404(client: TestClient) -> None:
    """Deleting a non-existent note ID returns HTTP 404."""
    response = client.delete("/notes/does-not-exist")

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# DI container override demonstration
# ---------------------------------------------------------------------------


def test_override_generator_with_shouting_adapter(client: TestClient) -> None:
    """Swapping the generator via the DI container changes API output.

    This is the core demonstration of dependency injection:
    ``container.generator.override()`` replaces the ``EchoGenerator``
    singleton with ``ShoutingGenerator`` for the duration of the
    ``with`` block.  No route, use-case, or repository code changes.
    """
    with app.container.generator.override(  # type: ignore[attr-defined]
        providers.Object(ShoutingGenerator())
    ):
        response = client.post("/notes/", json={"prompt": "hello"})

    assert response.status_code == 201
    assert response.json()["content"] == "HELLO!!!"
