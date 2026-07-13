<script setup lang="ts">
defineProps<{
  loading: boolean
}>()

const emit = defineEmits<{
  submit: []
}>()

const model = defineModel<string>({ required: true })
</script>

<template>
  <form class="chat-form" @submit.prevent="emit('submit')">
    <label class="field">
      <span>问题</span>
      <textarea v-model="model" rows="4" :disabled="loading" aria-label="输入问题" />
    </label>
    <button type="submit" :disabled="loading || model.trim().length === 0">
      {{ loading ? '发送中' : '发送' }}
    </button>
  </form>
</template>
