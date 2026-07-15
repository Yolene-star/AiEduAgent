<script setup lang="ts">
import { computed, onBeforeUnmount, ref } from 'vue'

const props = defineProps<{
  text: string
}>()

const isSpeaking = ref(false)
const isPaused = ref(false)
const rate = ref(1)
const speechError = ref('')

const canSpeak = computed(() => typeof window !== 'undefined' && 'speechSynthesis' in window)

function stopSpeech() {
  if (!canSpeak.value) {
    return
  }
  window.speechSynthesis.cancel()
  isSpeaking.value = false
  isPaused.value = false
}

function playSpeech() {
  speechError.value = ''
  if (!canSpeak.value) {
    speechError.value = '当前浏览器不支持语音播放，文本仍可正常阅读。'
    return
  }

  stopSpeech()
  const utterance = new SpeechSynthesisUtterance(props.text)
  utterance.lang = 'zh-CN'
  utterance.rate = rate.value
  utterance.onend = () => {
    isSpeaking.value = false
    isPaused.value = false
  }
  utterance.onerror = () => {
    speechError.value = '语音播放失败，文本仍可正常阅读。'
    isSpeaking.value = false
    isPaused.value = false
  }
  window.speechSynthesis.speak(utterance)
  isSpeaking.value = true
}

function pauseSpeech() {
  if (!canSpeak.value || !isSpeaking.value) {
    return
  }
  window.speechSynthesis.pause()
  isPaused.value = true
}

function resumeSpeech() {
  if (!canSpeak.value || !isSpeaking.value) {
    return
  }
  window.speechSynthesis.resume()
  isPaused.value = false
}

onBeforeUnmount(stopSpeech)
</script>

<template>
  <div class="speech-controls" aria-label="语音播放控制">
    <button type="button" @click="playSpeech">播放旁白</button>
    <button type="button" :disabled="!isSpeaking || isPaused" @click="pauseSpeech">暂停</button>
    <button type="button" :disabled="!isSpeaking || !isPaused" @click="resumeSpeech">继续</button>
    <label>
      <span>语速</span>
      <input v-model.number="rate" type="range" min="0.7" max="1.3" step="0.1" />
    </label>
    <p class="caption">字幕：{{ text }}</p>
    <p v-if="speechError" class="error" role="alert">{{ speechError }}</p>
  </div>
</template>
