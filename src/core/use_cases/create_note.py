"""Use-case: create a note from a prompt.

This module contains the single application service ``CreateNote``, which
orchestrates text generation and persistence.  It depends exclusively on the
port abstractions, never on concrete adapter classes.
"""

from core.models.note import Note
from core.ports.inbound.create_note_port import CreateNotePort
from core.ports.outbound.generator_port import GeneratorPort
from core.ports.outbound.repository_port import RepositoryPort


class CreateNote(CreateNotePort):
    """Application service that generates a note and persists it.

    Implements the `CreateNotePort` inbound interface so that primary
    adapters (e.g. the HTTP router) depend only on the abstraction.

    Depends on two outbound ports:

    - `GeneratorPort`: produces text content from a prompt.
    - `RepositoryPort`: persists and retrieves notes.

    Because the class only imports port abstractions, it works unchanged
    regardless of which concrete adapters are wired by the DI container.

    Attributes:
        generator: Adapter that produces text from a prompt.
        repository: Adapter that persists and retrieves notes.
    """

    def __init__(
        self,
        generator: GeneratorPort,
        repository: RepositoryPort,
    ) -> None:
        """Initialise the use-case with its required port adapters.

        Args:
            generator (GeneratorPort): Text-generation adapter.
            repository (RepositoryPort): Note-persistence adapter.
        """
        self.generator = generator
        self.repository = repository

    def execute(self, prompt: str) -> Note:
        """Run the use-case: generate content and save the note.

        Args:
            prompt (str): Input text forwarded to the generator.

        Returns:
            Note: The newly created and persisted note.
        """
        content = self.generator.generate(prompt)
        note = Note(content=content)
        return self.repository.save(note)
