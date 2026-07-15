# DeepSeek Compatibility Notes

Checked on 2026-07-15 against official DeepSeek API docs.

Recommended local environment:

```bash
MODEL_PROVIDER=real
LLM_MODEL=deepseek-v4-flash
LLM_BASE_URL=https://api.deepseek.com
LLM_API_KEY=<local secret, never commit>
LLM_TIMEOUT_SECONDS=20
```

Compatibility updates:

- RealModelProvider uses `/chat/completions`, which matches DeepSeek's OpenAI-compatible API.
- Payload includes `response_format: {"type": "json_object"}`.
- System prompt now includes lowercase `json` and an example json object, matching DeepSeek JSON Output guidance.
- Payload sets `max_tokens: 800` to reduce truncated JSON risk.
- Provider maps empty content to `empty_content` and HTTP errors to `http_error` with safe detail.
- `scripts/check_model_provider.py` can test the configured provider without printing the API key.

Useful command:

```bash
MODEL_PROVIDER=real \
LLM_MODEL=deepseek-v4-flash \
LLM_API_KEY=<your key> \
LLM_BASE_URL=https://api.deepseek.com \
LLM_TIMEOUT_SECONDS=20 \
conda run -n aieduagent-py312 python scripts/check_model_provider.py
```
