from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from app.api.routers import saas_info, leads, reddit_posts, tasks
from app.core.database import engine
from app.core.dependencies import get_command_bus, get_query_bus
from app.models import models # Keep for target_metadata in Alembic env.py, but not for create_all
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = FastAPI(
    title="Reddit Engagement API",
    description="API for managing SaaS information, Reddit leads, and post generation/posting.",
    version="1.0.0",
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logging.error(f"HTTP Exception: {exc.detail} (Status Code: {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"message": "An unexpected error occurred."},
    )

app.include_router(saas_info.router)
app.include_router(leads.router)
app.include_router(reddit_posts.router)
app.include_router(reddit_posts.comments_router) # Include the new comments router
app.include_router(tasks.router) # Include the new tasks router

@app.get("/")
async def root():
    return {"message": "Welcome to the Reddit Engagement API!"}
