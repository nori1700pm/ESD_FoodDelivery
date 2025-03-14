<template>
  <div class="flex justify-center items-center h-full">
    <div 
      :class="`animate-spin rounded-full ${sizeClasses[size]} border-t-blue-500 border-r-blue-500 border-b-transparent border-l-transparent`"
    ></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  }
})

const sizeClasses = {
  small: 'h-6 w-6 border-2',
  medium: 'h-10 w-10 border-2',
  large: 'h-16 w-16 border-4'
}
</script>
