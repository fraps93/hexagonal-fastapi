"""Dependency injection container, the single composition root of the application.

This is the only module where the core knows about concrete adapter
implementations. Everything else depends on abstractions (ports).
"""

from dependency_injector import containers, providers

from adapters.outbound.generators.echo_generator import EchoGenerator
from adapters.outbound.repositories.in_memory_repository import InMemoryRepository
from config import Settings
from core.use_cases.create_note import CreateNote


class Container(containers.DeclarativeContainer):
    """DI container for the Hexagonal Fastapi application.

    Providers declared here:

    - `settings`: Singleton, single Settings instance for the whole process.
    - `repository`: Singleton, one shared in-memory store per process.
    - `generator`: Singleton, stateless, safe to reuse.
    - `create_note_use_case`: Factory, new instance per injection point,
      mirroring real-world patterns where use-cases may carry request-scoped
      state.

    To swap an adapter, change the class passed to the provider here.
    No other file needs to change.

    Attributes:
        wiring_config: Auto-wire target modules so `@inject` resolves providers.
        settings: Application configuration (env vars).
        repository: Persistent in-memory note store.
        generator: Text generation strategy.
        create_note_use_case: Factory for the CreateNote use-case.
    """

    wiring_config = containers.WiringConfiguration(
        modules=["adapters.inbound.api.routes"],
    )

    settings: providers.Provider = providers.Singleton(Settings)

    repository: providers.Provider = providers.Singleton(InMemoryRepository)

    generator: providers.Provider = providers.Singleton(EchoGenerator)

    create_note_use_case: providers.Provider = providers.Factory(
        CreateNote,
        generator=generator,
        repository=repository,
    )
