<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import { fetchAnimationSpec } from '../api'
import type { AnimationSpec, AnimationStep } from '../types'
import SpeechControls from './SpeechControls.vue'

const spec = ref<AnimationSpec | null>(null)
const stepIndex = ref(0)
const isPlaying = ref(false)
const errorMessage = ref('')
let timer: number | undefined

const currentStep = computed<AnimationStep | null>(() => spec.value?.steps[stepIndex.value] ?? null)
const subtitle = computed(() => currentStep.value?.caption ?? '')
const progress = computed(() => (spec.value ? stepIndex.value / Math.max(1, spec.value.steps.length - 1) : 0))

async function loadSpec() {
  errorMessage.value = ''
  try {
    spec.value = await fetchAnimationSpec()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '动画资源加载失败。'
  }
}

function clearTimer() {
  if (timer !== undefined) {
    window.clearInterval(timer)
    timer = undefined
  }
}

function play() {
  if (!spec.value) {
    return
  }
  isPlaying.value = true
  clearTimer()
  timer = window.setInterval(() => {
    if (!spec.value) {
      return
    }
    if (stepIndex.value >= spec.value.steps.length - 1) {
      pause()
      return
    }
    stepIndex.value += 1
  }, 1600)
}

function pause() {
  isPlaying.value = false
  clearTimer()
}

function restart() {
  stepIndex.value = 0
  play()
}

function previous() {
  pause()
  stepIndex.value = Math.max(0, stepIndex.value - 1)
}

function next() {
  pause()
  if (!spec.value) {
    return
  }
  stepIndex.value = Math.min(spec.value.steps.length - 1, stepIndex.value + 1)
}

onMounted(loadSpec)
onBeforeUnmount(clearTimer)
</script>

<template>
  <section class="multimodal-panel" aria-labelledby="animation-title">
    <div class="section-heading">
      <div>
        <p class="eyebrow">阶段 7</p>
        <h2 id="animation-title">{{ spec?.title ?? '图像分类动画' }}</h2>
      </div>
      <p class="meta">{{ spec?.concept_id ?? 'U1-C04' }}</p>
    </div>

    <p v-if="errorMessage" class="error" role="alert">{{ errorMessage }} 可继续使用文字问答和练习。</p>

    <template v-if="spec && currentStep">
      <p>{{ spec.subtitle }}</p>

      <div
        class="animation-stage"
        :data-step="currentStep.id"
        :style="{ '--progress': progress.toString() }"
        aria-label="图像分类过程动态演示"
      >
        <div class="timeline-track" aria-hidden="true">
          <span
            v-for="(step, index) in spec.steps"
            :key="step.id"
            :class="{ active: index <= stepIndex }"
          ></span>
        </div>
        <div class="scene-object picture-node" aria-hidden="true">
          <span class="picture-sun"></span>
          <span class="picture-mountain"></span>
        </div>
        <div class="scene-object pixel-node" aria-hidden="true">
          <span v-for="cell in 24" :key="cell"></span>
        </div>
        <div class="scene-object feature-node" aria-hidden="true">
          <span></span>
          <span></span>
          <span></span>
        </div>
        <div class="scene-object model-node" aria-hidden="true">
          <span>模型</span>
        </div>
        <div class="scene-object score-node" aria-hidden="true">
          <span style="--score: 78%">猫</span>
          <span style="--score: 42%">狗</span>
          <span style="--score: 24%">车</span>
        </div>
        <div class="scene-object label-node" aria-hidden="true">预测标签：猫</div>
      </div>

      <article class="step-caption" aria-live="polite">
        <p class="meta">第 {{ stepIndex + 1 }} / {{ spec.steps.length }} 步</p>
        <h3>{{ currentStep.title }}</h3>
        <p>{{ currentStep.caption }}</p>
      </article>

      <div class="control-row" aria-label="动画控制">
        <button type="button" @click="previous">上一步</button>
        <button type="button" @click="isPlaying ? pause() : play()">{{ isPlaying ? '暂停' : '播放' }}</button>
        <button type="button" @click="next">下一步</button>
        <button type="button" @click="restart">重播</button>
      </div>

      <SpeechControls :text="subtitle" />
    </template>
  </section>
</template>
