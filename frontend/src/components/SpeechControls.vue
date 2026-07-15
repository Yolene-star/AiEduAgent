<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps<{
  text: string
}>()

const isSpeaking = ref(false)
const isPaused = ref(false)
const rate = ref(1)
const speechError = ref('')
const voices = ref<SpeechSynthesisVoice[]>([])
const selectedVoiceName = ref('')
let voiceRetryTimer: number | undefined
let activeUtterance: SpeechSynthesisUtterance | null = null
let isCancelling = false

type SpeechSynthesisWithVoiceChange = SpeechSynthesis & {
  onvoiceschanged: ((this: SpeechSynthesis, event: Event) => void) | null
}

const canSpeak = computed(() => typeof window !== 'undefined' && 'speechSynthesis' in window)
const chineseVoices = computed(() => voices.value.filter((voice) => voice.lang.toLowerCase().startsWith('zh')))
const selectedVoice = computed(() => {
  const preferredVoices = chineseVoices.value.length > 0 ? chineseVoices.value : voices.value
  return (
    preferredVoices.find((voice) => voice.name === selectedVoiceName.value) ??
    preferredVoices.find((voice) => voice.default) ??
    preferredVoices[0] ??
    null
  )
})

function loadVoices() {
  if (!canSpeak.value) {
    return
  }
  voices.value = window.speechSynthesis.getVoices().sort((left, right) => left.name.localeCompare(right.name))
  if (!selectedVoiceName.value && selectedVoice.value) {
    selectedVoiceName.value = selectedVoice.value.name
  }
}

function scheduleVoiceLoadRetries() {
  if (!canSpeak.value) {
    return
  }
  loadVoices()
  let attempts = 0
  voiceRetryTimer = window.setInterval(() => {
    attempts += 1
    loadVoices()
    if (voices.value.length > 0 || attempts >= 8) {
      clearVoiceRetryTimer()
    }
  }, 250)
  if (typeof window.speechSynthesis.addEventListener === 'function') {
    window.speechSynthesis.addEventListener('voiceschanged', loadVoices)
  } else {
    ;(window.speechSynthesis as SpeechSynthesisWithVoiceChange).onvoiceschanged = loadVoices
  }
}

function clearVoiceRetryTimer() {
  if (voiceRetryTimer !== undefined) {
    window.clearInterval(voiceRetryTimer)
    voiceRetryTimer = undefined
  }
}

function stopSpeech() {
  if (!canSpeak.value) {
    return
  }
  isCancelling = true
  window.speechSynthesis.cancel()
  window.setTimeout(() => {
    isCancelling = false
  }, 0)
  activeUtterance = null
  isSpeaking.value = false
  isPaused.value = false
}

function playSpeech() {
  speechError.value = ''
  if (!canSpeak.value) {
    speechError.value = '当前浏览器不支持语音播放，文本仍可正常阅读。'
    return
  }
  loadVoices()

  stopSpeech()
  isCancelling = false
  speakWithVoice(selectedVoice.value, false)
}

function speakWithVoice(voice: SpeechSynthesisVoice | null, isDefaultRetry: boolean) {
  const utterance = new SpeechSynthesisUtterance(props.text)
  utterance.lang = 'zh-CN'
  utterance.voice = voice
  utterance.rate = rate.value
  activeUtterance = utterance
  utterance.onend = () => {
    if (activeUtterance !== utterance) {
      return
    }
    isSpeaking.value = false
    isPaused.value = false
    activeUtterance = null
  }
  utterance.onerror = (event) => {
    if (isCancelling || activeUtterance !== utterance) {
      return
    }
    if (!isDefaultRetry && voice) {
      speakWithVoice(null, true)
      return
    }
    const reason = event.error ? `（${event.error}）` : ''
    speechError.value = `语音播放失败${reason}，已保留字幕。可以换一个声音，或确认浏览器/系统已安装中文语音包。`
    isSpeaking.value = false
    isPaused.value = false
    activeUtterance = null
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

watch(rate, () => {
  if (isSpeaking.value) {
    playSpeech()
  }
})

onMounted(scheduleVoiceLoadRetries)
onBeforeUnmount(() => {
  clearVoiceRetryTimer()
  if (canSpeak.value) {
    if (typeof window.speechSynthesis.removeEventListener === 'function') {
      window.speechSynthesis.removeEventListener('voiceschanged', loadVoices)
    } else {
      ;(window.speechSynthesis as SpeechSynthesisWithVoiceChange).onvoiceschanged = null
    }
  }
  stopSpeech()
})
</script>

<template>
  <div class="speech-controls" aria-label="语音播放控制">
    <button type="button" @click="playSpeech">播放旁白</button>
    <button type="button" :disabled="!isSpeaking || isPaused" @click="pauseSpeech">暂停</button>
    <button type="button" :disabled="!isSpeaking || !isPaused" @click="resumeSpeech">继续</button>
    <label>
      <span>声音</span>
      <select v-model="selectedVoiceName" :disabled="voices.length === 0" aria-label="选择语音">
        <option v-if="voices.length === 0" value="">浏览器暂无可用语音</option>
        <option v-for="voice in voices" :key="voice.name" :value="voice.name">
          {{ voice.name }} · {{ voice.lang }}
        </option>
      </select>
    </label>
    <label>
      <span>语速</span>
      <input v-model.number="rate" type="range" min="0.7" max="1.3" step="0.1" />
    </label>
    <p class="caption">字幕：{{ text }}</p>
    <p class="meta">
      当前声音：{{ selectedVoice?.name ?? '默认声音' }} · 可用声音 {{ voices.length }} 个
    </p>
    <p v-if="speechError" class="error" role="alert">{{ speechError }}</p>
  </div>
</template>
