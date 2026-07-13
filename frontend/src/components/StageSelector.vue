<script setup lang="ts">
import type { Stage } from '../types'

const stageOptions: Array<{ value: Stage; label: string }> = [
  { value: 'lower_primary', label: '小学低年级' },
  { value: 'upper_primary', label: '小学高年级' },
  { value: 'middle_school', label: '初中' },
  { value: 'high_school', label: '高中' }
]

const model = defineModel<Stage>({ required: true })
</script>

<template>
  <label class="field">
    <span>学段</span>
    <select v-model="model" aria-label="选择学段">
      <option v-for="option in stageOptions" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
  </label>
</template>
