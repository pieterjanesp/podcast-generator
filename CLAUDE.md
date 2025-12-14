# Claude Context File - Daily Learning Podcast Generator

> **IMPORTANT**: This file provides context for Claude in every new session. Update the "Current Status" section at the end of each session.

## Project Overview

**Name**: Daily Learning Podcast Generator (working title)

**What it does**: Automatically generates personalized 20-minute podcasts on topics you want to learn about. It researches recent papers, news, and learning resources daily, then synthesizes them into an engaging audio format.

### Core Flow
```
User selects topics → System researches daily → Generates script → TTS (ElevenLabs) → Serves via podcast feed
```

### Key Features
- **Topic Configuration**: Web dashboard to manage what you want to learn
- **Multi-source Research**: Academic papers, news, learning resources (tutorials, docs, etc.)
- **Script Generation**: LLM synthesizes research into engaging podcast script
- **Audio Generation**: ElevenLabs TTS converts script to natural speech
- **Podcast Delivery**: RSS feed compatible with Plappa/Audiobookshelf/standard podcast apps

---

## Tech Stack

### Backend (Python/FastAPI)
- **FastAPI**: REST API for dashboard + podcast feed endpoints
- **Celery + Redis**: Background job scheduling (daily research & generation)
- **SQLite/PostgreSQL**: Store topics, episodes, user preferences
- **ElevenLabs API**: Text-to-speech generation

### Frontend (React)
- **React + TypeScript**: Dashboard for topic management
- **Simple UI**: Topic selection, episode history, playback (optional)

### Infrastructure
- **Raspberry Pi**: Self-hosted on existing Pi with Docker
- **Docker Compose**: Backend, frontend, Redis, database
- **Cron/Celery Beat**: Trigger daily podcast generation

### External APIs & Sources
- **LLM API**: OpenAI/Anthropic for script generation
- **ElevenLabs**: TTS
- **Research Sources**:
  - arXiv API (academic papers)
  - Semantic Scholar API (papers + citations)
  - RSS feeds (news, blogs)
  - Documentation sites (learning resources)

---

## Architecture

### Backend Structure
```
backend/
├── app/
│   ├── main.py                     # FastAPI entry point
│   ├── api/
│   │   ├── routes/
│   │   │   ├── topics.py           # CRUD for topics/preferences
│   │   │   ├── episodes.py         # List/serve episodes
│   │   │   └── feed.py             # RSS feed endpoint
│   ├── services/
│   │   ├── research/               # Research orchestration
│   │   │   ├── orchestrator.py     # Coordinates all sources
│   │   │   └── sources/            # Strategy pattern per source type
│   │   │       ├── base.py         # Abstract source interface
│   │   │       ├── arxiv.py
│   │   │       ├── rss.py
│   │   │       └── docs.py
│   │   ├── script_generator.py     # LLM script creation
│   │   ├── audio_generator.py      # ElevenLabs integration
│   │   └── podcast_builder.py      # Combines everything
│   ├── workers/
│   │   └── tasks.py                # Celery tasks (daily job)
│   ├── models/                     # SQLAlchemy/Pydantic models
│   └── core/
│       ├── config.py               # Settings, API keys
│       └── scheduler.py            # Celery Beat config
├── audio/                          # Generated audio files
└── tests/
```

### Frontend Structure
```
frontend/
├── src/
│   ├── api/                        # HTTP calls to backend
│   ├── hooks/                      # React state management
│   ├── components/
│   │   ├── TopicSelector/          # Add/remove topics
│   │   ├── EpisodeList/            # Browse generated episodes
│   │   └── Player/                 # Optional in-browser playback
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   └── Settings.tsx
│   └── types/
```

### Key Design Decisions

1. **Strategy Pattern for Sources**: Each research source (arXiv, RSS, docs) implements a common interface. Easy to add new sources without changing orchestration logic.

2. **Background Processing**: Podcast generation is slow (research + LLM + TTS). Use Celery for:
   - Daily scheduled jobs
   - Async generation triggered from dashboard
   - Retry logic for API failures

3. **RSS Feed Delivery**: Standard podcast RSS format means any podcast app can subscribe. No custom client needed.

4. **Separation of Concerns**:
   - Routes = HTTP layer (thin)
   - Services = Business logic (testable)
   - Workers = Background jobs (isolated)

---

## Data Models

### Core Entities
```
Topic
├── id
├── name (e.g., "Machine Learning", "Rust Programming")
├── description
├── sources[] (which source types to use)
├── keywords[] (search terms)
├── is_active
└── created_at

Episode
├── id
├── topic_id (nullable - could be multi-topic)
├── title
├── description
├── script_text
├── audio_file_path
├── duration_seconds
├── sources_used[] (citations/links)
├── generated_at
└── published_at

Source (reference data)
├── id
├── type (arxiv, rss, docs)
├── name
├── url/config
└── is_active
```

---

## MVP Scope

### Phase 1: Core Pipeline (No Dashboard)
1. **Config file** defines topics (skip dashboard initially)
2. **Research service** fetches from 1-2 sources (start with arXiv + one RSS)
3. **Script generator** creates 20-min podcast script via LLM
4. **Audio generator** converts to speech via ElevenLabs
5. **File storage** saves audio locally
6. **Manual trigger** via CLI command

**Success criteria**: Run a command, get a podcast audio file on a topic.

### Phase 2: Scheduling + Feed
1. **Celery Beat** triggers daily generation
2. **RSS endpoint** serves podcast feed
3. **Connect to Audiobookshelf** and verify playback

### Phase 3: Dashboard
1. **Topic CRUD** via web UI
2. **Episode browser** with playback
3. **Settings** (generation time, voice, length)

---

## API Design

### REST Endpoints
```
# Topics
GET    /api/topics              # List all topics
POST   /api/topics              # Create topic
PUT    /api/topics/{id}         # Update topic
DELETE /api/topics/{id}         # Delete topic

# Episodes
GET    /api/episodes            # List episodes (paginated)
GET    /api/episodes/{id}       # Episode details
POST   /api/episodes/generate   # Trigger manual generation
GET    /api/episodes/{id}/audio # Stream audio file

# Feed
GET    /feed/rss                # Podcast RSS feed
```

---

## Configuration

### Environment Variables
```bash
# LLM
OPENAI_API_KEY=
ANTHROPIC_API_KEY=

# TTS
ELEVENLABS_API_KEY=
ELEVENLABS_VOICE_ID=

# Database
DATABASE_URL=sqlite:///./podcast.db

# Redis (for Celery)
REDIS_URL=redis://localhost:6379

# Generation settings
PODCAST_DURATION_MINUTES=20
GENERATION_HOUR=6  # 6 AM daily
```

---

## Learning Objectives

This project teaches:
1. **Background Job Processing**: Celery, task queues, scheduling
2. **External API Integration**: Rate limiting, error handling, retries
3. **Audio Processing**: Working with audio files, streaming
4. **RSS/Podcast Standards**: Feed generation, podcast app compatibility
5. **Multi-source Aggregation**: Combining data from diverse APIs
6. **LLM Prompt Engineering**: Creating engaging scripts from research

---

## Technical Challenges to Solve

1. **Rate Limiting**: ElevenLabs has character limits; need chunking strategy
2. **Script Quality**: Prompt engineering for engaging, educational content
3. **Source Relevance**: Filtering/ranking research results
4. **Audio Length**: Hitting ~20 min target consistently
5. **Pi Performance**: Might need to offload TTS to cloud if Pi struggles

---

## Open Questions

- [ ] Single voice or conversational (two hosts)? ElevenLabs supports both.
- [ ] How to handle multi-topic days? One combined podcast or separate?
- [ ] Caching strategy for research results?
- [ ] How to cite sources in audio format naturally?

---

## Current Status

**Last Updated**: 2024-12-14

**Phase**: Project Setup

**Completed**:
- [x] Defined project scope and goals
- [x] Chose tech stack (FastAPI + React + ElevenLabs)
- [x] Designed initial architecture
- [x] Created CLAUDE.md

**In Progress**:
- [ ] Initialize project structure

**Next Steps**:
1. Create backend folder structure
2. Set up FastAPI with basic health endpoint
3. Create first research source (arXiv)
4. Test LLM script generation with sample research
5. Test ElevenLabs integration

---

## Commands Reference

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Celery worker
celery -A app.workers.tasks worker --loglevel=info

# Celery beat (scheduler)
celery -A app.workers.tasks beat --loglevel=info

# Frontend
cd frontend
npm install
npm run dev

# Docker (production)
docker-compose up -d
```

---

## How to Continue

When starting a new Claude session, say:
- "Let's continue building the podcast generator"
- "What's next for the podcast project?"
- "Pick up where we left off"

Claude will read this file and know the full context.
