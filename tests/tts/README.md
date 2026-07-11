# TTS Loopback Tests

TTS loopback tests verify user-facing text can be spoken and understood.

MVP uses a mock loopback:

```text
text -> MockTTS audio token -> MockSTT text -> similarity and safety checks
```

The backend endpoint is:

```text
POST /api/tts/loopback-test
```

It checks:

- text is not empty
- text is stage-appropriate
- no blocked unsafe terms are present
- loopback similarity passes the threshold
