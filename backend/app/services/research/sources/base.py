from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ResearchItem:
    """A single piece of research content from any source."""

    title: str
    summary: str
    url: str
    source_type: str  # e.g., "arxiv", "rss", "docs"
    authors: list[str] | None = None
    published_date: str | None = None


class ResearchSource(ABC):
    """Abstract base class for all research sources.

    This is the Strategy Pattern - each source (arXiv, RSS, docs)
    implements this interface, so the orchestrator can treat them uniformly.
    """

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Identifier for this source type (e.g., 'arxiv', 'rss')."""
        pass

    @abstractmethod
    async def search(self, query: str, max_results: int = 5) -> list[ResearchItem]:
        """Search this source for content matching the query.

        Args:
            query: Search terms (e.g., "machine learning transformers")
            max_results: Maximum number of results to return

        Returns:
            List of ResearchItem objects
        """
        pass
