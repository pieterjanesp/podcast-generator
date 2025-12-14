from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore extra env vars not defined here
    )

    # LLM API (using Anthropic for script generation)
    anthropic_api_key: str = ""

    # Text-to-Speech (ElevenLabs)
    elevenlabs_api_key: str = ""
    elevenlabs_voice_id: str = "21m00Tcm4TlvDq8ikWAM"  # Default: "Rachel" voice

    # Podcast settings
    podcast_duration_minutes: int = 5
    audio_output_dir: str = "audio"

    # Development
    debug: bool = False


# Singleton instance - import this throughout the app
settings = Settings()
