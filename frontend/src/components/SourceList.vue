<script setup lang="ts">
defineProps<{
  cardIds: string[]
}>()
</script>

<template>
  <section class="sources" aria-label="来源卡片">
    <h2>来源占位</h2>
    <ul>
      <li v-for="cardId in cardIds" :key="cardId">{{ cardId }}</li>
    </ul>
  </section>
</template>
