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
        <h1 class="text-3xl font-extrabold text-gray-900 mb-2">Create an Account</h1>
        <p class="text-gray-600">Join NomNomGo and start ordering</p>
      </div>
      
      <!-- Login type selection -->
      <!-- <div class="flex mb-8 bg-gray-100 rounded-lg p-1">
        <button 
          @click="userType = 'customer'" 
          :class="[
            'flex-1 py-3 rounded-md font-medium transition-all',
            userType === 'customer' 
              ? 'bg-white shadow-sm text-blue-600' 
              : 'text-gray-500 hover:text-gray-700'
          ]"
        >
          Customer
        </button>
        <button 
          @click="userType = 'driver'" 
          :class="[
            'flex-1 py-3 rounded-md font-medium transition-all',
            userType === 'driver' 
              ? 'bg-white shadow-sm text-blue-600' 
              : 'text-gray-500 hover:text-gray-700'
          ]"
        >
          Driver
        </button>
      </div> -->
      
      <div v-if="error" class="bg-red-100 text-red-700 p-4 rounded-lg">
        {{ error }}
      </div>
      
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <div>
          <label for="name" class="block mb-2 text-sm font-medium text-gray-700">Full Name</label>
          <div class="relative">
            <vue-feather type="user" size="18" class="absolute top-3.5 left-3 text-gray-400"></vue-feather>
            <input
              id="name"
              type="text"
              v-model="name"
              class="w-full pl-10 p-3.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              placeholder="Your full name"
            />
          </div>
        </div>
        
        <div>
          <label for="email" class="block mb-2 text-sm font-medium text-gray-700">Email Address</label>
          <div class="relative">
            <vue-feather type="mail" size="18" class="absolute top-3.5 left-3 text-gray-400"></vue-feather>
            <input
              id="email"
              type="email"
              v-model="email"
              class="w-full pl-10 p-3.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              :placeholder="userType === 'driver' ? 'driver@driver.com' : 'customer@example.com'"
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
        
        <div>
          <label for="phone" class="block mb-2 text-sm font-medium text-gray-700">Phone Number</label>
          <div class="relative">
            <vue-feather type="phone" size="18" class="absolute top-3.5 left-3 text-gray-400"></vue-feather>
            <input
              id="phone"
              type="tel"
              v-model="phone"
              class="w-full pl-10 p-3.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              placeholder="Your phone number"
            />
          </div>
        </div>
        
        <div v-if="userType === 'customer'">
          <label for="address" class="block mb-2 text-sm font-medium text-gray-700">Delivery Address</label>
          <div class="relative">
            <vue-feather type="map-pin" size="18" class="absolute top-3.5 left-3 text-gray-400"></vue-feather>
            <textarea
              id="address"
              v-model="address"
              class="w-full pl-10 p-3.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors"
              rows="3"
              placeholder="Your delivery address"
            ></textarea>
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
          {{ loading ? 'Creating account...' : 'Create Account' }}
        </button>
      </form>
      
      <div class="text-center">
        <p class="text-gray-600">
          Already have an account?
          <router-link to="/login" class="text-blue-600 hover:underline font-medium">
            Sign In
          </router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { getAuth, createUserWithEmailAndPassword } from 'firebase/auth'
import VueFeather from 'vue-feather'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'

const router = useRouter()
const auth = useAuthStore()
const { user } = storeToRefs(auth)

const email = ref('')
const password = ref('')
const name = ref('')
const phone = ref('')
const address = ref('')
const driverLocation = ref('Somewhere') // Default driver location
const userType = ref('customer') // Default to 'customer'
const driverStatus = ref('Busy') // Default driver status
const error = ref(null)
const loading = ref(false)

// Check if user is already authenticated on component mount
onMounted(() => {
  if (user.value) {
    // User is already logged in, redirect to appropriate page
    if (user.value.email && user.value.email.endsWith('@driver.com')) {
      router.push('/activeOrder') // Redirect drivers to activeOrder page
    } else {
      router.push('/restaurants') // Redirect customers to restaurants page
    }
  }
})

const handleSubmit = async () => {
  if (!email.value || !password.value || !name.value || !phone.value || 
      (userType.value === 'customer' && !address.value)) {
    error.value = 'Please fill in all fields'
    return
  }

  // Email domain validation
  const emailDomain = email.value.split('@')[1];
  if (userType.value === 'driver' && emailDomain !== 'driver.com') {
    error.value = 'Drivers must use an email with the domain @driver.com';
    return;
  }
  if (userType.value === 'customer' && emailDomain === 'driver.com') {
    error.value = 'Customers cannot use an email with the domain @driver.com';
    return;
  }

  try {
    loading.value = true
    error.value = null

    const auth = getAuth()

    if (userType.value === 'customer') {

      const response = await axios.post('http://localhost:8000/customers', {
        name: name.value,
        email: email.value,
        phone: phone.value,
        password: password.value,
        address: address.value
      })
      console.log("Customer registration complete:", response.data)
      router.push('/')
    } else if (userType.value === 'driver') {
      // Create Firebase Auth record for driver
      await createUserWithEmailAndPassword(auth, email.value, password.value)

      // try {
      //   // Call the OutSystems API for driver registration with correct field names
      //   const response = await axios.post('http://localhost:8000/createDriver', {
      //     DriverName: name.value, 
      //     DriverStatus: driverStatus.value, 
      //     DriverNumber: phone.value, 
      //     DriverLocation: driverLocation.value, 
      //     DriverEmail: email.value 
      //   })
      //   console.log("Driver registration complete in OutSystems:", response.data)
      // } catch (outsystemsError) {
      //   console.error("OutSystems API error:", outsystemsError.response?.data || outsystemsError.message)
      //   error.value = "Failed to save driver in OutSystems. Please contact support."
      //   return
      // }

      router.push('/activeorder') // Redirect drivers to activeorder.vue
    }
  } catch (err) {
    console.error('Registration failed:', err)
    error.value = err.response?.data?.message || 'Failed to register. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>