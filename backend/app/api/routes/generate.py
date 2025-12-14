"""Generate Podcast API Route

This module provides the REST endpoint for generating podcast scripts.
It connects the frontend to the script generation service.

Flow:
    1. Frontend sends POST /api/generate with topic and duration
    2. Script generator researches via MCP and writes script
    3. Returns the generated script to the frontend

Note: This is a synchronous endpoint for simplicity. In production,
you'd want to use background tasks (Celery) for long-running generations.
"""

from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

from app.services.script_generator import generate_script


router = APIRouter(prefix="/api", tags=["generate"])


class GenerateRequest(BaseModel):
    """Request body for podcast generation."""

    topic: str = Field(..., min_length=1, description="The research topic")
    duration_minutes: int = Field(
        default=5, ge=1, le=30, description="Target duration in minutes"
    )


class GenerateResponse(BaseModel):
    """Response body containing the generated script."""

    topic: str
    duration_minutes: int
    script: str
    word_count: int


@router.post("/generate", response_model=GenerateResponse)
async def generate_podcast(request: GenerateRequest) -> GenerateResponse:
    """Generate a podcast script for the given topic.

    This endpoint:
    1. Searches arXiv for relevant papers using MCP
    2. Downloads and reads paper content
    3. Generates an engaging podcast script

    Args:
        request: Contains topic and duration_minutes

    Returns:
        GenerateResponse with the script and metadata

    Raises:
        HTTPException: If generation fails
    """
    try:
        print(f"\n🎙️ Generating podcast: '{request.topic}' ({request.duration_minutes} min)")

        script = await generate_script(
            topic=request.topic,
            duration_minutes=request.duration_minutes,
        )

        word_count = len(script.split())

        print(f"✅ Generated {word_count} words")

        return GenerateResponse(
            topic=request.topic,
            duration_minutes=request.duration_minutes,
            script=script,
            word_count=word_count,
        )

    except Exception as e:
        print(f"❌ Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
