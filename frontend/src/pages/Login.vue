<template>
  <div class="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-gray-50">
    <div class="max-w-lg w-full bg-white p-10 rounded-xl shadow-2xl space-y-8">
      <!-- Back to landing page button -->
      <div class="absolute top-6 left-6">
        <router-link to="/" class="flex items-center text-gray-600 hover:text-blue-600 transition-colors">
          <vue-feather type="arrow-left" size="18" class="mr-2"></vue-feather>
          <span>Back to Home</span>
        </router-link>
      </div>
      
      <div class="text-center">
        <h1 class="text-3xl font-extrabold text-gray-900 mb-2">Welcome Back</h1>
        <p class="text-gray-600">Sign in to your NomNomGo account</p>
      </div>
      
      <!-- Login type selection -->
      <div class="flex mb-8 bg-gray-100 rounded-lg p-1">
        <button 
          @click="loginType = 'customer'" 
          :class="[
            'flex-1 py-3 rounded-md font-medium transition-all',
            loginType === 'customer' 
              ? 'bg-white shadow-sm text-blue-600' 
              : 'text-gray-500 hover:text-gray-700'
          ]"
        >
          Customer
        </button>
        <button 
          @click="loginType = 'driver'" 
          :class="[
            'flex-1 py-3 rounded-md font-medium transition-all',
            loginType === 'driver' 
              ? 'bg-white shadow-sm text-blue-600' 
              : 'text-gray-500 hover:text-gray-700'
          ]"
        >
          Driver
        </button>
      </div>
      
      <div v-if="error" class="bg-red-100 text-red-700 p-4 rounded-lg">
        {{ error }}
      </div>
      
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div>
          <label for="email" class="block mb-2 text-sm font-medium text-gray-700">Email Address</label>
          <div class="relative">
            <vue-feather type="mail" size="18" class="absolute top-3.5 left-3 text-gray-400"></vue-feather>
            <input
              id="email"
              type="email"
              v-model="email"
              class="w-full pl-10 p-3.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              :placeholder="loginType === 'driver' ? 'driver@driver.com' : 'customer@example.com'"
            />
          </div>
        </div>
        
        <div>
          <label for="password" class="block mb-2 text-sm font-medium text-gray-700">Password</label>
          <div class="relative">
            <vue-feather type="lock" size="18" class="absolute top-3.5 left-3 text-gray-400"></vue-feather>
            <input
              id="password"
              type="password"
              v-model="password"
              class="w-full pl-10 p-3.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              placeholder="••••••••"
            />
          </div>
        </div>
        
        <button
          type="submit"
          :disabled="loading"
          class="w-full py-3.5 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:bg-blue-300 transition-colors flex items-center justify-center"
        >
          <span v-if="loading" class="mr-2">
            <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </span>
          {{ loading ? 'Signing in...' : loginType === 'driver' ? 'Login as Driver' : 'Login as Customer' }}
        </button>
      </form>
      
      <!-- Demo login credentials hint -->
      <div class="p-4 bg-gray-50 rounded-lg text-sm text-gray-600 border border-gray-200">
        <p class="font-semibold mb-2">Demo Credentials:</p>
        <div v-if="loginType === 'customer'" class="space-y-2">
          <div class="flex items-center">
            <vue-feather type="user" size="14" class="text-gray-500 mr-2"></vue-feather>
            <span class="font-medium w-20">Customer:</span>
          </div>
          <div class="ml-6 space-y-1">
            <div class="flex">
              <span class="w-16 text-gray-500">Email:</span>
              <code class="bg-gray-100 px-2 py-1 rounded">customer1@example.com</code>
            </div>
            <div class="flex">
              <span class="w-16 text-gray-500">Password:</span>
              <code class="bg-gray-100 px-2 py-1 rounded">password123</code>
            </div>
          </div>
        </div>
        <div v-else class="space-y-2">
          <div class="flex items-center">
            <vue-feather type="truck" size="14" class="text-gray-500 mr-2"></vue-feather>
            <span class="font-medium w-20">Driver:</span>
          </div>
          <div class="ml-6 space-y-1">
            <div class="flex">
              <span class="w-16 text-gray-500">Email:</span>
              <code class="bg-gray-100 px-2 py-1 rounded">jewel@driver.com</code>
            </div>
            <div class="flex">
              <span class="w-16 text-gray-500">Password:</span>
              <code class="bg-gray-100 px-2 py-1 rounded">123123</code>
            </div>
          </div>
        </div>
      </div>
      
      <div class="text-center">
        <p class="text-gray-600">
          Don't have an account?
          <router-link to="/register" class="text-blue-600 hover:underline font-medium">
            Register
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import VueFeather from 'vue-feather'

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

  // Prevent customers from using @driver.com email
  if (loginType.value === 'customer' && email.value.endsWith('@driver.com')) {
    error.value = 'Please log in as a driver if your email ends with @driver.com'
    return
  }

  // Ensure drivers use @driver.com email
  if (loginType.value === 'driver' && !email.value.endsWith('@driver.com')) {
    error.value = 'Driver email must end with @driver.com, Please log in as a customer if you are not a driver'
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
