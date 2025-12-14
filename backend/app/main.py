from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.generate import router as generate_router

app = FastAPI(
    title="Podcast Generator API",
    description="Generates personalized learning podcasts",
    version="0.1.0",
)

# CORS middleware - allows frontend to call backend
# In production, restrict origins to your actual domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(generate_router)


@app.get("/health")
def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy"}
