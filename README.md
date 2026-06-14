# Student Hostel Management System - Backend

This backend implements a FastAPI service for student hostel management with PostgreSQL, JWT authentication, M-Pesa callback handling, and optional Firebase uploads.

## Features

- User signup/login with JWT
- Role-based access (student/admin)
- Available room browsing and room applications
- Maintenance request creation/tracking
- M-Pesa STK push initiation and callback handling
- Firebase storage upload endpoint
- Docker-ready backend

## Requirements

- Python 3.12+
- PostgreSQL
- `pip install -r requirements.txt`

## Environment

Create a `.env` file in the backend root with:

```env
SECRET_KEY=supersecretkey
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/hostel_db
FIREBASE_CREDENTIALS=
FIREBASE_STORAGE_BUCKET=
MPESA_CONSUMER_KEY=
MPESA_CONSUMER_SECRET=
MPESA_SHORTCODE=
MPESA_PASSKEY=
MPESA_CALLBACK_URL=
MPESA_ENVIRONMENT=sandbox
```

## Run locally

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker

```bash
docker build -t hostel-management-backend .
docker run -e SECRET_KEY=supersecretkey -e DATABASE_URL=postgresql://postgres:postgres@db:5432/hostel_db -p 8000:8000 hostel-management-backend
```

## Render

- Set `Dockerfile` as the service root
- Add environment variables from above
- Expose port `8000`

## Notes

- Use PostgreSQL in production.
- Keep Firebase service account keys out of version control.
- Use the `/payments/mpesa/callback` endpoint as the Daraja callback URL.


