<template>
  <div class="max-w-md mx-auto mt-10">
    <h1 class="text-2xl font-bold mb-6 text-center">Log In</h1>
    
    <div v-if="error" class="bg-red-100 text-red-700 p-3 rounded-lg mb-4">
      {{ error }}
    </div>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label for="email" class="block mb-1 text-gray-700">Email</label>
        <input
          id="email"
          type="email"
          v-model="email"
          class="w-full p-3 border border-gray-300 rounded-md"
          placeholder="Email"
        />
      </div>
      
      <div>
        <label for="password" class="block mb-1 text-gray-700">Password</label>
        <input
          id="password"
          type="password"
          v-model="password"
          placeholder="Password"
          class="w-full p-3 border border-gray-300 rounded-md"
        />
      </div>
      
      <button
        type="submit"
        :disabled="loading"
        class="w-full bg-blue-600 text-white p-3 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
      >
        {{ loading ? 'Logging in...' : 'Login' }}
      </button>
    </form>
    
    <p class="mt-4 text-center text-gray-600">
      Don't have an account?
      <router-link to="/register" class="text-blue-600 hover:underline">
        Sign Up
      </router-link>
    </p>
    
    <div class="mt-6 text-center">
      <p class="text-gray-600 text-sm">
        Test account: customer1@example.com / password123
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref(null)

const handleSubmit = async () => {
  if (!email.value || !password.value) {
    error.value = 'Please enter both email and password'
    return
  }
  
  try {
    loading.value = true
    error.value = null
    
    await auth.login(email.value, password.value)
    router.push('/')
  } catch (err) {
    console.error('Login failed:', err)
    error.value = 'Invalid email or password'
  } finally {
    loading.value = false
  }
}
</script>
