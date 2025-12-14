import xml.etree.ElementTree as ET

import httpx

from .base import ResearchItem, ResearchSource


class ArxivSource(ResearchSource):
    """Research source that fetches papers from arXiv API.

    arXiv provides free access to scientific papers. Their API returns
    Atom XML feeds that we parse into ResearchItem objects.

    API docs: https://info.arxiv.org/help/api/basics.html
    """

    BASE_URL = "https://export.arxiv.org/api/query"

    # XML namespaces used in arXiv's Atom feed
    NAMESPACES = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
    }

    @property
    def source_type(self) -> str:
        return "arxiv"

    async def search(self, query: str, max_results: int = 5) -> list[ResearchItem]:
        """Search arXiv for papers matching the query.

        Args:
            query: Search terms (searches title, abstract, authors)
            max_results: Maximum papers to return (default 5)

        Returns:
            List of ResearchItem objects with paper details
        """
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending",
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(self.BASE_URL, params=params)
            response.raise_for_status()

        return self._parse_response(response.text)

    def _parse_response(self, xml_text: str) -> list[ResearchItem]:
        """Parse arXiv Atom XML response into ResearchItem objects."""
        root = ET.fromstring(xml_text)
        items = []

        for entry in root.findall("atom:entry", self.NAMESPACES):
            title = entry.find("atom:title", self.NAMESPACES)
            summary = entry.find("atom:summary", self.NAMESPACES)
            link = entry.find("atom:id", self.NAMESPACES)
            published = entry.find("atom:published", self.NAMESPACES)

            # Get all authors
            authors = [
                author.find("atom:name", self.NAMESPACES).text
                for author in entry.findall("atom:author", self.NAMESPACES)
                if author.find("atom:name", self.NAMESPACES) is not None
            ]

            items.append(
                ResearchItem(
                    title=self._clean_text(title.text) if title is not None else "",
                    summary=self._clean_text(summary.text) if summary is not None else "",
                    url=link.text if link is not None else "",
                    source_type=self.source_type,
                    authors=authors,
                    published_date=published.text[:10] if published is not None else None,
                )
            )

        return items

    def _clean_text(self, text: str) -> str:
        """Remove extra whitespace from text."""
        return " ".join(text.split())
