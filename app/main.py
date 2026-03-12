from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import http_exception_handler, validation_exception_handler

from app.api.users import router as users_router
from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.issues import router as issues_router
from app.api.labels import router as labels_router
from app.api.memberships import router as memberships_router
from app.api.comments import router as comments_router

app = FastAPI(title="Issue Tracker API")

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(memberships_router)
app.include_router(projects_router)
app.include_router(issues_router)
app.include_router(labels_router)
app.include_router(comments_router)



@app.get("/")
def root():
    return {"message": "Issue Tracker API is running"}