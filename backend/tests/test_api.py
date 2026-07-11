import unittest
from unittest.mock import Mock, patch

from app.core.stages import Stage
from app.services.dify import DifyClient
from app.services.judge0 import Judge0Client
from app.main import (
    chat,
    courses,
    create_student_session,
    classification_animation,
    generate_quiz,
    health,
    learning_path,
    mastery,
    submit_quiz,
    system_info,
    teacher_analytics,
    tts_loopback,
    run_code,
)
from app.services.store import store
from app.models import (
    ChatRequest,
    QuizGenerateRequest,
    QuizSubmitRequest,
    CodeRunRequest,
    StudentSessionCreate,
    TTSLoopbackRequest,
)


class ApiTests(unittest.TestCase):
    def create_session(self, stage: Stage = Stage.upper_primary) -> str:
        response = create_student_session(StudentSessionCreate(stage=stage, interest="robot"))
        self.assertTrue(response.session_id)
        return response.session_id

    def test_health_and_system_info(self) -> None:
        self.assertEqual(health().status, "ok")
        self.assertEqual(system_info().tts_provider, "mock-loopback")

    def test_student_session_and_courses(self) -> None:
        session_id = self.create_session(Stage.lower_primary)
        self.assertTrue(session_id)

        course = courses("lower_primary")
        self.assertEqual(course.id, "ai-classification")
        self.assertGreaterEqual(len(course.knowledge_points), 10)
        self.assertIn("整理玩具", str(course.knowledge_points[0]["intro"]))

    def test_chat_uses_stage_adaptive_fallback(self) -> None:
        lower_session = self.create_session(Stage.lower_primary)
        high_session = self.create_session(Stage.high_school)

        lower = chat(
            ChatRequest(
                session_id=lower_session,
                message="什么是分类？",
                knowledge_point_id="classification",
            )
        )
        high = chat(
            ChatRequest(
                session_id=high_session,
                message="什么是分类？",
                knowledge_point_id="classification",
            )
        )

        self.assertIn("小学低年级", lower.answer)
        self.assertIn("高中", high.answer)
        self.assertIn("特征", high.answer)

    def test_dify_client_uses_real_api_when_configured(self) -> None:
        client = DifyClient()
        old_key = client.settings.dify_api_key
        old_base_url = client.settings.dify_base_url
        client.settings.dify_api_key = "test-key"
        client.settings.dify_base_url = "https://dify.example/v1"

        mock_response = Mock()
        mock_response.json.return_value = {"answer": "来自 Dify 的适龄回答。"}
        mock_response.raise_for_status.return_value = None

        try:
            with patch("app.services.dify.httpx.Client") as mock_client:
                mock_client.return_value.__enter__.return_value.post.return_value = mock_response
                answer, source = client.generate_answer(Stage.upper_primary, "什么是分类？", "classification")
        finally:
            client.settings.dify_api_key = old_key
            client.settings.dify_base_url = old_base_url

        self.assertEqual(source, "dify")
        self.assertEqual(answer, "来自 Dify 的适龄回答。")
        call = mock_client.return_value.__enter__.return_value.post.call_args
        self.assertEqual(call.kwargs["headers"]["Authorization"], "Bearer test-key")
        self.assertEqual(call.kwargs["json"]["inputs"]["stage"], "小学高年级")

    def test_dify_client_falls_back_when_api_fails(self) -> None:
        client = DifyClient()
        old_key = client.settings.dify_api_key
        client.settings.dify_api_key = "test-key"

        try:
            with patch("app.services.dify.httpx.Client") as mock_client:
                mock_client.return_value.__enter__.return_value.post.side_effect = http_error()
                answer, source = client.generate_answer(Stage.lower_primary, "什么是分类？", "classification")
        finally:
            client.settings.dify_api_key = old_key

        self.assertEqual(source, "dify-error-fallback")
        self.assertIn("小学低年级", answer)

    def test_quiz_mastery_and_recommendation_flow(self) -> None:
        session_id = self.create_session(Stage.upper_primary)
        quiz = generate_quiz(QuizGenerateRequest(session_id=session_id, knowledge_point_id="features"))
        question = quiz["questions"][0]

        result = submit_quiz(
            QuizSubmitRequest(
                session_id=session_id,
                question_id=str(question["id"]),
                answer=str(question["answer"]),
            )
        )
        self.assertTrue(result.correct)
        self.assertGreater(result.mastery, 20)

        mastery_result = mastery(session_id)
        self.assertIn("features", mastery_result.mastery)

        recommendation = learning_path(session_id)
        self.assertTrue(recommendation.reason)

    def test_sqlite_persists_messages_mastery_and_quiz_attempts(self) -> None:
        session_id = self.create_session(Stage.high_school)
        chat(
            ChatRequest(
                session_id=session_id,
                message="什么是训练集？",
                knowledge_point_id="train-test",
            )
        )
        quiz = generate_quiz(QuizGenerateRequest(session_id=session_id, knowledge_point_id="simple-classifier"))
        question = quiz["questions"][0]
        submit_quiz(
            QuizSubmitRequest(
                session_id=session_id,
                question_id=str(question["id"]),
                answer=str(question["answer"]),
            )
        )

        reloaded = store.require_session(session_id)
        self.assertGreaterEqual(len(reloaded.messages), 2)
        self.assertGreater(reloaded.mastery["simple-classifier"], 0)
        with store.connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS count FROM quiz_attempts WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        self.assertEqual(int(row["count"]), 1)

    def test_tts_loopback(self) -> None:
        response = tts_loopback(TTSLoopbackRequest(stage=Stage.lower_primary, text="分类就像整理玩具。"))
        self.assertTrue(response.passed)
        self.assertGreaterEqual(response.similarity, 0.95)

    def test_animation_teacher_and_code_extension_points(self) -> None:
        session_id = self.create_session(Stage.high_school)
        animation = classification_animation()
        self.assertEqual(animation.id, "classification-features")
        self.assertGreaterEqual(len(animation.steps), 3)
        for step in animation.steps:
            loopback = tts_loopback(TTSLoopbackRequest(stage=Stage.upper_primary, text=step.narration))
            self.assertTrue(loopback.passed)

        analytics = teacher_analytics()
        self.assertGreaterEqual(analytics.total_sessions, 1)

        code_result = run_code(
            CodeRunRequest(session_id=session_id, language="python", code="print('hello classifier')")
        )
        self.assertEqual(code_result.status, "ok")

    def test_judge0_client_uses_real_api_when_configured(self) -> None:
        client = Judge0Client()
        old_base_url = client.settings.judge0_base_url
        old_key = client.settings.judge0_api_key
        client.settings.judge0_base_url = "https://judge0.example"
        client.settings.judge0_api_key = "judge-key"

        mock_response = Mock()
        mock_response.json.return_value = {
            "status": {"description": "Accepted"},
            "stdout": "hello\n",
            "stderr": None,
            "compile_output": None,
        }
        mock_response.raise_for_status.return_value = None

        try:
            with patch("app.services.judge0.httpx.Client") as mock_client:
                mock_client.return_value.__enter__.return_value.post.return_value = mock_response
                status, output, feedback = client.run_python("print('hello')")
        finally:
            client.settings.judge0_base_url = old_base_url
            client.settings.judge0_api_key = old_key

        self.assertEqual(status, "ok")
        self.assertEqual(output, "hello")
        self.assertIn("成功", feedback)

    def test_judge0_client_falls_back_when_api_fails(self) -> None:
        client = Judge0Client()
        old_base_url = client.settings.judge0_base_url
        client.settings.judge0_base_url = "https://judge0.example"
        try:
            with patch("app.services.judge0.httpx.Client") as mock_client:
                mock_client.return_value.__enter__.return_value.post.side_effect = http_error()
                status, _, feedback = client.run_python("print('hello')")
        finally:
            client.settings.judge0_base_url = old_base_url
        self.assertEqual(status, "fallback")
        self.assertIn("Judge0", feedback)


if __name__ == "__main__":
    unittest.main()


def http_error():
    import httpx

    return httpx.ConnectError("network unavailable")
