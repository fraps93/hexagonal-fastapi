"""Inbound port (primary port) for note creation.

Defines the contract that primary adapters (e.g. the HTTP router) use to
drive the application.  The concrete implementation lives in
``core.use_cases.create_note``; this interface ensures the adapter layer
depends on an abstraction, not on the implementation class.
"""

from abc import ABC, abstractmethod

from core.models.note import Note


class CreateNotePort(ABC):
    """Primary port exposing the note-creation capability to driving adapters.

    Any class that wants to be injectable as the note-creation use-case must
    implement this interface.  This keeps the inbound adapter (FastAPI router)
    fully decoupled from the concrete ``CreateNote`` class.
    """

    @abstractmethod
    def execute(self, prompt: str) -> Note:
        """Generate a note from a prompt and persist it.

        Args:
            prompt (str): Non-empty input text for the generator.

        Returns:
            Note: The newly created and persisted note.
        """
        ...
