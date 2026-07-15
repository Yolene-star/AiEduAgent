<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import { fetchStorybookSpec } from '../api'
import type { Stage, StorybookSpec } from '../types'
import SpeechControls from './SpeechControls.vue'

const props = defineProps<{
  stage: Stage
}>()

const spec = ref<StorybookSpec | null>(null)
const pageIndex = ref(0)
const isOpen = ref(props.stage === 'lower_primary')
const imageFailed = ref(false)
const errorMessage = ref('')

const currentPage = computed(() => spec.value?.pages[pageIndex.value] ?? null)
const speechText = computed(() => {
  if (!currentPage.value) {
    return ''
  }
  return `${currentPage.value.narration}${currentPage.value.dialogue}${currentPage.value.question}`
})

async function loadSpec() {
  errorMessage.value = ''
  try {
    spec.value = await fetchStorybookSpec()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '绘本资源加载失败。'
  }
}

function previousPage() {
  imageFailed.value = false
  pageIndex.value = Math.max(0, pageIndex.value - 1)
}

function nextPage() {
  if (!spec.value) {
    return
  }
  imageFailed.value = false
  pageIndex.value = Math.min(spec.value.pages.length - 1, pageIndex.value + 1)
}

watch(
  () => props.stage,
  (stage) => {
    if (stage === 'lower_primary') {
      isOpen.value = true
    }
  }
)

onMounted(loadSpec)
</script>

<template>
  <section class="multimodal-panel" aria-labelledby="storybook-title">
    <div class="section-heading">
      <div>
        <p class="eyebrow">阶段 7</p>
        <h2 id="storybook-title">{{ spec?.title ?? '互动绘本' }}</h2>
      </div>
      <button v-if="!isOpen" type="button" @click="isOpen = true">打开绘本</button>
    </div>

    <p v-if="stage !== 'lower_primary'" class="meta">绘本默认推荐给小学低年级；当前学段可按需打开。</p>
    <p v-if="errorMessage" class="error" role="alert">{{ errorMessage }} 可继续使用文字问答和练习。</p>

    <template v-if="isOpen && spec && currentPage">
      <article class="storybook-page">
        <div class="storybook-media">
          <img v-if="!imageFailed" :src="currentPage.image" :alt="currentPage.alt" @error="imageFailed = true" />
          <div v-else class="image-placeholder" role="img" :aria-label="currentPage.alt">
            图片暂时无法显示：{{ currentPage.alt }}
          </div>
        </div>

        <div class="storybook-copy">
          <p class="meta">第 {{ currentPage.page }} / {{ spec.pages.length }} 页</p>
          <h3>{{ currentPage.title }}</h3>
          <p>{{ currentPage.narration }}</p>
          <p>{{ currentPage.dialogue }}</p>
          <h4>互动问题</h4>
          <p>{{ currentPage.question }}</p>
        </div>
      </article>

      <div class="control-row" aria-label="绘本翻页控制">
        <button type="button" :disabled="pageIndex === 0" @click="previousPage">上一页</button>
        <button type="button" :disabled="pageIndex === spec.pages.length - 1" @click="nextPage">下一页</button>
      </div>

      <SpeechControls :text="speechText" />
    </template>
  </section>
</template>
