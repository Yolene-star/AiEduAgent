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
    <ul>
      <li v-for="cardId in cardIds" :key="cardId">{{ cardId }}</li>
    </ul>
    <h3>可核验来源</h3>
    <ul>
      <li v-for="source in sources" :key="`${source.card_id}-${source.url}`">
        <a :href="source.url" target="_blank" rel="noreferrer">{{ source.title }}</a>
        <span>（{{ source.card_id }}）</span>
      </li>
    </ul>
  </section>
</template>
