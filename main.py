"""hexagonal-fastapi application entry point.

Creates the FastAPI app, wires the DI container, registers the router,
and starts the Uvicorn server when run directly.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import uvicorn
from fastapi import FastAPI

from adapters.inbound.api.routes import router
from container import Container


def create_app() -> FastAPI:
    """Create, configure, and return the FastAPI application.

    Responsibilities:

    - Instantiate the DI container.
    - Wire the container to all modules that use ``@inject``.
    - Register API routers.

    Returns:
        FastAPI: The fully configured application instance.
    """
    container = Container()
    container.wire(modules=["adapters.inbound.api.routes"])
    cfg = container.settings()

    app = FastAPI(
        title=cfg.app_name,
        description=cfg.app_description,
        version=cfg.app_version,
        debug=cfg.debug,
    )
    app.container = container  # type: ignore[attr-defined]
    app.include_router(router)
    return app


app = create_app()

if __name__ == "__main__":
    cfg = app.container.settings()  # type: ignore[attr-defined]
    uvicorn.run(
        "main:app",
        host=cfg.host,
        port=cfg.port,
        reload=cfg.reload,
        log_level=cfg.log_level,
    )
