export type Stage = "lower_primary" | "upper_primary" | "middle_school" | "high_school";

export type StudentSession = {
  session_id: string;
  stage: Stage;
  stage_label: string;
  welcome_message: string;
};

export type KnowledgePoint = {
  id: string;
  title: string;
  order: number;
  prerequisites: string[];
  goal: string;
  intro: string;
};

export type Course = {
  id: string;
  title: string;
  summary: string;
  stage: Stage;
  knowledge_points: KnowledgePoint[];
};

export type ChatResponse = {
  answer: string;
  stage: Stage;
  knowledge_point_id: string;
  citations: { title: string; source: string }[];
  model_source: string;
};

export type QuizQuestion = {
  id: string;
  knowledge_point_id: string;
  type: string;
  prompt: string;
  options: string[];
  answer: string;
  explanation: string;
};

export type AnimationStep = {
  id: string;
  title: string;
  narration: string;
  highlighted_features: string[];
  category: string;
};

export type AnimationResponse = {
  id: string;
  title: string;
  reference: string;
  steps: AnimationStep[];
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    }
  });
  if (!response.ok) {
    throw new Error(`Request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; service: string; version: string }>("/health"),
  createSession: (stage: Stage) =>
    request<StudentSession>("/api/students/session", {
      method: "POST",
      body: JSON.stringify({ stage })
    }),
  course: (stage: Stage) => request<Course>(`/api/courses?stage=${stage}`),
  chat: (sessionId: string, message: string, knowledgePointId: string) =>
    request<ChatResponse>("/api/chat", {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        message,
        knowledge_point_id: knowledgePointId
      })
    }),
  ttsLoopback: (stage: Stage, text: string) =>
    request<{ passed: boolean; similarity: number; notes: string[] }>("/api/tts/loopback-test", {
      method: "POST",
      body: JSON.stringify({ stage, text })
    }),
  generateQuiz: (sessionId: string, knowledgePointId: string) =>
    request<{ questions: QuizQuestion[] }>("/api/quizzes/generate", {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        knowledge_point_id: knowledgePointId
      })
    }),
  submitQuiz: (sessionId: string, questionId: string, answer: string) =>
    request<{ correct: boolean; explanation: string; mastery: number; feedback: string }>(
      "/api/quizzes/submit",
      {
        method: "POST",
        body: JSON.stringify({
          session_id: sessionId,
          question_id: questionId,
          answer
        })
      }
    ),
  recommendation: (sessionId: string) =>
    request<{ next_action: string; knowledge_point_id: string; reason: string; estimated_minutes: number }>(
      `/api/learning-path?session_id=${sessionId}`
    ),
  animation: () => request<AnimationResponse>("/api/animations/classification")
};
