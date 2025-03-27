<template>
  <div class="App min-h-screen flex flex-col bg-gray-50">
    <template v-if="authStore && !authStore.loading">
      <Navbar />
      <main class="container mx-auto px-4 py-8 flex-grow">
        <router-view />
      </main>
      <Footer />
    </template>
    <div v-else class="flex justify-center items-center h-screen">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from './stores/auth'
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'

const authStore = ref(null)

onMounted(() => {
  authStore.value = useAuthStore()
})
</script>