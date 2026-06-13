import json
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, storage

from app.config import settings


def initialize_firebase() -> None:
    if not settings.FIREBASE_CREDENTIALS or not settings.FIREBASE_STORAGE_BUCKET:
        return

    if firebase_admin._apps:
        return

    credentials_data = settings.FIREBASE_CREDENTIALS
    if Path(credentials_data).exists():
        cred = credentials.Certificate(credentials_data)
    else:
        cred = credentials.Certificate(json.loads(credentials_data))

    firebase_admin.initialize_app(cred, {"storageBucket": settings.FIREBASE_STORAGE_BUCKET})


def upload_file(filename: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    initialize_firebase()
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_string(data, content_type=content_type)
    blob.make_public()
    return blob.public_url
