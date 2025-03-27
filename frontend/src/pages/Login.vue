<template>
  <div class="max-w-md mx-auto bg-white p-8 rounded-lg shadow-md">
    <h1 class="text-2xl font-bold mb-6 text-center">Login to Your Account</h1>
    
    <!-- Login type selection -->
    <div class="flex mb-6">
      <button 
        @click="loginType = 'customer'" 
        :class="[
          'flex-1 py-2 border-b-2 text-center',
          loginType === 'customer' 
            ? 'border-blue-500 text-blue-600 font-medium' 
            : 'border-gray-200 text-gray-500'
        ]"
      >
        Customer
      </button>
      <button 
        @click="loginType = 'driver'" 
        :class="[
          'flex-1 py-2 border-b-2 text-center',
          loginType === 'driver' 
            ? 'border-blue-500 text-blue-600 font-medium' 
            : 'border-gray-200 text-gray-500'
        ]"
      >
        Driver
      </button>
    </div>
    
    <div v-if="error" class="bg-red-100 text-red-700 p-3 rounded-md mb-4">
      {{ error }}
    </div>
    
    <form @submit.prevent="handleSubmit">
      <div class="mb-4">
        <label for="email" class="block mb-1 text-gray-700">Email</label>
        <input
          id="email"
          type="email"
          v-model="email"
          class="w-full p-3 border border-gray-300 rounded-md"
          :placeholder="loginType === 'driver' ? 'driver@driver.com' : 'customer@example.com'"
        />
      </div>
      
      <div class="mb-6">
        <label for="password" class="block mb-1 text-gray-700">Password</label>
        <input
          id="password"
          type="password"
          v-model="password"
          class="w-full p-3 border border-gray-300 rounded-md"
        />
      </div>
      
      <button
        type="submit"
        :disabled="loading"
        class="w-full bg-blue-600 text-white p-3 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
      >
        {{ loading ? 'Signing in...' : loginType === 'driver' ? 'Login as Driver' : 'Login as Customer' }}
      </button>
    </form>
    
    <!-- Demo login credentials hint -->
    <div class="mt-4 p-3 bg-gray-50 rounded-md text-sm text-gray-600">
      <p class="font-semibold">Demo Credentials:</p>
      <p v-if="loginType === 'customer'">
        <span class="font-medium">Customer:</span> customer1@example.com / password123
      </p>
      <p v-else>
        <span class="font-medium">Driver:</span> jewel@driver.com / 123123
      </p>
    </div>
    
    <p class="mt-4 text-center text-gray-600">
      Don't have an account?
      <router-link to="/register" class="text-blue-600 hover:underline">
        Register
      </router-link>
    </p>
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
const loginType = ref('customer')

const handleSubmit = async () => {
  if (!email.value || !password.value) {
    error.value = 'Please enter both email and password'
    return
  }
  
  try {
    loading.value = true
    error.value = null
    
    // Ensure driver emails have @driver.com suffix for driver login
    if (loginType.value === 'driver' && !email.value.endsWith('@driver.com')) {
      email.value = `${email.value.split('@')[0]}@driver.com`
    }
    
    await auth.login(email.value, password.value)
    
    // Redirect based on email domain
    if (email.value.endsWith('@driver.com')) {
      router.push('/activeOrder') // Redirect to active orders page for drivers
    } else {
      router.push('/restaurants') // Redirect to restaurants list page for customers
    }
  } catch (err) {
    console.error('Login failed:', err)
    error.value = 'Invalid email or password'
  } finally {
    loading.value = false
  }
}

const handleLogout = async () => {
  try {
    await auth.logout()
    router.push('/login') // Redirect to login page after logout
  } catch (err) {
    console.error('Logout failed:', err)
  }
}
</script>
