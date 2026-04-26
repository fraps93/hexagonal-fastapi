"""In-memory repository adapter.

Implements ``RepositoryPort`` using a plain Python dictionary.  No database
or external infrastructure is required, making this adapter ideal for
local development, demos, and unit tests.
"""


from core.models.note import Note
from core.ports.outbound.repository_port import RepositoryPort


class InMemoryRepository(RepositoryPort):
    """``RepositoryPort`` implementation backed by an in-process dictionary.

    All data is lost when the process exits.  This is intentional for a
    demo; a real application would swap this for a SQL or NoSQL adapter
    in the DI container without changing any other code.

    Attributes:
        _store: Internal mapping of note ID → Note.
    """

    def __init__(self) -> None:
        """Initialise an empty in-memory store."""
        self._store: dict[str, Note] = {}

    def save(self, note: Note) -> Note:
        """Persist a note in the internal dictionary.

        Args:
            note (Note): The note to store.

        Returns:
            Note: The same note instance (unchanged).
        """
        self._store[note.id] = note
        return note

    def find_by_id(self, note_id: str) -> Note | None:
        """Look up a note by its UUID.

        Args:
            note_id (str): UUID of the note to retrieve.

        Returns:
            Optional[Note]: The note if found, otherwise ``None``.
        """
        return self._store.get(note_id)

    def find_all(self) -> list[Note]:
        """Return all stored notes.

        Returns:
            List[Note]: Snapshot of all notes in insertion order.
        """
        return list(self._store.values())

    def delete(self, note_id: str) -> None:
        """Remove a note from the store.

        A missing ``note_id`` is silently ignored; callers should verify
        existence beforehand if they need to distinguish that case.

        Args:
            note_id (str): UUID of the note to delete.
        """
        self._store.pop(note_id, None)
