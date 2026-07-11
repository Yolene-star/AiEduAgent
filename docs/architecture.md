# Architecture

## System Layers

```text
Next.js frontend
  -> FastAPI backend
    -> SQLite persistence
    -> Dify adapter
    -> Judge0 adapter
    -> Mock TTS loopback
```

## Frontend

- `LearningWorkspace`: student learning flow.
- `TeacherDashboard`: teacher analytics.
- `ClassificationAnimation`: state-sequence animation inspired by Algorithm Visualizer.
- `CodeRunner`: Python practice UI.
- `SpeechButton`: browser Web Speech playback.

## Backend

- `/api/students/session`: creates a stage-specific learning session.
- `/api/courses`: returns stage-adaptive course content.
- `/api/chat`: proxies Dify or uses local fallback.
- `/api/quizzes/generate`: returns stage-matched quiz items.
- `/api/quizzes/submit`: grades answers and updates mastery.
- `/api/learning-path`: recommends the next task.
- `/api/tts/loopback-test`: validates text for speech playback.
- `/api/animations/classification`: returns animation state sequence.
- `/api/code/run`: uses Judge0 when configured, safe fallback otherwise.
- `/api/teacher/analytics`: summarizes weak knowledge points.

## Persistence

SQLite stores:

- sessions
- mastery
- messages
- quiz_attempts

The database path defaults to `backend/aieduagent.db` and can be overridden by `SQLITE_DB_PATH`.
