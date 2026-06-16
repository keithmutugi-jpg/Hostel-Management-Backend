import json
from pathlib import Path

import firebase_admin
from firebase_admin import App, credentials

from app.config import settings

from .exceptions import FirebaseConfigurationError


def _build_credentials():
    credentials_data = settings.FIREBASE_CREDENTIALS
    if not credentials_data:
        raise FirebaseConfigurationError("FIREBASE_CREDENTIALS is not configured")

    credentials_path = Path(credentials_data)
    if credentials_path.exists():
        return credentials.Certificate(str(credentials_path))

    try:
        return credentials.Certificate(json.loads(credentials_data))
    except json.JSONDecodeError as exc:
        raise FirebaseConfigurationError("FIREBASE_CREDENTIALS must be a JSON string or a file path") from exc


def initialize_firebase() -> App | None:
    if not settings.FIREBASE_CREDENTIALS or not settings.FIREBASE_STORAGE_BUCKET:
        return None

    if firebase_admin._apps:
        return firebase_admin.get_app()

    options = {"storageBucket": settings.FIREBASE_STORAGE_BUCKET}
    if settings.FIREBASE_PROJECT_ID:
        options["projectId"] = settings.FIREBASE_PROJECT_ID

    return firebase_admin.initialize_app(_build_credentials(), options)


def get_firebase_app() -> App:
    app = initialize_firebase()
    if app is None:
        raise FirebaseConfigurationError("Firebase Admin SDK is not configured")
    return app
