from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.database.connection import init_db_pool, close_db_pool
from app.core.config import settings

app = FastAPI(
    title="MailToCall API",
    description="API for managing MailToCall system - contact groups, triggers, contacts, call logs, and email events",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    await init_db_pool()


@app.on_event("shutdown")
async def shutdown_event():
    await close_db_pool()


@app.get("/")
async def root():
    return {"message": "MailToCall API is running"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}