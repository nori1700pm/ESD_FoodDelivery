<template>
  <div class="App min-h-screen flex flex-col bg-gray-50">
    <template v-if="authStore && !authStore.loading">
      <!-- Only show navbar and footer on authenticated pages -->
      <template v-if="!isAuthPage">
        <Navbar />
        <main class="container mx-auto px-4 py-8 flex-grow">
          <router-view />
        </main>
        <Footer />
      </template>
      <!-- For landing/login/register pages, just render the router view without navbar and footer -->
      <template v-else>
        <router-view />
      </template>
    </template>
    <div v-else class="flex justify-center items-center h-screen">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from './stores/auth'
import { useRoute } from 'vue-router'
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'

const authStore = ref(null)
const route = useRoute()

// Compute whether we're on an authentication page (landing, login, register)
const isAuthPage = computed(() => {
  const authPages = ['Landing', 'Login', 'Register']
  return authPages.includes(route.name)
})

onMounted(() => {
  authStore.value = useAuthStore()
})
</script>