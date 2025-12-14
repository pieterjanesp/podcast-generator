"""CLI for Podcast Generator

This module provides command-line commands to generate podcasts.

Usage:
    # Generate a podcast on a topic
    uv run python -m app.cli generate "machine learning"

    # Generate with custom duration (minutes)
    uv run python -m app.cli generate "quantum computing" --duration 10

Flow (Agentic):
    1. Claude researches the topic using arXiv tool (decides what to search)
    2. Claude generates a podcast script from the research
    3. ElevenLabs converts script to audio
    4. Save MP3 to audio/ directory

Dependencies:
    - click: CLI framework
    - app.services.script_generator: Agentic script generation with tool use
    - app.services.audio_generator: ElevenLabs TTS
"""

import asyncio
from datetime import datetime

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
def generate(topic: str, duration: int | None):
    """Generate a podcast episode on TOPIC.

    Claude will research the topic using arXiv, then generate a script
    and convert it to audio.

    Example:
        uv run python -m app.cli generate "machine learning"
    """
    asyncio.run(_generate_podcast(topic, duration))


async def _generate_podcast(topic: str, duration: int | None):
    """Async implementation of podcast generation pipeline.

    This orchestrates the agentic flow:
    1. Claude researches + writes script (using arXiv tool)
    2. ElevenLabs generates audio

    Args:
        topic: Topic to generate podcast about
        duration: Target duration in minutes (or None for default)
    """
    click.echo(f"🎙️  Generating podcast on: {topic}")
    click.echo("=" * 50)

    # Step 1: Agentic research + script generation
    # Claude decides what to search and synthesizes results
    click.echo("\n🤖 Step 1/2: Researching & generating script...")
    click.echo("   (Claude is searching arXiv and writing the script)")
    script = await generate_script(topic, duration_minutes=duration)
    word_count = len(script.split())
    click.echo(f"   Generated {word_count} words (~{word_count // 150} minutes)")

    # Step 2: Generate audio
    click.echo("\n🔊 Step 2/2: Generating audio...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{topic.replace(' ', '_')}_{timestamp}.mp3"
    audio_path = await generate_audio(script, filename)
    file_size = audio_path.stat().st_size / (1024 * 1024)  # MB
    click.echo(f"   Saved to: {audio_path}")
    click.echo(f"   File size: {file_size:.1f} MB")

    # Done
    click.echo("\n" + "=" * 50)
    click.echo("✅ Podcast generated successfully!")
    click.echo(f"   Audio file: {audio_path}")


if __name__ == "__main__":
    cli()
