# Testing Policy

Every feature must include:

- API or unit tests.
- User behavior tests.
- TTS loopback tests for user-facing generated text.
- Failure-mode tests for AI, TTS, and network degradation where applicable.
- A third-party reference note when existing GitHub projects informed the design.

Feature work is not accepted until the following checks pass:

```text
backend unit/API tests
frontend component tests
behavior tests or documented behavior test fixture
TTS loopback tests
manual acceptance note for UI-heavy work
third-party reference note
```
