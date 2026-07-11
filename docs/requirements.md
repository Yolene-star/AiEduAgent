# Requirements

## Project Goal

Build a K12 AI literacy teaching assistant for four stages:

- lower primary
- upper primary
- middle school
- high school

The system must show that the same AI concept changes by stage in:

- learning goal
- language style
- interaction type
- quiz difficulty
- feedback strategy

## MVP Learning Loop

```text
choose stage -> load course -> ask AI -> TTS loopback
-> generate quiz -> submit answer -> update mastery
-> recommend next action -> optional animation/code practice
```

## MVP Feature Requirements

- Stage selection.
- Course path for “人工智能如何学会分类”.
- Stage-adaptive chat through Dify with local fallback.
- SQLite persistence for sessions, messages, mastery, and quiz attempts.
- Quiz generation and grading.
- Mastery-based recommendation.
- Mock TTS loopback and browser speech playback.
- Classification animation.
- Python code runner through Judge0 adapter with safe fallback.
- Teacher analytics dashboard.

## Quality Gates

Every feature must pass:

- backend unit/API tests
- frontend component tests
- Playwright behavior tests where UI is affected
- TTS loopback tests for user-facing instructional text
- open-source reference and license notes when applicable
