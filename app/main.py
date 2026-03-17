from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.users import router as users_router
from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.project_activity import router as project_activity_router
from app.api.issues import router as issues_router
from app.api.labels import router as labels_router
from app.api.comments import router as comments_router
from app.api.memberships import router as memberships_router
from app.core.exceptions import (
    http_exception_handler,
    validation_exception_handler,
)

app = FastAPI(title="Issue Tracker API")

# Exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# CORS
frontend_url = os.getenv("FRONTEND_URL")

allowed_origins = [
    "http://127.0.0.1:5173",
    "http://localhost:5173",
]

if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(users_router)
app.include_router(auth_router)
app.include_router(memberships_router)
app.include_router(projects_router)
app.include_router(project_activity_router)
app.include_router(issues_router)
app.include_router(labels_router)
app.include_router(comments_router)

# Health check
@app.get("/")
def root():
    return {"message": "Issue Tracker API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}