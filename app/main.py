from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth_router, admin_router, payments_router, students_router
from app.services import FirebaseConfigurationError, initialize_firebase


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    initialize_firebase()
    yield

tags_metadata = [
    {"name": "Root", "description": "Service health and welcome endpoint."},
    {"name": "Auth", "description": "User signup, login, and current profile endpoints."},
    {"name": "Students", "description": "Student room browsing, applications, maintenance, and payments."},
    {"name": "Admin", "description": "Administrative room, application, maintenance, payment, and report operations."},
    {"name": "Payments", "description": "Payment provider callbacks."},
    {"name": "Upload", "description": "Optional Firebase-backed file upload."},
]

app = FastAPI(title=settings.PROJECT_NAME, openapi_tags=tags_metadata, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
def root():
    return {"message": "Student Hostel Management System backend is running."}


@app.post("/upload", tags=["Upload"])
async def upload_file(file: UploadFile = File(...)):
    from app.services import upload_file as upload_to_firebase

    if not settings.FIREBASE_CREDENTIALS or not settings.FIREBASE_STORAGE_BUCKET:
        raise HTTPException(status_code=503, detail="Firebase storage is not configured")

    data = await file.read()
    try:
        public_url = upload_to_firebase(file.filename, data, file.content_type or "application/octet-stream")
    except FirebaseConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return {"url": public_url}


app.include_router(auth_router)
app.include_router(students_router)
app.include_router(admin_router)
app.include_router(payments_router)
