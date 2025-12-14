# Podcast Generator - Development Progress

## Current Status: MVP Complete ✅

**Goal achieved**: Run a command → get a podcast audio file on a topic.

```bash
uv run python -m app.cli generate "machine learning" --duration 5
```

---

## Completed Steps

### 1. Project Setup ✅
- Created folder structure following separation of concerns
- Initialized FastAPI with health endpoint
- Set up `uv` for package management

**Files created:**
- `app/main.py` — FastAPI entry point with `/health` endpoint
- `app/api/routes/` — (empty, for future HTTP endpoints)
- `app/services/` — Business logic layer
- `app/models/` — (empty, for Pydantic/DB models)
- `app/core/` — Configuration and settings

### 2. Config System ✅
- Pydantic Settings for type-safe config from environment variables
- `.env` file support for local development
- `.env.example` template for required variables

**Files created:**
- `app/core/config.py` — Settings class with all config options
- `.env.example` — Template showing required env vars
- `.env` — Local config (gitignored, contains API keys)

**Config options:**
- `ANTHROPIC_API_KEY` — For LLM script generation
- `ELEVENLABS_API_KEY` — For text-to-speech
- `ELEVENLABS_VOICE_ID` — Which voice to use
- `PODCAST_DURATION_MINUTES` — Target podcast length (default: 5)

### 3. arXiv Research Source ✅
- Implemented Strategy Pattern for research sources
- Base interface allows adding new sources easily
- arXiv source fetches recent papers via their API

**Files created:**
- `app/services/research/sources/base.py` — Abstract interface + ResearchItem dataclass
- `app/services/research/sources/arxiv.py` — arXiv API implementation

**How it works:**
```
ArxivSource.search("machine learning")
  → HTTP GET to arXiv API (https://export.arxiv.org/api/query)
  → Parse XML response
  → Return list[ResearchItem]
```

### 4. Script Generator ✅
- Uses Anthropic API (Claude) to generate podcast scripts
- Takes topic + research items → returns natural script text
- Configurable duration (word count based on ~150 words/minute)

**Files created:**
- `app/services/script_generator.py` — LLM-based script generation

**How it works:**
```
generate_script("AI", research_items, duration_minutes=10)
  → Format research into prompt
  → Call Claude API with system prompt
  → Return script text (~1500 words for 10 min)
```

### 5. Audio Generator ✅
- Uses ElevenLabs API for text-to-speech
- Converts script text to natural-sounding MP3 audio
- Saves to `audio/` directory

**Files created:**
- `app/services/audio_generator.py` — ElevenLabs TTS integration

**How it works:**
```
generate_audio(script_text, "episode.mp3")
  → Call ElevenLabs API with voice ID
  → Stream audio chunks to file
  → Return path to saved MP3
```

### 6. CLI Command ✅
- Ties everything together into a simple command
- Full pipeline: Research → Script → Audio

**Files created:**
- `app/cli.py` — Click-based CLI with `generate` command

**Usage:**
```bash
# Basic usage
uv run python -m app.cli generate "quantum computing"

# With options
uv run python -m app.cli generate "AI" --duration 10 --max-papers 5
```

---

## Architecture Overview

```
backend/
├── app/
│   ├── main.py                 # FastAPI entry point (health check)
│   ├── cli.py                  # CLI commands (generate)
│   ├── api/routes/             # HTTP endpoints (future)
│   ├── services/               # Business logic (framework-agnostic)
│   │   ├── research/
│   │   │   └── sources/        # Strategy Pattern
│   │   │       ├── base.py     # Abstract interface + ResearchItem
│   │   │       └── arxiv.py    # arXiv implementation
│   │   ├── script_generator.py # Claude script generation
│   │   └── audio_generator.py  # ElevenLabs TTS
│   ├── models/                 # Pydantic schemas (future)
│   └── core/
│       └── config.py           # Settings from env vars
├── audio/                      # Generated podcast MP3 files
├── .env                        # Local config (gitignored)
├── .env.example                # Template for env vars
├── pyproject.toml              # Dependencies (uv)
└── tests/                      # (future)
```

**Key Design Decisions:**

1. **Strategy Pattern** for research sources — easy to add RSS, docs, etc.
2. **Separation of concerns** — services are framework-agnostic, callable from CLI, API, or tests
3. **Async throughout** — prepared for concurrent operations
4. **Config via environment** — secure, 12-factor app style

---

## Dependencies

```toml
[project]
dependencies = [
    "fastapi>=0.124.4",      # Web framework
    "uvicorn[standard]",     # ASGI server
    "pydantic-settings",     # Config from env vars
    "httpx",                 # Async HTTP client (arXiv)
    "anthropic",             # Claude API
    "elevenlabs",            # Text-to-speech
]
```

---

## Future Enhancements (Post-MVP)

### Phase 2: Scheduling + Feed
- [ ] Celery + Redis for background job scheduling
- [ ] Daily automatic generation
- [ ] RSS feed endpoint for podcast apps

### Phase 3: Dashboard
- [ ] React frontend for topic management
- [ ] Episode browser with playback
- [ ] Settings UI

### Future Ideas
- [ ] LLM-based research orchestrator (agentic research)
- [ ] Multiple research sources (RSS, Hacker News, documentation)
- [ ] Multi-voice conversations (two hosts)
- [ ] Script chunking for very long podcasts
- [ ] Citation handling in audio

---

## Quick Reference

```bash
# Start dev server
uv run uvicorn app.main:app --reload

# Generate podcast
uv run python -m app.cli generate "topic" --duration 5

# Check health
curl http://localhost:8000/health
```
