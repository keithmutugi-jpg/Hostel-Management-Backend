from firebase_admin import storage

from .client import get_firebase_app


def upload_file(filename: str, data: bytes, content_type: str = "application/octet-stream") -> str:
    get_firebase_app()
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_string(data, content_type=content_type)
    blob.make_public()
    return blob.public_url
