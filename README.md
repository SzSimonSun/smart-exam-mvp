
# Smart Exam System (V3.1) — MVP Starter

Generated on 2025-09-26T06:09:20

## What's inside
- `schema.sql` — PostgreSQL schema for MVP
- `openapi.yaml` — Minimal API contract for core flows
- `docker-compose.yml` — Dev stack (Postgres, Redis, RabbitMQ, MinIO, backend, frontend)
- `backend/` — FastAPI skeleton with health/upload/report
- `frontend/` — Placeholder README for Vite + React bootstrapping

## Quick Start
1. Install Docker & Docker Compose.
2. Clone/extract this package and run:
   ```bash
   docker-compose up -d
   ```
3. Initialize DB:
   ```bash
   docker exec -i smart_exam_pg psql -U exam -d examdb < /init/schema.sql
   ```
   (or run `psql` locally and execute `schema.sql`)

4. Backend API: http://localhost:8000/docs
5. Frontend dev server: http://localhost:5173

## Next Steps
- Implement MinIO upload in `/api/answer-sheets/upload` and queue OCR/OMR job.
- Flesh out API endpoints per `openapi.yaml`.
- Build teacher UI pages: Question Bank, Paper Builder, Upload & Progress, Reports, Ingest Review.
- Add unit/integration tests and edge-case dataset.

## Notes
- Default credentials for services:
  - Postgres: `exam/exam` DB `examdb`
  - MinIO: `minio/minio123` (console http://localhost:9001)
  - RabbitMQ console: http://localhost:15672 (guest/guest)
