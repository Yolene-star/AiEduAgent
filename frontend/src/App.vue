<script setup lang="ts">
import { ref } from 'vue'

import { sendChat } from './api'
import AnswerCard from './components/AnswerCard.vue'
import ChatInput from './components/ChatInput.vue'
import SourceList from './components/SourceList.vue'
import StageSelector from './components/StageSelector.vue'
import type { ChatResponse, Stage } from './types'

const stage = ref<Stage>('lower_primary')
const message = ref('AI怎么认识小猫？')
const answer = ref<ChatResponse | null>(null)
const isLoading = ref(false)
const errorMessage = ref('')

async function submitQuestion() {
  errorMessage.value = ''
  answer.value = null
  isLoading.value = true

  try {
    answer.value = await sendChat({ stage: stage.value, message: message.value })
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '请求失败，请确认后端已启动。'
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <main class="app-shell">
    <section class="workspace" aria-labelledby="page-title">
      <div class="header-row">
        <div>
          <p class="eyebrow">阶段 2</p>
          <h1 id="page-title">K12 AI 教学助手</h1>
        </div>
        <StageSelector v-model="stage" />
      </div>

      <ChatInput v-model="message" :loading="isLoading" @submit="submitQuestion" />

      <p v-if="isLoading" class="status" role="status">正在请求后端...</p>
      <p v-if="errorMessage" class="error" role="alert">{{ errorMessage }}</p>

      <AnswerCard v-if="answer" :answer="answer" />
      <SourceList v-if="answer" :card-ids="answer.used_card_ids" />
    </section>
  </main>
</template>
