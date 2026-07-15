import type { ChatRequest, ChatResponse, QuizQuestion, QuizSubmitResponse, Stage } from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000'

export async function sendChat(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/chat`, {
    method: 'POST',
    headers: {
      'content-type': 'application/json'
    },
    body: JSON.stringify(request)
  })

  if (!response.ok) {
    throw new Error(`请求失败：HTTP ${response.status}`)
  }

  return response.json() as Promise<ChatResponse>
}

export async function fetchQuizzes(stage: Stage): Promise<QuizQuestion[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/quizzes?stage=${stage}`)

  if (!response.ok) {
    throw new Error(`题库请求失败：HTTP ${response.status}`)
  }

  return response.json() as Promise<QuizQuestion[]>
}

export async function submitQuiz(
  quizId: string,
  answer: string | boolean | string[],
  idempotencyKey: string
): Promise<QuizSubmitResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/quiz/${quizId}/submit`, {
    method: 'POST',
    headers: {
      'content-type': 'application/json'
    },
    body: JSON.stringify({
      student_id: 'demo-student',
      answer,
      hints_used: 0,
      elapsed_ms: 0,
      idempotency_key: idempotencyKey
    })
  })

  if (!response.ok) {
    throw new Error(`提交失败：HTTP ${response.status}`)
  }

  return response.json() as Promise<QuizSubmitResponse>
}
