<script setup lang="ts">
import type { ChatResponse } from '../types'

defineProps<{
  answer: ChatResponse
}>()
</script>

<template>
  <article class="answer-card">
    <h2>回答</h2>
    <p>{{ answer.answer }}</p>
    <h3>检查题</h3>
    <p>{{ answer.check_question }}</p>
    <h3>下一步</h3>
    <ul>
      <li v-for="action in answer.next_actions" :key="action">{{ action }}</li>
    </ul>
  </article>
</template>
