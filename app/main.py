"""
FastAPI Application - CHAT-O delivery layer

Entry point: uvicorn app.main:app --host 0.0.0.0 --port 7860
"""
import logging
import os
from contextlib import asynccontextmanager
import json
from typing import Generator, List

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Load env at import time (same behavior as old app.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Repo root: keeps memoria.db and .env where they have always lived
REPO_ROOT = os.path.dirname(BASE_DIR)
dotenv_path = os.path.join(REPO_ROOT, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()

# Import business layer (DO NOT MODIFY these files)
from config.settings import (
    SYSTEM_PROMPT,
    BAD_WORDS,
    MODEL_CONFIG,
    MEMORY_CONFIG,
)
from adapters.data.database import DatabaseAdapter
from adapters.external.groq import GroqAdapter
from utils.moderation import ContentModerator
from use_cases.chat import ChatUseCase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("chat-o")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build ChatUseCase once at startup (not per-request)"""
    # Initialize adapters
    db_path = os.path.join(REPO_ROOT, "memoria.db")
    database_adapter = DatabaseAdapter(db_path)
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError(
            "Missing GROQ_API_KEY! Set it in .env file or as environment variable."
        )
    groq_adapter = GroqAdapter(groq_api_key)
    
    # Initialize components
    content_moderator = ContentModerator(BAD_WORDS)
    chat_use_case = ChatUseCase(
        system_prompt=SYSTEM_PROMPT,
        groq_adapter=groq_adapter,
        database_adapter=database_adapter,
        content_moderator=content_moderator,
        memory_config=MEMORY_CONFIG
    )
    
    # Store on app.state so endpoints can reach it
    app.state.chat_use_case = chat_use_case
    logger.info("CHAT-O initialized successfully")
    yield


# Create FastAPI app
app = FastAPI(
    title="CHAT-O",
    description="El robot más chistoso y divertido de todo internet!",
    version="1.0.0",
    lifespan=lifespan
)


class ChatRequest(BaseModel):
    """Request body for the chat endpoint"""
    message: str
    history: List = []


@app.get("/")
async def root(request: Request) -> FileResponse:
    """Serve the main chat UI"""
    static_dir = os.path.join(BASE_DIR, "static")
    return FileResponse(
        os.path.join(static_dir, "index.html"),
        media_type="text/html",
        headers={"Cache-Control": "no-cache"}
    )


app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


@app.post("/api/chat")
async def chat_endpoint(body: ChatRequest, request: Request) -> StreamingResponse:
    """
    Chat endpoint with SSE streaming.

    Accepts JSON body: {"message": str, "history": list}
    Returns text/event-stream with ONE event containing the full reply.
    """
    chat_use_case = request.app.state.chat_use_case
    
    def generate() -> Generator[str, None, None]:
        try:
            # Process message through use case (yields one tuple per call)
            for reply, _ in chat_use_case.process_message(body.message, body.history):
                payload = json.dumps({"reply": reply})
                yield f"data: {payload}\n\n"
            
            # Emit done marker
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            payload = json.dumps({"error": str(e)})
            yield f"data: {payload}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@app.get("/health")
async def health_check() -> dict:
    """Liveness probe"""
    return {"status": "ok"}
