$ErrorActionPreference = "Stop"

conda run -n aieduagent-py312 python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
