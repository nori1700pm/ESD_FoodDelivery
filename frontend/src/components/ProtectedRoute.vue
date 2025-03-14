<template>
  <div v-if="loading" class="flex justify-center items-center h-64">
    <LoadingSpinner size="large" />
  </div>
  <slot v-else-if="isAuthenticated" />
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'
import LoadingSpinner from './LoadingSpinner.vue'

const router = useRouter()
const auth = useAuthStore()
const { user, loading } = storeToRefs(auth)

const isAuthenticated = computed(() => {
  if (!loading.value && !user.value) {
    router.push('/login')
    return false
  }
  return true
})
</script>
