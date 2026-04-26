"""Outbound port (secondary port) for text generation.

Any adapter that produces text content must implement this ABC.
Concrete examples include `EchoGenerator`, `ShoutingGenerator`, or
a real LLM-backed adapter, all interchangeable without touching the core.
"""

from abc import ABC, abstractmethod


class GeneratorPort(ABC):
    """Abstract generator that defines the text-generation contract.

    Concrete adapters must implement `generate`.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate text content from a prompt.

        Args:
            prompt (str): Input text to base the generation on.

        Returns:
            str: Generated text content.
        """
        ...
