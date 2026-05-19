# Phase 1 Capstone — DevSecOps Project

A Dockerised Python Flask REST API with PostgreSQL, built as the capstone for
Phase 1 of a DevSecOps learning path.

## Stack
- Python 3.12 + Flask + SQLAlchemy
- PostgreSQL 16 (Alpine)
- Docker + Docker Compose
- pytest for testing
- GitHub Actions for CI (coming in Step 11)

## Quick start

```bash
# Run the full stack
docker compose up --build

# Test the API
curl http://localhost:5000/health
curl http://localhost:5000/users
```

## Project structure

- `app/` — Flask application
- `tests/` — pytest unit tests
- `scripts/` — environment checks, dependency validator, DB init
- `Dockerfile` — secure image build (non-root user, slim base)
- `docker-compose.yml` — Flask + PostgreSQL orchestration

## Phase 2 preview

This project is the foundation for Phase 2, which will add:
- Semgrep (SAST scanning)
- Gitleaks (secret detection)
- Trivy (container/dependency vulnerability scanning)
