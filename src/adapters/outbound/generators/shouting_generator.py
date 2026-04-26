"""Shouting generator adapter.

An alternative ``GeneratorPort`` implementation that uppercases the prompt
and appends ``"!!!"``.  Its only purpose is to demonstrate that swapping an
adapter in the DI container changes behaviour without modifying the core.
"""

from core.ports.outbound.generator_port import GeneratorPort


class ShoutingGenerator(GeneratorPort):
    """Generator adapter that uppercases the prompt and appends ``"!!!"``.

    Wire this class in place of ``EchoGenerator`` inside ``Container`` to
    instantly change the generation behaviour for the entire application
    without touching any core or route code.
    """

    def generate(self, prompt: str) -> str:
        """Return the prompt uppercased with ``"!!!"`` appended.

        Args:
            prompt (str): Input text to transform.

        Returns:
            str: ``prompt.upper() + "!!!"``.
        """
        return prompt.upper() + "!!!"
