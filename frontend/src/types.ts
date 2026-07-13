export type Stage = 'lower_primary' | 'upper_primary' | 'middle_school' | 'high_school'

export interface ChatRequest {
  stage: Stage
  message: string
}

export interface ChatResponse {
  answer: string
  check_question: string
  used_card_ids: string[]
  next_actions: string[]
}
