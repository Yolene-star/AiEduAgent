<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import { fetchQuizzes, submitQuiz } from '../api'
import type { QuizQuestion, QuizSubmitResponse, Stage } from '../types'

const props = defineProps<{
  stage: Stage
}>()

const quizzes = ref<QuizQuestion[]>([])
const selectedQuizId = ref('')
const choiceAnswer = ref('')
const booleanAnswer = ref('true')
const orderingAnswer = ref<string[]>([])
const feedback = ref<QuizSubmitResponse | null>(null)
const isLoading = ref(false)
const isSubmitting = ref(false)
const errorMessage = ref('')

const currentQuiz = computed(() => quizzes.value.find((quiz) => quiz.id === selectedQuizId.value) ?? null)

function newIdempotencyKey() {
  return globalThis.crypto?.randomUUID?.() ?? `quiz-${Date.now()}-${Math.random()}`
}

async function loadStageQuizzes() {
  isLoading.value = true
  errorMessage.value = ''
  feedback.value = null

  try {
    quizzes.value = await fetchQuizzes(props.stage)
    selectedQuizId.value = quizzes.value[0]?.id ?? ''
    resetAnswer()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '题库加载失败。'
  } finally {
    isLoading.value = false
  }
}

function resetAnswer() {
  feedback.value = null
  choiceAnswer.value = currentQuiz.value?.options[0]?.id ?? ''
  booleanAnswer.value = 'true'
  orderingAnswer.value = currentQuiz.value?.items.map((item) => item.id) ?? []
}

async function submitCurrentQuiz() {
  if (!currentQuiz.value) {
    return
  }

  isSubmitting.value = true
  errorMessage.value = ''

  const answer =
    currentQuiz.value.quiz_type === 'true_false'
      ? booleanAnswer.value === 'true'
      : currentQuiz.value.quiz_type === 'ordering'
        ? orderingAnswer.value
        : choiceAnswer.value

  try {
    feedback.value = await submitQuiz(currentQuiz.value.id, answer, newIdempotencyKey())
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '提交失败。'
  } finally {
    isSubmitting.value = false
  }
}

watch(() => props.stage, loadStageQuizzes)
watch(selectedQuizId, resetAnswer)
onMounted(loadStageQuizzes)
</script>

<template>
  <section class="quiz-panel" aria-labelledby="quiz-title">
    <div class="section-heading">
      <div>
        <p class="eyebrow">阶段 6</p>
        <h2 id="quiz-title">游戏化练习</h2>
      </div>
      <select v-model="selectedQuizId" :disabled="isLoading || quizzes.length === 0" aria-label="选择题目">
        <option v-for="quiz in quizzes" :key="quiz.id" :value="quiz.id">
          {{ quiz.card_id }} · {{ quiz.quiz_type }}
        </option>
      </select>
    </div>

    <p v-if="isLoading" class="status" role="status">正在加载固定题库...</p>
    <p v-if="errorMessage" class="error" role="alert">{{ errorMessage }}</p>

    <form v-if="currentQuiz" class="quiz-form" @submit.prevent="submitCurrentQuiz">
      <p class="meta">{{ currentQuiz.id }}</p>
      <h3>{{ currentQuiz.prompt }}</h3>

      <div v-if="currentQuiz.quiz_type === 'multiple_choice'" class="choice-list">
        <label v-for="option in currentQuiz.options" :key="option.id">
          <input v-model="choiceAnswer" type="radio" name="choice-answer" :value="option.id" />
          <span>{{ option.id }}. {{ option.text }}</span>
        </label>
      </div>

      <div v-else-if="currentQuiz.quiz_type === 'true_false'" class="choice-list">
        <label>
          <input v-model="booleanAnswer" type="radio" name="boolean-answer" value="true" />
          <span>正确</span>
        </label>
        <label>
          <input v-model="booleanAnswer" type="radio" name="boolean-answer" value="false" />
          <span>错误</span>
        </label>
      </div>

      <div v-else class="ordering-list">
        <label v-for="(_, index) in orderingAnswer" :key="index">
          <span>第 {{ index + 1 }} 步</span>
          <select v-model="orderingAnswer[index]">
            <option v-for="item in currentQuiz.items" :key="item.id" :value="item.id">
              {{ item.id }}. {{ item.text }}
            </option>
          </select>
        </label>
      </div>

      <button type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? '批改中...' : '提交练习' }}
      </button>
    </form>

    <article v-if="feedback" class="feedback-card" aria-label="练习反馈">
      <h3>{{ feedback.correct ? '回答正确' : '继续加油' }}</h3>
      <p>{{ feedback.explanation }}</p>
      <p class="meta">错因：{{ feedback.error_type }} · 回看：{{ feedback.review_card_id }}</p>
      <p v-if="feedback.already_recorded" class="meta">已识别重复提交，本次没有重复计分。</p>
    </article>
  </section>
</template>
