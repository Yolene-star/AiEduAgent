# Open Source Reference Map

The system uses open source projects as references, not as copied product code.

## MVP modules

- Backend API: FastAPI route and Pydantic model structure.
- Frontend UI: Next.js App Router and React component structure.
- AI/RAG: Dify API adapter, with local fallback for development and tests.
- Behavior tests: Playwright test style and trace workflow.
- TTS loopback: Mock provider first; Coqui TTS may be evaluated later.
- Curriculum: Microsoft AI-Edu-inspired topic sequence, rewritten for K12 stages.
- Product flow: LearnHouse-inspired course/progress structure, implemented from scratch.

## Compliance rules

- Do not copy code from repositories with unclear or restrictive licenses.
- Keep GPL/AGPL systems behind service boundaries if adopted later.
- Keep API keys in environment variables only.
- Record every new dependency or copied snippet in `THIRD_PARTY_NOTICES.md`.
