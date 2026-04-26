"""Outbound port (secondary port) for note persistence.

Any infrastructure adapter that stores notes must implement this ABC.
The core never imports concrete repository classes; it only depends on
this interface.
"""

from abc import ABC, abstractmethod

from core.models.note import Note


class RepositoryPort(ABC):
    """Abstract repository that defines the persistence contract for notes.

    Concrete adapters (e.g. ``InMemoryRepository``, a SQL adapter, …) must
    implement every method declared here.
    """

    @abstractmethod
    def save(self, note: Note) -> Note:
        """Persist a note and return the saved instance.

        Args:
            note (Note): The note to persist.

        Returns:
            Note: The persisted note (may be enriched by the adapter).
        """
        ...

    @abstractmethod
    def find_by_id(self, note_id: str) -> Note | None:
        """Retrieve a note by its unique identifier.

        Args:
            note_id (str): UUID of the note to look up.

        Returns:
            Optional[Note]: The matching note, or ``None`` if not found.
        """
        ...

    @abstractmethod
    def find_all(self) -> list[Note]:
        """Retrieve every stored note.

        Returns:
            List[Note]: All notes in the store (may be empty).
        """
        ...

    @abstractmethod
    def delete(self, note_id: str) -> None:
        """Remove a note from the store.

        Callers must verify existence before calling this method; the
        adapter is not required to raise when the ID is absent.

        Args:
            note_id (str): UUID of the note to delete.
        """
        ...
