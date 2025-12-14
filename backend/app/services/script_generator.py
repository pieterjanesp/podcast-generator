"""Script Generator Service (Agentic with MCP)

This module generates podcast scripts using Claude with MCP tool access.
Claude acts as an agent that can search arXiv, download papers, and read
their full content using the arxiv-mcp-server.

Flow:
    1. Connect to arxiv-mcp-server via MCP protocol
    2. Claude receives the server's tools (search_papers, download_paper, read_paper, etc.)
    3. Claude decides what to search, which papers to download, and what to read
    4. Claude synthesizes all research into a podcast script
    5. Returns the final script text

MCP Tools Available:
    - search_papers: Search arXiv for papers (returns metadata)
    - download_paper: Download a paper by arXiv ID (stores locally)
    - read_paper: Read the full content of a downloaded paper
    - list_papers: List all downloaded papers

Usage:
    from app.services.script_generator import generate_script

    script = await generate_script("machine learning", duration_minutes=5)

Key Concepts:
    - MCP (Model Context Protocol): Standard for connecting AI to external tools
    - The arxiv-mcp-server runs as a subprocess, communicating via stdio
    - Claude dynamically discovers and uses the server's tools
"""

import anthropic

from app.core.config import settings
from app.services.mcp_client import ArxivMCPClient


# System prompt for the agentic script generator
SYSTEM_PROMPT = """You are a podcast script writer with access to arXiv research tools.

You have access to these tools:
- search_papers: Search arXiv for papers on a topic
- download_paper: Download a paper by its arXiv ID to read its full content
- read_paper: Read the full text of a downloaded paper
- list_papers: See what papers you've already downloaded

Your workflow should be:
1. Search for relevant papers on the topic
2. Download 2-3 of the most interesting/relevant papers
3. Read the downloaded papers to understand their content deeply
4. Write an engaging podcast script synthesizing your research

Your scripts should:
- Be conversational and engaging, as if explaining to a curious friend
- Break down complex concepts into digestible pieces
- Include specific insights from the papers you read
- Be approximately {duration_minutes} minutes when read aloud (~150 words per minute)
- NOT include speaker labels, timestamps, or production notes
- Flow naturally as a monologue

Target length: approximately {word_count} words.

When you're ready to write the script, just write it directly (don't use any tools)."""


async def generate_script(
    topic: str,
    duration_minutes: int | None = None,
) -> str:
    """Generate a podcast script using Claude with MCP arXiv tools.

    This is an agentic function — Claude decides what to search, download,
    and read, then writes a script based on the full paper content.

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

    # Connect to the arXiv MCP server
    async with ArxivMCPClient() as mcp:
        # Get available tools from the MCP server
        tools = mcp.tools

        # Initial message asking Claude to research and write the script
        messages = [
            {
                "role": "user",
                "content": f'Research and create a podcast script about "{topic}". '
                f"First search for relevant papers, download 2-3 of the most interesting ones, "
                f"read them to understand the content deeply, then write an engaging "
                f"{duration}-minute script (~{word_count} words) based on your research.",
            }
        ]

        # Agentic loop: keep calling Claude until it gives us the final script
        while True:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=8000,
                system=SYSTEM_PROMPT.format(duration_minutes=duration, word_count=word_count),
                tools=tools,
                messages=messages,
            )

            # Check if Claude wants to use tools
            if response.stop_reason == "tool_use":
                # Process all tool calls in this response
                tool_results = []

                for block in response.content:
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_args = block.input

                        print(f"  🔧 Tool: {tool_name}")
                        if "query" in tool_args:
                            print(f"     Query: {tool_args['query']}")
                        if "paper_id" in tool_args:
                            print(f"     Paper: {tool_args['paper_id']}")

                        # Execute the tool via MCP
                        result = await mcp.call_tool(tool_name, tool_args)

                        # Truncate very long results for logging
                        result_preview = result[:200] + "..." if len(result) > 200 else result
                        print(f"     Result: {result_preview}")

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
