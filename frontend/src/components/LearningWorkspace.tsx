"use client";

import { useEffect, useMemo, useState } from "react";
import { api, AnimationResponse, Course, QuizQuestion, Stage, StudentSession } from "@/lib/api";
import { ClassificationAnimation } from "./ClassificationAnimation";
import { SpeechButton } from "./SpeechButton";
import { CodeRunner } from "./CodeRunner";

const stages: { id: Stage; label: string }[] = [
  { id: "lower_primary", label: "小学低年级" },
  { id: "upper_primary", label: "小学高年级" },
  { id: "middle_school", label: "初中" },
  { id: "high_school", label: "高中" }
];

export function LearningWorkspace() {
  const [health, setHealth] = useState("检查中");
  const [stage, setStage] = useState<Stage>("upper_primary");
  const [session, setSession] = useState<StudentSession | null>(null);
  const [course, setCourse] = useState<Course | null>(null);
  const [selectedPointId, setSelectedPointId] = useState("classification");
  const [message, setMessage] = useState("机器怎么学会分类？");
  const [answer, setAnswer] = useState("选择学段后，可以开始和 AI 教学助手对话。");
  const [ttsStatus, setTtsStatus] = useState("待测试");
  const [quiz, setQuiz] = useState<QuizQuestion | null>(null);
  const [quizResult, setQuizResult] = useState("尚未答题");
  const [recommendation, setRecommendation] = useState("完成练习后生成推荐。");
  const [animation, setAnimation] = useState<AnimationResponse | null>(null);
  const [animationStep, setAnimationStep] = useState(0);
  const [busy, setBusy] = useState(false);

  const selectedPoint = useMemo(
    () => course?.knowledge_points.find((item) => item.id === selectedPointId),
    [course, selectedPointId]
  );

  useEffect(() => {
    api
      .health()
      .then((data) => setHealth(`${data.service} ${data.version} 已连接`))
      .catch(() => setHealth("后端未连接"));
  }, []);

  async function startLearning(nextStage = stage) {
    setBusy(true);
    try {
      const created = await api.createSession(nextStage);
      const loadedCourse = await api.course(nextStage);
      setStage(nextStage);
      setSession(created);
      setCourse(loadedCourse);
      setSelectedPointId(loadedCourse.knowledge_points[0]?.id ?? "classification");
      setAnswer(created.welcome_message);
      const tts = await api.ttsLoopback(nextStage, created.welcome_message);
      setTtsStatus(tts.passed ? `TTS 回环通过，相似度 ${tts.similarity}` : "TTS 回环未通过");
    } catch (error) {
      setAnswer("启动学习失败，请确认后端服务是否运行。");
    } finally {
      setBusy(false);
    }
  }

  async function askQuestion() {
    if (!session) {
      await startLearning(stage);
      return;
    }
    setBusy(true);
    try {
      const response = await api.chat(session.session_id, message, selectedPointId);
      setAnswer(response.answer);
      const tts = await api.ttsLoopback(stage, response.answer);
      setTtsStatus(tts.passed ? `TTS 回环通过，相似度 ${tts.similarity}` : "TTS 回环未通过");
    } catch {
      setAnswer("AI 回答暂时不可用，已保留问题，请稍后重试。");
    } finally {
      setBusy(false);
    }
  }

  async function loadQuiz() {
    if (!session) return;
    setBusy(true);
    try {
      const response = await api.generateQuiz(session.session_id, selectedPointId);
      setQuiz(response.questions[0]);
      setQuizResult("请选择一个答案。");
    } finally {
      setBusy(false);
    }
  }

  async function loadAnimation() {
    setBusy(true);
    try {
      const response = await api.animation();
      setAnimation(response);
      setAnimationStep(0);
      if (response.steps[0]) {
        await api.ttsLoopback(stage, response.steps[0].narration);
        setTtsStatus("动画旁白 TTS 回环通过");
      }
    } finally {
      setBusy(false);
    }
  }

  async function submitAnswer(answerText: string) {
    if (!session || !quiz) return;
    setBusy(true);
    try {
      const result = await api.submitQuiz(session.session_id, quiz.id, answerText);
      setQuizResult(`${result.feedback} ${result.explanation} 当前掌握度：${result.mastery}`);
      const next = await api.recommendation(session.session_id);
      setRecommendation(`${next.reason} 预计 ${next.estimated_minutes} 分钟。`);
      await api.ttsLoopback(stage, `${result.feedback} ${next.reason}`);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="brand">
          <strong>AiEduAgent</strong>
          <span>多模态 K12 人工智能通识课教学助手</span>
        </div>
        <div className={health.includes("已连接") ? "status ok" : "status warn"}>{health}</div>
      </header>

      <section className="workspace">
        <aside className="panel">
          <h2>学段</h2>
          <div className="stage-list">
            {stages.map((item) => (
              <button
                key={item.id}
                className={stage === item.id ? "selected" : ""}
                disabled={busy}
                onClick={() => startLearning(item.id)}
              >
                {item.label}
              </button>
            ))}
          </div>
          <h2 style={{ marginTop: 20 }}>课程路径</h2>
          <div className="knowledge-list">
            {(course?.knowledge_points ?? []).map((item) => (
              <button
                className={selectedPointId === item.id ? "knowledge-item selected" : "knowledge-item"}
                key={item.id}
                onClick={() => setSelectedPointId(item.id)}
              >
                <strong>{item.title}</strong>
                <span>{item.goal}</span>
              </button>
            ))}
          </div>
        </aside>

        <section className="panel chat-box">
          <h2>{course?.title ?? "开始学习"}</h2>
          <p>{selectedPoint?.intro ?? "请选择一个学段载入课程。"}</p>
          <div className="answer" aria-live="polite">{answer}</div>
          <SpeechButton text={answer} />
          <div className="chat-input">
            <input
              aria-label="输入问题"
              value={message}
              onChange={(event) => setMessage(event.target.value)}
            />
            <button className="primary" disabled={busy} onClick={askQuestion}>
              提问
            </button>
          </div>
          <button disabled={!session || busy} onClick={loadQuiz}>
            生成练习
          </button>
          <button disabled={busy} onClick={loadAnimation}>
            动画讲解
          </button>
          <ClassificationAnimation
            animation={animation}
            currentStep={animationStep}
            onStepChange={async (step) => {
              setAnimationStep(step);
              const narration = animation?.steps[step]?.narration;
              if (narration) {
                await api.ttsLoopback(stage, narration);
              }
            }}
          />
          {quiz ? (
            <div>
              <h2>{quiz.prompt}</h2>
              <div className="quiz-options">
                {quiz.options.map((option) => (
                  <button key={option} disabled={busy} onClick={() => submitAnswer(option)}>
                    {option}
                  </button>
                ))}
              </div>
            </div>
          ) : null}
          <CodeRunner sessionId={session?.session_id ?? null} />
        </section>

        <aside className="panel meta-grid">
          <h2>学习反馈</h2>
          <div className="metric">
            <span>当前会话</span>
            <strong>{session?.stage_label ?? "未开始"}</strong>
          </div>
          <div className="metric">
            <span>TTS 回环</span>
            <strong>{ttsStatus}</strong>
          </div>
          <div className="metric">
            <span>练习反馈</span>
            <strong>{quizResult}</strong>
          </div>
          <div className="metric">
            <span>下一步</span>
            <strong>{recommendation}</strong>
          </div>
        </aside>
      </section>
    </main>
  );
}
