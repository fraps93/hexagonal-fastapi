"""FastAPI router for the notes resource.

All dependencies are resolved by the DI container via `@inject` +
`Depends(Provide[Container.<provider>])`. The router depends on the
`CreateNotePort` inbound interface, never on the concrete `CreateNote`
class, keeping the adapter fully decoupled from the implementation.
"""

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException

from adapters.inbound.api.schemas import CreateNoteRequest, NoteResponse
from container import Container
from core.ports.inbound.create_note_port import CreateNotePort
from core.ports.outbound.repository_port import RepositoryPort

router = APIRouter(prefix="/notes", tags=["notes"])


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/", response_model=NoteResponse, status_code=201)
@inject
def create_note(
    body: CreateNoteRequest,
    use_case: CreateNotePort = Depends(Provide[Container.create_note_use_case]),
) -> NoteResponse:
    """Create a new note from a prompt.

    Args:
        body (CreateNoteRequest): Request payload containing the prompt.
        use_case (CreateNotePort): Injected use-case (inbound port).

    Returns:
        NoteResponse: The persisted note with its generated ID and content.
    """
    note = use_case.execute(body.prompt)
    return NoteResponse(id=note.id, content=note.content, created_at=note.created_at)


@router.get("/", response_model=list[NoteResponse])
@inject
def list_notes(
    repository: RepositoryPort = Depends(Provide[Container.repository]),
) -> list[NoteResponse]:
    """Return all stored notes.

    Args:
        repository (RepositoryPort): Injected repository adapter.

    Returns:
        list[NoteResponse]: All notes currently in the store.
    """
    return [
        NoteResponse(id=n.id, content=n.content, created_at=n.created_at)
        for n in repository.find_all()
    ]


@router.get("/{note_id}", response_model=NoteResponse)
@inject
def get_note(
    note_id: str,
    repository: RepositoryPort = Depends(Provide[Container.repository]),
) -> NoteResponse:
    """Return a single note by ID.

    Args:
        note_id (str): UUID of the note to retrieve.
        repository (RepositoryPort): Injected repository adapter.

    Returns:
        NoteResponse: The matching note.

    Raises:
        HTTPException: 404 if no note with `note_id` exists.
    """
    note = repository.find_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    return NoteResponse(id=note.id, content=note.content, created_at=note.created_at)


@router.delete("/{note_id}", status_code=204)
@inject
def delete_note(
    note_id: str,
    repository: RepositoryPort = Depends(Provide[Container.repository]),
) -> None:
    """Delete a note by ID.

    Args:
        note_id (str): UUID of the note to delete.
        repository (RepositoryPort): Injected repository adapter.

    Raises:
        HTTPException: 404 if no note with `note_id` exists.
    """
    if not repository.find_by_id(note_id):
        raise HTTPException(status_code=404, detail="Note not found.")
    repository.delete(note_id)
