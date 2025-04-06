<template>
  <div v-if="loading" class="flex justify-center items-center h-64">
    <loading-spinner size="large" />
  </div>

  <div v-else-if="error && !profile" class="text-center py-10">
    <p class="text-red-500 text-lg">{{ error }}</p>
    <button 
      @click="$router.go(0)"
      class="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
    >
      Try Again
    </button>
  </div>

  <div v-else class="max-w-2xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center">
        <vue-feather type="user" size="28" class="mr-2"></vue-feather>
        <h1 class="text-3xl font-bold">My Profile</h1>
      </div>
    </div>
    
    <div v-if="error" class="bg-red-100 text-red-700 p-4 rounded-lg mb-6">
      {{ error }}
    </div>
    
    <div v-if="successMessage" class="bg-green-100 text-green-700 p-4 rounded-lg mb-6">
      {{ successMessage }}
    </div>
    
    <div class="bg-white rounded-lg shadow-lg p-6">
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label for="name" class="block mb-1 text-gray-700">Full Name</label>
          <input
            id="name"
            v-model="profile.name"
            type="text"
            class="w-full p-3 border border-gray-300 rounded-md"
          />
        </div>
        
        <div>
          <label for="email" class="block mb-1 text-gray-700">Email</label>
          <input
            id="email"
            v-model="profile.email"
            type="email"
            disabled
            class="w-full p-3 border border-gray-300 rounded-md bg-gray-50"
          />
          <p class="text-xs text-gray-500 mt-1">Email cannot be changed</p>
        </div>
        
        <div>
          <label for="phone" class="block mb-1 text-gray-700">Phone Number</label>
          <input
            id="phone"
            v-model="profile.phone"
            type="tel"
            class="w-full p-3 border border-gray-300 rounded-md"
          />
        </div>
        
        <div>
          <label for="address" class="block mb-1 text-gray-700">Delivery Address</label>
          <textarea
            id="address"
            v-model="profile.address"
            class="w-full p-3 border border-gray-300 rounded-md"
            rows="3"
          ></textarea>
        </div>
        
        <button
          type="submit"
          :disabled="saving"
          class="flex items-center justify-center w-full py-2 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 disabled:bg-gray-400"
        >
          <template v-if="saving">
            <vue-feather type="loader" size="18" class="mr-2 animate-spin"></vue-feather> Saving...
          </template>
          <template v-else>
            <vue-feather type="save" size="18" class="mr-2"></vue-feather> Save Changes
          </template>
        </button>
      </form>
    </div>
    
    <div v-if="user" class="mt-4 text-xs text-gray-400">
      User ID: {{ user.uid }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'
import VueFeather from 'vue-feather'
import axios from 'axios'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const auth = useAuthStore()
const { user } = storeToRefs(auth)

const profile = ref(null)
const loading = ref(true)
const saving = ref(false)
const error = ref(null)
const successMessage = ref(null)

onMounted(async () => {
  await fetchUserProfile()
})

const fetchUserProfile = async () => {
  if (!user.value) return
  
  try {
    loading.value = true
    error.value = null

    // Fetch user profile from the microservice
    const response = await axios.get(`http://localhost:8000/customers/${user.value.uid}`)
    const userData = response.data

    profile.value = {
      name: userData.name || '',
      email: userData.email || user.value.email || '',
      phone: userData.phone || '',
      address: userData.address || '',
    }
  } catch (err) {
    console.error("Error fetching user profile:", err)
    error.value = "Failed to load your profile. Please try again."
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!user.value || !profile.value) return
  
  try {
    saving.value = true
    error.value = null
    
    // Call customer microservice to update user info in the backend
    await axios.put(`http://localhost:8000/customers/${user.value.uid}`, {
      name: profile.value.name,
      phone: profile.value.phone,
      address: profile.value.address
    })
    
    successMessage.value = "Profile updated successfully"
    setTimeout(() => successMessage.value = null, 3000)
  } catch (err) {
    console.error("Error updating profile:", err.response ? err.response.data : err.message)
    error.value = err.response?.data?.message || "Failed to update profile"
  } finally {
    saving.value = false
  }
}
</script>
