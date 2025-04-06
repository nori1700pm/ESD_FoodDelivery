<template>
  <div>
    <!-- Personalized Call to Action - Removed background styling -->
    <div class="mb-8">
      <h1 class="text-3xl font-bold text-gray-800">What would you like to eat today, {{ profile?.name || 'there' }}?</h1>
      <p class="text-gray-600 mt-2">Browse our selection of restaurants and cuisines below.</p>
    </div>

    <h1 class="text-3xl font-bold mb-6">Restaurants</h1>

    <div v-if="loading" class="flex justify-center items-center py-20">
      <loading-spinner size="large" />
    </div>

    <div v-else-if="error" class="text-center py-10">
      <p class="text-red-500 text-lg">{{ error }}</p>
      <button 
        @click="fetchRestaurants"
        class="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Try Again
      </button>
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <router-link 
        v-for="restaurant in restaurants"
        :key="restaurant.id"
        :to="`/restaurants/${restaurant.id}`" 
        class="border rounded-lg shadow-lg p-4 transition-transform hover:scale-105"
      >
        <div class="relative h-48 mb-3">
          <img 
            :src="restaurant.imageUrl" 
            :alt="restaurant.name" 
            class="w-full h-full object-cover rounded" 
          />
          <span class="absolute top-2 right-2 bg-white px-2 py-1 rounded text-sm">
            {{ restaurant.deliveryTime }}
          </span>
        </div>
        
        <h2 class="text-xl font-bold">{{ restaurant.name }}</h2>
        <div class="flex items-center mb-1">
          <span class="text-yellow-500 mr-1">★</span>
          <span>{{ restaurant.rating }}</span>
          <span class="mx-2">•</span>
          <span class="text-gray-600">{{ restaurant.cuisine }}</span>
        </div>
        <p class="text-sm text-gray-500 mb-2">{{ restaurant.address }}</p>
        <p class="text-sm">Delivery: ${{ restaurant.deliveryFee.toFixed(2) }}</p>
      </router-link>
    </div>
    
    <p v-if="restaurants.length === 0 && !error && !loading" class="text-center py-10 text-gray-500">
      No restaurants available at the moment.
    </p>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { collection, getDocs } from 'firebase/firestore'
import { db } from '../config/firebase'
import LoadingSpinner from '../components/LoadingSpinner.vue'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'
import axios from 'axios'

const restaurants = ref([])
const loading = ref(true)
const error = ref(null)
const profile = ref(null)

const auth = useAuthStore()
const { user } = storeToRefs(auth)

// Try to load profile from localStorage first for immediate display
const cachedProfile = localStorage.getItem('userProfile')
if (cachedProfile) {
  try {
    profile.value = JSON.parse(cachedProfile)
    console.log('Restaurant page: Loaded profile from cache:', profile.value)
  } catch (e) {
    console.error('Failed to parse cached profile', e)
  }
}

onMounted(async () => {
  await fetchRestaurants()
  if (user.value && !profile.value) {
    await fetchUserProfile()
  }
})

const fetchUserProfile = async () => {
  try {
    if (!user.value) return
    
    console.log('Restaurant page: Fetching user profile for:', user.value.uid)
    const response = await axios.get(`http://localhost:8000/customers/${user.value.uid}`)
    profile.value = response.data
    
    // Cache the profile in localStorage for quick access
    localStorage.setItem('userProfile', JSON.stringify(profile.value))
    console.log('Restaurant page: Profile fetched and cached:', profile.value)
  } catch (err) {
    console.error('Error fetching profile:', err)
    // We don't need to set an error state for this since it's not critical
  }
}

const fetchRestaurants = async () => {
  try {
    loading.value = true
    error.value = null
    
    const querySnapshot = await getDocs(collection(db, 'restaurants'))
    
    if (querySnapshot.empty) {
      error.value = "No restaurants found. Please try again later."
      return
    }
    
    restaurants.value = querySnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    }))
    
  } catch (err) {
    console.error("Error fetching restaurants:", err)
    error.value = "Failed to load restaurants. Please try again later."
  } finally {
    loading.value = false
  }
}
</script>
