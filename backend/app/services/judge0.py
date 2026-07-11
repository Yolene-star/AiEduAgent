import httpx

from app.core.config import get_settings


PYTHON_LANGUAGE_ID = 71


class Judge0Client:
    def __init__(self) -> None:
        self.settings = get_settings()

    def is_configured(self) -> bool:
        return bool(self.settings.judge0_base_url)

    def run_python(self, code: str) -> tuple[str, str, str]:
        if not self.is_configured():
            return "ok", "示例运行完成", "MVP 未配置 Judge0，已使用安全演示结果。"
        try:
            return self._request_judge0(code)
        except (httpx.HTTPError, ImportError, KeyError, ValueError):
            return "fallback", "", "Judge0 暂不可用，系统已保留代码并给出分级提示。"

    def _request_judge0(self, code: str) -> tuple[str, str, str]:
        url = self.settings.judge0_base_url.rstrip("/") + "/submissions"
        headers = {"Content-Type": "application/json"}
        if self.settings.judge0_api_key:
            headers["X-Auth-Token"] = self.settings.judge0_api_key
        payload = {
            "language_id": PYTHON_LANGUAGE_ID,
            "source_code": code,
            "stdin": "",
        }
        with httpx.Client(timeout=self.settings.judge0_timeout_seconds) as client:
            response = client.post(url, params={"base64_encoded": "false", "wait": "true"}, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()

        status = str(data.get("status", {}).get("description", "Unknown"))
        stdout = str(data.get("stdout") or "")
        stderr = str(data.get("stderr") or data.get("compile_output") or "")
        if status.lower() == "accepted":
            return "ok", stdout.strip() or "程序运行完成，但没有输出。", "代码运行成功。"
        return "error", stderr.strip() or status, "代码没有通过运行，请先看错误类型，再逐步定位。"


judge0_client = Judge0Client()
