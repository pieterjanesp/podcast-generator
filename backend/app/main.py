from fastapi import FastAPI

app = FastAPI(
    title="Podcast Generator API",
    description="Generates personalized learning podcasts",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    """Health check endpoint to verify the API is running."""
    return {"status": "healthy"}
