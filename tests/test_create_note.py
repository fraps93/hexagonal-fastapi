"""Unit tests for the ``CreateNote`` use-case.

These tests exercise the core layer in complete isolation: no HTTP
stack, no DI container.  Each test wires adapters directly, demonstrating
that the use-case is agnostic to which concrete adapter is used.
"""

from adapters.outbound.generators.echo_generator import EchoGenerator
from adapters.outbound.generators.shouting_generator import ShoutingGenerator
from adapters.outbound.repositories.in_memory_repository import InMemoryRepository
from core.use_cases.create_note import CreateNote


def _make_use_case(generator) -> CreateNote:
    """Construct a ``CreateNote`` use-case with an ``InMemoryRepository``.

    Args:
        generator: Any ``GeneratorPort`` implementation to inject.

    Returns:
        CreateNote: A fully wired use-case ready for execution.
    """
    return CreateNote(generator=generator, repository=InMemoryRepository())


def test_echo_generator_produces_expected_content() -> None:
    """EchoGenerator prefixes the prompt with ``"Echo: "``."""
    note = _make_use_case(EchoGenerator()).execute("hello world")

    assert note.content == "Echo: hello world"
    assert note.id is not None


def test_shouting_generator_uppercases_and_appends_bangs() -> None:
    """ShoutingGenerator uppercases the prompt and appends ``"!!!"``."""
    note = _make_use_case(ShoutingGenerator()).execute("hello world")

    assert note.content == "HELLO WORLD!!!"


def test_swapping_adapter_leaves_use_case_class_unchanged() -> None:
    """The use-case class is identical regardless of the injected generator.

    This is the key hexagonal-architecture assertion: the core does not
    know, and does not care, which concrete adapter it receives.
    """
    for generator in (EchoGenerator(), ShoutingGenerator()):
        note = _make_use_case(generator).execute("test")
        assert note.id
        assert note.content


def test_repository_persists_and_retrieves_a_note() -> None:
    """A saved note can be retrieved by ID from the same repository."""
    repo = InMemoryRepository()
    use_case = CreateNote(generator=EchoGenerator(), repository=repo)

    note = use_case.execute("persist me")
    found = repo.find_by_id(note.id)

    assert found is not None
    assert found.content == note.content


def test_repository_find_all_returns_all_saved_notes() -> None:
    """``find_all`` reflects every note created through the use-case."""
    repo = InMemoryRepository()
    use_case = CreateNote(generator=EchoGenerator(), repository=repo)

    use_case.execute("first")
    use_case.execute("second")

    assert len(repo.find_all()) == 2


def test_repository_delete_removes_note() -> None:
    """``delete`` removes the note so it is no longer findable."""
    repo = InMemoryRepository()
    use_case = CreateNote(generator=EchoGenerator(), repository=repo)

    note = use_case.execute("delete me")
    assert repo.find_by_id(note.id) is not None

    repo.delete(note.id)

    assert repo.find_by_id(note.id) is None
    assert len(repo.find_all()) == 0
