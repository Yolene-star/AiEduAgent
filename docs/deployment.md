# Deployment

## Local Docker Compose

If Docker is not installed on Ubuntu, run:

```bash
bash scripts/install_docker_ubuntu.sh
```

Then log out and log back in, or run `newgrp docker`.

If the current machine has no sudo permission, use the GitHub Actions workflow instead:

1. Push to GitHub.
2. Open `Actions`.
3. Run or inspect `Docker Build`.

The workflow builds both Docker images and runs `docker compose build` on GitHub's Ubuntu runner.

```bash
docker compose up --build
```

Services:

- Frontend: http://localhost:3000
- Backend: http://localhost:8000

Environment variables can be placed in `.env`:

```bash
DIFY_BASE_URL=https://api.dify.ai/v1
DIFY_API_KEY=
JUDGE0_BASE_URL=
JUDGE0_API_KEY=
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
SQLITE_DB_PATH=/data/aieduagent.db
```

## Notes

- The backend uses SQLite for MVP persistence.
- Dify and Judge0 are optional; the app falls back safely when they are not configured.
- Do not commit `.env` or local database files.
