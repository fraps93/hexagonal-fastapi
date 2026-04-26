"""Echo generator adapter.

A trivial ``GeneratorPort`` implementation that reflects the prompt back
prefixed with ``"Echo: "``.  Useful for local development and unit tests
where no real LLM is available.
"""

from core.ports.outbound.generator_port import GeneratorPort


class EchoGenerator(GeneratorPort):
    """Generator adapter that echoes the prompt unchanged.

    This adapter is the default choice wired in ``Container``.  Swap it
    for ``ShoutingGenerator`` (or a real LLM adapter) in the container
    without touching any other file.
    """

    def generate(self, prompt: str) -> str:
        """Return the prompt prefixed with ``"Echo: "``.

        Args:
            prompt (str): Input text to echo.

        Returns:
            str: The string ``"Echo: " + prompt``.
        """
        return f"Echo: {prompt}"
