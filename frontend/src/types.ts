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

export type ResourceType = 'link' | 'document' | 'ppt' | 'video' | 'image' | 'knowledge_card' | 'quiz'

export interface CourseResourceCreate {
  title: string
  resource_type: ResourceType
  stage?: Stage | null
  unit: string
  topic: string
  source_url?: string | null
  license: string
  description: string
  card_ids: string[]
  created_by: string
}

export interface CourseResourceResponse extends CourseResourceCreate {
  id: string
  status: 'draft' | 'pending_review'
  created_at: string
}

export type AnimationVisual = 'image-card' | 'pixel-grid' | 'feature-lines' | 'score-bars' | 'label-badge'

export interface AnimationStep {
  id: string
  title: string
  caption: string
  visual: AnimationVisual
}

export interface AnimationSpec {
  id: string
  title: string
  concept_id: string
  template: 'image_classification_process'
  version: number
  subtitle: string
  steps: AnimationStep[]
  allowed_controls: string[]
  license: string
}

export interface StorybookPage {
  page: number
  title: string
  image: string
  alt: string
  narration: string
  dialogue: string
  question: string
}

export interface StorybookSpec {
  id: string
  title: string
  stage: Stage
  concept_id: string
  version: number
  recommended_by_default: boolean
  pages: StorybookPage[]
  license: string
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
