from fastapi import APIRouter
from . import auth, contact_groups, triggers, contacts, call_logs, email_events, system_stats

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(contact_groups.router)
api_router.include_router(triggers.router)
api_router.include_router(contacts.router)
api_router.include_router(call_logs.router)
api_router.include_router(email_events.router)
api_router.include_router(system_stats.router)