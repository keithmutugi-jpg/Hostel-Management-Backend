from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth_router, admin_router, payments_router, students_router
from app.services import initialize_firebase

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    initialize_firebase()


@app.get("/", tags=["Root"])
def root():
    return {"message": "Student Hostel Management System backend is running."}


@app.post("/upload", tags=["Upload"])
async def upload_file(file: UploadFile = File(...)):
    from app.services import upload_file as upload_to_firebase

    if not settings.FIREBASE_CREDENTIALS or not settings.FIREBASE_STORAGE_BUCKET:
        raise HTTPException(status_code=503, detail="Firebase storage is not configured")

    data = await file.read()
    public_url = upload_to_firebase(file.filename, data, file.content_type or "application/octet-stream")
    return {"url": public_url}


app.include_router(auth_router)
app.include_router(students_router)
app.include_router(admin_router)
app.include_router(payments_router)
