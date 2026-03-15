"""
Main entry point for the FastAPI application.
"""
from fastapi import FastAPI
from app.routers import items, interactions, learners, analytics, pipeline

app = FastAPI(title="Learning Management Service")

app.include_router(items.router, prefix="/items", tags=["items"])
app.include_router(interactions.router, prefix="/interactions", tags=["interactions"])
app.include_router(learners.router, prefix="/learners", tags=["learners"])
app.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
app.include_router(pipeline.router, prefix="/pipeline", tags=["pipeline"])

@app.get("/")
async def root():
    return {"message": "Learning Management Service API"}
