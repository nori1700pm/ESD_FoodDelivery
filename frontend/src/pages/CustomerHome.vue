<template>
  <div class="customer-home">
    <!-- Hero Banner Section - Fixed positioning issue -->
    <div class="welcome-banner">
      <div class="overlay">
        <div class="container mx-auto px-4 relative z-10">
          <div v-if="loading" class="animate-pulse py-16">
            <div class="h-10 w-64 bg-blue-400 bg-opacity-50 rounded mb-4"></div>
            <div class="h-6 w-96 bg-blue-400 bg-opacity-50 rounded"></div>
          </div>
          <div v-else class="py-16">
            <h1 class="text-4xl md:text-5xl font-bold text-white mb-3">Welcome, {{ profile?.name || 'Customer' }}!</h1>
            <p class="text-xl md:text-2xl text-white opacity-90">What delicious meal are you craving today?</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Quick Action Cards -->
    <div class="container mx-auto px-4 py-16">
      <h2 class="section-title">Quick Actions</h2>
      
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 mt-12">
        <div class="feature-card">
          <router-link to="/restaurants" class="block h-full">
            <div class="icon-container">
              <vue-feather type="shopping-bag" size="48" class="feature-icon"></vue-feather>
            </div>
            <h3>Browse Restaurants</h3>
            <p>Explore our wide selection of restaurants and cuisines</p>
          </router-link>
        </div>
        
        <div class="feature-card">
          <router-link to="/orders" class="block h-full">
            <div class="icon-container">
              <vue-feather type="package" size="48" class="feature-icon"></vue-feather>
            </div>
            <h3>My Orders</h3>
            <p>View your order history and track current deliveries</p>
          </router-link>
        </div>
        
        <div class="feature-card">
          <router-link to="/wallet" class="block h-full">
            <div class="icon-container">
              <vue-feather type="credit-card" size="48" class="feature-icon"></vue-feather>
            </div>
            <h3>My Wallet</h3>
            <p>Manage your wallet and payment methods</p>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'
import axios from 'axios'
import VueFeather from 'vue-feather'

const auth = useAuthStore()
const { user } = storeToRefs(auth)

const profile = ref(null)
const loading = ref(true)
const error = ref(null)

// Try to load profile from localStorage first for immediate display
const cachedProfile = localStorage.getItem('userProfile')
if (cachedProfile) {
  try {
    profile.value = JSON.parse(cachedProfile)
    console.log('Loaded profile from cache:', profile.value)
  } catch (e) {
    console.error('Failed to parse cached profile', e)
  }
}

onMounted(async () => {
  if (user.value) {
    await fetchUserProfile()
  }
})

const fetchUserProfile = async () => {
  try {
    console.log('Fetching user profile for:', user.value.uid)
    const response = await axios.get(`http://localhost:8000/customers/${user.value.uid}`)
    profile.value = response.data
    
    // Cache the profile in localStorage for quick access
    localStorage.setItem('userProfile', JSON.stringify(profile.value))
    console.log('Profile fetched and cached:', profile.value)
  } catch (err) {
    console.error('Error fetching profile:', err)
    error.value = 'Failed to load your profile data'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.customer-home {
  font-family: 'Roboto', sans-serif;
  color: #333;
  overflow-x: hidden;
}

.welcome-banner {
  background-image: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('https://images.unsplash.com/photo-1504674900247-0877df9cc836?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80');
  background-size: cover;
  background-position: center;
  position: relative;
  min-height: 300px; /* Ensure minimum height for banner */
}

.overlay {
  position: relative; /* Changed from absolute to relative */
  width: 100%;
  padding: 40px 0; /* Added padding instead of using height */
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.7) 0%, rgba(0, 0, 0, 0.5) 100%);
  display: flex;
  align-items: center;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: #333;
  position: relative;
}

.section-title:after {
  content: '';
  display: block;
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #4a6cf7 0%, #3452db 100%);
  margin: 24px auto 0;
  border-radius: 2px;
}

.feature-card {
  background: white;
  padding: 40px 30px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  text-align: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  height: 100%;
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.feature-card:before {
  content: '';
  position: absolute;
  width: 100%;
  height: 6px;
  background: linear-gradient(90deg, #4a6cf7, #3452db);
  top: 0;
  left: 0;
  transform: scaleX(0);
  transform-origin: right;
  transition: transform 0.4s ease;
}

.feature-card:hover:before {
  transform: scaleX(1);
  transform-origin: left;
}

.icon-container {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, rgba(74, 108, 247, 0.1) 0%, rgba(52, 82, 219, 0.1) 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
}

.feature-icon {
  color: #4a6cf7;
}

.feature-card h3 {
  font-size: 1.6rem;
  font-weight: 600;
  margin-bottom: 16px;
  color: #333;
}

.feature-card p {
  color: #666;
  line-height: 1.7;
  font-size: 1.1rem;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .section-title {
    font-size: 2rem;
  }
  
  .feature-card h3 {
    font-size: 1.4rem;
  }
}

@media (max-width: 480px) {
  .section-title {
    font-size: 1.8rem;
  }
  
  .feature-card {
    padding: 30px 20px;
  }
}
</style>
