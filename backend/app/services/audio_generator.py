"""Audio Generator Service

This module converts text scripts to audio using the ElevenLabs API.

Flow:
    1. Receives a text script
    2. Sends text to ElevenLabs TTS API
    3. Receives audio stream
    4. Saves to MP3 file

Usage:
    from app.services.audio_generator import generate_audio

    audio_path = await generate_audio(
        text="Hello, welcome to the podcast...",
        output_filename="episode_001.mp3"
    )

Dependencies:
    - elevenlabs: Official ElevenLabs Python SDK
    - app.core.config: For API key, voice ID, and output directory

Notes:
    - ElevenLabs has character limits per request (~5000 chars for most plans)
    - Long scripts may need chunking (not implemented yet - future enhancement)
    - Audio is saved as MP3 format
"""

from pathlib import Path

from elevenlabs import ElevenLabs

from app.core.config import settings


async def generate_audio(
    text: str,
    output_filename: str,
    voice_id: str | None = None,
) -> Path:
    """Convert text to speech and save as MP3.

    Uses ElevenLabs API to generate natural-sounding speech from text.
    The audio is saved to the configured output directory.

    Args:
        text: The script text to convert to speech
        output_filename: Name for the output file (e.g., "episode_001.mp3")
        voice_id: ElevenLabs voice ID. Defaults to settings.elevenlabs_voice_id

    Returns:
        Path to the saved audio file

    Raises:
        elevenlabs.ApiError: If the ElevenLabs API call fails
        OSError: If file cannot be written
    """
    # Use provided voice or fall back to config
    voice = voice_id or settings.elevenlabs_voice_id

    # Ensure output directory exists
    output_dir = Path(settings.audio_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / output_filename

    # Initialize ElevenLabs client
    client = ElevenLabs(api_key=settings.elevenlabs_api_key)

    # Generate audio using text-to-speech
    # Returns a generator of audio chunks
    audio_generator = client.text_to_speech.convert(
        voice_id=voice,
        text=text,
        model_id="eleven_multilingual_v2",  # High quality multilingual model
    )

    # Write audio chunks to file
    with open(output_path, "wb") as f:
        for chunk in audio_generator:
            f.write(chunk)

    return output_path
