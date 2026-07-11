import unittest

from app.core.stages import Stage
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
        self.assertGreaterEqual(len(course.knowledge_points), 4)
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


if __name__ == "__main__":
    unittest.main()
