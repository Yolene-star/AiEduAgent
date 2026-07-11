import unittest

from app.core.stages import Stage
from app.main import (
    chat,
    courses,
    create_student_session,
    generate_quiz,
    learning_path,
    submit_quiz,
    tts_loopback,
)
from app.models import (
    ChatRequest,
    QuizGenerateRequest,
    QuizSubmitRequest,
    StudentSessionCreate,
    TTSLoopbackRequest,
)


class LearningBehaviorTests(unittest.TestCase):
    def test_mvp_learning_behavior(self) -> None:
        session = create_student_session(StudentSessionCreate(stage=Stage.middle_school))
        course = courses("middle_school")
        first_point = course.knowledge_points[0]

        chat_response = chat(
            ChatRequest(
                session_id=session.session_id,
                message="机器怎么知道猫和狗不一样？",
                knowledge_point_id=str(first_point["id"]),
            )
        )
        self.assertIn("初中", chat_response.answer)

        tts_response = tts_loopback(
            TTSLoopbackRequest(stage=Stage.middle_school, text=chat_response.answer)
        )
        self.assertTrue(tts_response.passed)

        quiz_response = generate_quiz(
            QuizGenerateRequest(session_id=session.session_id, knowledge_point_id="train-test")
        )
        question = quiz_response["questions"][0]

        submit_response = submit_quiz(
            QuizSubmitRequest(
                session_id=session.session_id,
                question_id=str(question["id"]),
                answer=str(question["answer"]),
            )
        )
        self.assertTrue(submit_response.correct)

        recommendation_response = learning_path(session.session_id)
        self.assertTrue(recommendation_response.reason)


if __name__ == "__main__":
    unittest.main()
