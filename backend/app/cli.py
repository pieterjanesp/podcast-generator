"""CLI for Podcast Generator

This module provides command-line commands to generate podcasts.

Usage:
    # Generate script only (default, saves to scripts/ as markdown)
    uv run python -m app.cli generate "machine learning"

    # Generate script AND audio
    uv run python -m app.cli generate "machine learning" --audio

    # Generate with custom duration (minutes)
    uv run python -m app.cli generate "quantum computing" --duration 10

Flow (Agentic):
    1. Claude researches the topic using arXiv MCP server
    2. Claude generates a podcast script from the research
    3. (Optional) ElevenLabs converts script to audio

Dependencies:
    - click: CLI framework
    - app.services.script_generator: Agentic script generation with MCP
    - app.services.audio_generator: ElevenLabs TTS (optional)
"""

import asyncio
from datetime import datetime
from pathlib import Path

import click

from app.services.script_generator import generate_script
from app.services.audio_generator import generate_audio


@click.group()
def cli():
    """Podcast Generator CLI."""
    pass


@cli.command()
@click.argument("topic")
@click.option(
    "--duration",
    "-d",
    default=None,
    type=int,
    help="Target duration in minutes (default: from config)",
)
@click.option(
    "--audio",
    "-a",
    is_flag=True,
    default=False,
    help="Generate audio with ElevenLabs (default: script only)",
)
def generate(topic: str, duration: int | None, audio: bool):
    """Generate a podcast episode on TOPIC.

    By default, generates only the script (saved as markdown).
    Use --audio to also generate audio via ElevenLabs.

    Examples:
        uv run python -m app.cli generate "machine learning"
        uv run python -m app.cli generate "SAM3" --audio --duration 5
    """
    asyncio.run(_generate_podcast(topic, duration, audio))


async def _generate_podcast(topic: str, duration: int | None, generate_audio_flag: bool):
    """Async implementation of podcast generation pipeline.

    This orchestrates the agentic flow:
    1. Claude researches + writes script (using arXiv MCP server)
    2. (Optional) ElevenLabs generates audio

    Args:
        topic: Topic to generate podcast about
        duration: Target duration in minutes (or None for default)
        generate_audio_flag: Whether to generate audio (default: False)
    """
    click.echo(f"🎙️  Generating podcast on: {topic}")
    click.echo("=" * 50)

    # Step 1: Agentic research + script generation
    click.echo("\n🤖 Researching & generating script...")
    click.echo("   (Claude is searching arXiv and writing the script)")
    script = await generate_script(topic, duration_minutes=duration)
    word_count = len(script.split())
    click.echo(f"   Generated {word_count} words (~{word_count // 150} minutes)")

    # Save script to markdown file
    scripts_dir = Path("scripts")
    scripts_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_topic = topic.replace(" ", "_").replace("/", "-")
    script_filename = f"{safe_topic}_{timestamp}.md"
    script_path = scripts_dir / script_filename

    with open(script_path, "w") as f:
        f.write(f"# Podcast Script: {topic}\n\n")
        f.write(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        f.write(f"*Duration: ~{word_count // 150} minutes ({word_count} words)*\n\n")
        f.write("---\n\n")
        f.write(script)

    click.echo(f"\n📝 Script saved to: {script_path}")

    # Step 2: Generate audio (optional)
    if generate_audio_flag:
        click.echo("\n🔊 Generating audio...")
        audio_filename = f"{safe_topic}_{timestamp}.mp3"
        audio_path = await generate_audio(script, audio_filename)
        file_size = audio_path.stat().st_size / (1024 * 1024)  # MB
        click.echo(f"   Saved to: {audio_path}")
        click.echo(f"   File size: {file_size:.1f} MB")

    # Done
    click.echo("\n" + "=" * 50)
    click.echo("✅ Podcast generated successfully!")
    click.echo(f"   Script: {script_path}")
    if generate_audio_flag:
        click.echo(f"   Audio: {audio_path}")


if __name__ == "__main__":
    cli()
