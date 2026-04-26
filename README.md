# Hexagonal Fastapi Demo

A focused demonstration of **Hexagonal Architecture** (Ports & Adapters), **Dependency Injection**, **Pydantic v2**, and **FastAPI** in Python.

The domain is intentionally trivial (a simple note-creation service), so the architecture patterns are the story, not the business logic.

---

## What this repo demonstrates

### Hexagonal Architecture (Ports & Adapters)

The codebase is organised around Alistair Cockburn's original model: an inner hexagon (the application core) surrounded by adapters, communicating only through ports.

```
        [ HTTP client ]   [ Test suite ]
               │                │
               ▼                ▼
    ┌─────────────────────────────────────┐
    │         Inbound adapters            │  drives the core
    │      adapters/inbound/api/          │
    └──────────────┬──────────────────────┘
                   │ CreateNotePort (inbound port)
    ┌──────────────▼──────────────────────┐
    │            Core                     │
    │  models/  ports/  use_cases/        │
    └──────────────┬──────────────────────┘
                   │ GeneratorPort / RepositoryPort (outbound ports)
    ┌──────────────▼──────────────────────┐
    │        Outbound adapters            │  driven by the core
    │  adapters/outbound/generators/      │
    │  adapters/outbound/repositories/    │
    └─────────────────────────────────────┘
```

Ports are split by direction, a distinction absent in many demos but required by the original model:

| Port type | Path | Direction |
|---|---|---|
| **Inbound (primary)** | `core/ports/inbound/` | External actor → core |
| **Outbound (secondary)** | `core/ports/outbound/` | Core → infrastructure |

The same split applies to adapters:

| Adapter type | Path | Direction |
|---|---|---|
| **Inbound** | `adapters/inbound/api/` | HTTP → core |
| **Outbound** | `adapters/outbound/generators/` | Core → text generation |
| **Outbound** | `adapters/outbound/repositories/` | Core → persistence |

### The inbound port: closing the symmetry

The HTTP router does **not** import the `CreateNote` class directly.  It
depends on `CreateNotePort`, an ABC that `CreateNote` implements:

```python
# core/ports/inbound/create_note_port.py
class CreateNotePort(ABC):
    @abstractmethod
    def execute(self, prompt: str) -> Note: ...

# core/use_cases/create_note.py
class CreateNote(CreateNotePort):   # implements the inbound port
    ...

# adapters/inbound/api/routes.py
@inject
def create_note(
    body: CreateNoteRequest,
    use_case: CreateNotePort = Depends(Provide[Container.create_note_use_case]),
) -> NoteResponse:
    ...
```

This makes both sides of the hexagon symmetric: the inbound adapter depends
on an abstraction, exactly like the outbound adapters.

### Dependency Injection with `dependency-injector`

`src/container.py` is the single **composition root**: the only place where
concrete adapter classes are named.

```python
class Container(containers.DeclarativeContainer):
    settings             = providers.Singleton(Settings)
    repository           = providers.Singleton(InMemoryRepository)
    generator            = providers.Singleton(EchoGenerator)
    create_note_use_case = providers.Factory(CreateNote,
                                             generator=generator,
                                             repository=repository)
```

FastAPI endpoints receive their dependencies via `@inject` +
`Depends(Provide[Container.xxx])` the same pattern used in production
services:

```python
@router.post("/", status_code=201)
@inject
def create_note(
    body: CreateNoteRequest,
    use_case: CreateNotePort = Depends(Provide[Container.create_note_use_case]),
) -> NoteResponse:
    ...
```

**Swapping an adapter** requires changing a single line in `container.py`.
Every test, route, and use-case is unaffected:

```python
# Before
generator = providers.Singleton(EchoGenerator)

# After (nothing else changes)
generator = providers.Singleton(ShoutingGenerator)
```

### Pydantic v2

Request validation and response serialization live in
`adapters/inbound/api/schemas.py`, separate from routing logic:

```python
class CreateNoteRequest(BaseModel):
    prompt: str = Field(..., min_length=1)   # automatic 422 on empty string

class NoteResponse(BaseModel):
    id: str
    content: str
    created_at: datetime                     # serialized to ISO-8601 by Pydantic
```

The domain model (`Note`) is a plain `dataclass`. Pydantic is an
API-layer concern, not a domain concern.

### Testing strategy

Two complementary test suites:

| Suite | File | What it tests |
|---|---|---|
| **Unit** | `tests/test_create_note.py` | Core use-case in pure isolation, no HTTP, no container |
| **Integration** | `tests/test_api.py` | Full HTTP stack via `TestClient`; includes DI override demo |

The `reset_repository` fixture in `conftest.py` calls
`container.repository.reset()` before every test, giving each test a clean
in-memory store without restarting the app.

The DI override test demonstrates runtime adapter swapping:

```python
def test_override_generator_with_shouting_adapter(client):
    with app.container.generator.override(providers.Object(ShoutingGenerator())):
        response = client.post("/notes/", json={"prompt": "hello"})
    assert response.json()["content"] == "HELLO!!!"
```

---

## Project structure

```
hexagonal-fastapi/
├── main.py                                   # Entry point: creates app, wires container
├── Dockerfile
├── pyproject.toml
└── src/
    ├── config.py                             # App settings via pydantic-settings (env vars)
    ├── container.py                          # Composition root (DI)
    ├── core/
    │   ├── models/
    │   │   └── note.py                       # Domain entity (pure dataclass)
    │   ├── ports/
    │   │   ├── inbound/
    │   │   │   └── create_note_port.py       # Primary port (what the core exposes)
    │   │   └── outbound/
    │   │       ├── generator_port.py         # Secondary port: text generation
    │   │       └── repository_port.py        # Secondary port: persistence
    │   └── use_cases/
    │       └── create_note.py                # Implements CreateNotePort
    └── adapters/
        ├── inbound/
        │   └── api/
        │       ├── routes.py                 # FastAPI router (depends on CreateNotePort)
        │       └── schemas.py                # Pydantic request/response models
        └── outbound/
            ├── generators/
            │   ├── echo_generator.py         # Default adapter (reflects prompt)
            │   └── shouting_generator.py     # Alternate adapter (uppercase)
            └── repositories/
                └── in_memory_repository.py   # Implements RepositoryPort
```

---

## API

| Method | Path | Description |
|---|---|---|
| `POST` | `/notes/` | Create a note from a prompt |
| `GET` | `/notes/` | List all notes |
| `GET` | `/notes/{id}` | Get a note by ID |
| `DELETE` | `/notes/{id}` | Delete a note |

Interactive docs available at `http://localhost:8000/docs` once the server is running.

---

## Run locally

```bash
pip install -e ".[dev]"
python main.py
```

## Run with Docker

```bash
docker build -t hex-arch-demo .
docker run -p 8000:8000 hex-arch-demo
```

## Run tests

```bash
pytest -v
```

---

## Technology stack

| Technology | Version | Role |
|---|---|---|
| [FastAPI](https://fastapi.tiangolo.com) | ≥ 0.115 | HTTP framework and OpenAPI generation |
| [Pydantic v2](https://docs.pydantic.dev/latest/) | ≥ 2.0 | Request validation and response serialization |
| [dependency-injector](https://python-dependency-injector.ets-labs.org) | ≥ 4.41 | Declarative DI container with `Singleton` / `Factory` providers |
| [Uvicorn](https://www.uvicorn.org) | ≥ 0.32 | ASGI server |
| [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) | ≥ 2.0 | App configuration from env vars |
| [pytest](https://pytest.org) | ≥ 8.0 | Test framework |
| [httpx](https://www.python-httpx.org) | ≥ 0.27 | HTTP client powering FastAPI's `TestClient` |
