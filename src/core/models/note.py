"""Domain model for a note.

This module contains the ``Note`` dataclass, which is a pure domain object
with no dependency on any framework or infrastructure library.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Note:
    """Immutable domain entity representing a generated note.

    Attributes:
        content: The generated text content of the note.
        id: Unique identifier (UUID4 string), auto-assigned at creation.
        created_at: UTC-aware timestamp of when the note was created.
    """

    content: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
