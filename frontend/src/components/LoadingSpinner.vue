<template>
  <div class="flex justify-center items-center h-full">
    <div v-if="type === 'circle'" :class="`animate-spin rounded-full ${sizeClasses[size]} border-t-2 border-b-2 border-blue-500`"></div>
    <div v-else class="flex items-center justify-center">
      <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <span v-if="showText" class="ml-2">{{ text }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  type: {
    type: String,
    default: 'circle',
    validator: (value) => ['circle', 'spinner'].includes(value)
  },
  showText: {
    type: Boolean,
    default: false
  },
  text: {
    type: String,
    default: 'Loading...'
  }
})

const sizeClasses = {
  small: 'h-6 w-6',
  medium: 'h-10 w-10',
  large: 'h-16 w-16'
}
</script>
