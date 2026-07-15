<script setup lang="ts">
import type { SourceLink } from '../types'

defineProps<{
  cardIds: string[]
  sources: SourceLink[]
}>()
</script>

<template>
  <section class="sources" aria-label="来源卡片">
    <h2>来源占位</h2>
    <p v-if="cardIds.length === 0" class="empty">暂无课内知识卡来源。</p>
    <ul v-else>
      <li v-for="cardId in cardIds" :key="cardId">{{ cardId }}</li>
    </ul>
    <h3>可核验来源</h3>
    <p v-if="sources.length === 0" class="empty">暂无可核验来源，属于通识回答或模型兜底回答。</p>
    <ul v-else>
      <li v-for="source in sources" :key="`${source.card_id}-${source.url}`">
        <a :href="source.url" target="_blank" rel="noreferrer">{{ source.title }}</a>
        <span>（{{ source.card_id }}）</span>
      </li>
    </ul>
  </section>
</template>
