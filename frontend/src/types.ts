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
  sources: SourceLink[]
  lesson_state: string
  next_lesson_state: string
  teaching_form: string
  stage_policy_label: string
  format_warnings: string[]
}

export interface SourceLink {
  card_id: string
  title: string
  url: string
}

export type QuizType = 'multiple_choice' | 'true_false' | 'ordering'

export interface QuizOption {
  id: string
  text: string
}

export interface QuizQuestion {
  id: string
  stage: Stage
  card_id: string
  quiz_type: QuizType
  prompt: string
  options: QuizOption[]
  items: QuizOption[]
  review_card_id: string
}

export interface QuizSubmitResponse {
  question_id: string
  correct: boolean
  explanation: string
  error_type: string
  review_card_id: string
  next_actions: string[]
  already_recorded: boolean
}
