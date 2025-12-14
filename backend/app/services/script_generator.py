"""Script Generator Service (Agentic)

This module generates podcast scripts using Claude with tool use.
Claude acts as an agent that can search arXiv for research papers,
then synthesizes the findings into an engaging podcast script.

Flow:
    1. Receives a topic
    2. Claude decides what to search for using the arxiv_search tool
    3. Claude can make multiple searches if needed
    4. Claude synthesizes all research into a podcast script
    5. Returns the final script text

Usage:
    from app.services.script_generator import generate_script

    script = await generate_script("machine learning", duration_minutes=5)

Key Concepts:
    - Tool Use: Claude can call tools (like arxiv_search) during generation
    - Agentic Loop: We keep calling Claude until it stops requesting tools
    - The LLM decides what queries to run, not us

Dependencies:
    - anthropic: Official Anthropic Python SDK (with tool use support)
    - app.core.config: For API key and settings
    - app.services.research.sources.arxiv: ArxivSource for actual searches
"""

import asyncio
import json

import anthropic

from app.core.config import settings
from app.services.research.sources.arxiv import ArxivSource


# Tool definition for arXiv search
# This tells Claude what the tool does and what parameters it accepts
ARXIV_SEARCH_TOOL = {
    "name": "arxiv_search",
    "description": (
        "Search arXiv for academic papers on a topic. "
        "Returns paper titles, authors, summaries, and URLs. "
        "Use this to find recent research on the podcast topic. "
        "You can call this multiple times with different queries to explore different angles."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query for arXiv (e.g., 'transformer neural networks', 'reinforcement learning robotics')",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of papers to return (default: 5, max: 10)",
                "default": 5,
            },
        },
        "required": ["query"],
    },
}


# System prompt for the agentic script generator
SYSTEM_PROMPT = """You are a podcast script writer with access to arXiv for research.

Your task:
1. Use the arxiv_search tool to find relevant recent research on the topic
2. You may search multiple times with different queries to get comprehensive coverage
3. Once you have enough research, write an engaging podcast script

Your scripts should:
- Be conversational and engaging, as if explaining to a curious friend
- Break down complex concepts into digestible pieces
- Include smooth transitions between topics
- Be approximately {duration_minutes} minutes when read aloud (~150 words per minute)
- NOT include speaker labels, timestamps, or production notes
- Flow naturally as a monologue

Target length: approximately {word_count} words.

When you're ready to write the script, just write it directly (don't use any tools)."""


async def _execute_arxiv_search(query: str, max_results: int = 5) -> str:
    """Execute an arXiv search and return formatted results.

    This is called when Claude uses the arxiv_search tool.

    Args:
        query: Search query string
        max_results: Maximum papers to return (capped at 10)

    Returns:
        Formatted string of search results for Claude to read
    """
    # Cap max_results to prevent abuse
    max_results = min(max_results, 10)

    source = ArxivSource()
    items = await source.search(query, max_results=max_results)

    if not items:
        return f"No results found for query: {query}"

    # Format results for Claude
    results = []
    for i, item in enumerate(items, 1):
        authors = ", ".join(item.authors[:3]) if item.authors else "Unknown"
        results.append(
            f"[{i}] {item.title}\n"
            f"    Authors: {authors}\n"
            f"    Date: {item.published_date or 'Unknown'}\n"
            f"    Summary: {item.summary}\n"
            f"    URL: {item.url}"
        )

    return f"Found {len(items)} papers for '{query}':\n\n" + "\n\n".join(results)


async def _process_tool_call(tool_name: str, tool_input: dict) -> str:
    """Process a tool call from Claude and return the result.

    Args:
        tool_name: Name of the tool Claude wants to use
        tool_input: Parameters for the tool

    Returns:
        Tool result as a string
    """
    if tool_name == "arxiv_search":
        return await _execute_arxiv_search(
            query=tool_input["query"],
            max_results=tool_input.get("max_results", 5),
        )
    else:
        return f"Unknown tool: {tool_name}"


async def generate_script(
    topic: str,
    duration_minutes: int | None = None,
) -> str:
    """Generate a podcast script using Claude with arXiv tool access.

    This is an agentic function — Claude decides what to search for
    and when it has enough information to write the script.

    Args:
        topic: The main topic of the podcast (e.g., "machine learning")
        duration_minutes: Target duration in minutes. Defaults to
                         settings.podcast_duration_minutes if not provided.

    Returns:
        The generated podcast script as a string, ready for TTS.

    Raises:
        anthropic.APIError: If the Anthropic API call fails
    """
    duration = duration_minutes or settings.podcast_duration_minutes
    word_count = duration * 150

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    # Initial message asking Claude to research and write the script
    messages = [
        {
            "role": "user",
            "content": f'Research and create a podcast script about "{topic}". '
            f"Use the arxiv_search tool to find recent relevant papers, "
            f"then write an engaging {duration}-minute script (~{word_count} words).",
        }
    ]

    # Agentic loop: keep calling Claude until it gives us the final script
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            system=SYSTEM_PROMPT.format(duration_minutes=duration, word_count=word_count),
            tools=[ARXIV_SEARCH_TOOL],
            messages=messages,
        )

        # Check if Claude wants to use tools
        if response.stop_reason == "tool_use":
            # Process all tool calls in this response
            tool_results = []

            for block in response.content:
                if block.type == "tool_use":
                    print(f"  🔍 Searching arXiv: {block.input.get('query', '')}")

                    # Execute the tool
                    result = await _process_tool_call(block.name, block.input)

                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )

            # Add Claude's response and tool results to conversation
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})

        else:
            # Claude is done with tools — extract the final text response
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text

            # Fallback if no text block found
            return "Error: No script generated"
