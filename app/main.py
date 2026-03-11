from fastapi import FastAPI

from app.api.users import router as users_router
from app.api.auth import router as auth_router
from app.api.projects import router as projects_router

app = FastAPI(title="Issue Tracker API")

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(projects_router)


@app.get("/")
def root():
    return {"message": "Issue Tracker API is running"}