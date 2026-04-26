"""Pydantic schemas for the notes API adapter.

Request and response models live here, separate from the routing logic,
so that route definitions stay lean and schemas can be reused or evolved
independently.  These models are pure API concerns and must not leak into
the core layer.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class CreateNoteRequest(BaseModel):
    """Validated request body for note creation.

    Attributes:
        prompt: Non-empty text forwarded to the generator adapter.
    """

    prompt: str = Field(..., min_length=1, description="Non-empty prompt text.")


class NoteResponse(BaseModel):
    """API representation of a persisted note.

    Attributes:
        id: UUID string assigned at creation time.
        content: Generated text content.
        created_at: UTC-aware timestamp of creation.
    """

    id: str
    content: str
    created_at: datetime
