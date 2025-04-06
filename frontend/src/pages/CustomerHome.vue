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

    <!-- Recent Restaurants Carousel -->
    <div v-if="!loading && recentRestaurants.length > 0" class="recent-restaurants py-16">
      <div class="container mx-auto px-4">
        <h2 class="section-title mb-12">Recently Ordered From</h2>
        
        <div class="carousel-container relative">
          <!-- Left Arrow -->
          <button 
            @click="prevSlide" 
            class="absolute -left-4 md:left-0 top-1/2 transform -translate-y-1/2 bg-white p-3 rounded-full shadow-lg z-10 hover:bg-gray-100"
            :disabled="currentSlide === 0"
            :class="{ 'opacity-50 cursor-not-allowed': currentSlide === 0 }"
          >
            <vue-feather type="chevron-left" size="24" class="text-blue-600"></vue-feather>
          </button>
          
          <!-- Carousel -->
          <div class="overflow-hidden">
            <div 
              class="flex transition-transform duration-500 ease-in-out"
              :style="{ transform: `translateX(-${currentSlide * (100 / slidesPerView)}%)` }"
            >
              <div 
                v-for="restaurant in recentRestaurants" 
                :key="restaurant.id"
                class="restaurant-card"
                :style="{ flexBasis: `${100 / slidesPerView}%` }"
              >
                <div class="mx-2 bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
                  <div class="h-48 overflow-hidden">
                    <img 
                      :src="restaurant.imageUrl" 
                      :alt="restaurant.name" 
                      class="w-full h-full object-cover transition-transform hover:scale-105" 
                    />
                  </div>
                  <div class="p-6">
                    <h3 class="text-xl font-bold mb-2 text-gray-800">{{ restaurant.name }}</h3>
                    <div class="flex items-center mb-3">
                      <span class="text-yellow-500 mr-1">★</span>
                      <span>{{ restaurant.rating }}</span>
                      <span class="mx-2">•</span>
                      <span class="text-gray-600">{{ restaurant.cuisine }}</span>
                    </div>
                    <p v-if="restaurant.lastOrderDate" class="text-sm text-gray-500 mb-3">
                      Last ordered on {{ formatDate(restaurant.lastOrderDate) }}
                    </p>
                    <router-link 
                      :to="`/restaurants/${restaurant.id}`" 
                      class="inline-block w-full text-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
                    >
                      Order Again
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Right Arrow -->
          <button 
            @click="nextSlide" 
            class="absolute -right-4 md:right-0 top-1/2 transform -translate-y-1/2 bg-white p-3 rounded-full shadow-lg z-10 hover:bg-gray-100"
            :disabled="currentSlide >= maxSlide"
            :class="{ 'opacity-50 cursor-not-allowed': currentSlide >= maxSlide }"
          >
            <vue-feather type="chevron-right" size="24" class="text-blue-600"></vue-feather>
          </button>
        </div>
        
        <!-- Carousel Dots -->
        <div class="flex justify-center mt-6">
          <button 
            v-for="(_, index) in Array(maxSlide + 1)" 
            :key="index"
            @click="currentSlide = index"
            class="mx-1 w-3 h-3 rounded-full"
            :class="currentSlide === index ? 'bg-blue-600' : 'bg-gray-300'"
          ></button>
        </div>
      </div>
    </div>

    <!-- Promotion Section -->
    <div class="cta-section">
      <div class="container mx-auto px-4">
        <div class="cta-content">
          <h2>Free Delivery On Your First Order</h2>
          <p>Use promo code WELCOME at checkout</p>
          <router-link to="/restaurants" class="cta-button">
            <vue-feather type="shopping-bag" size="18" class="mr-2"></vue-feather>
            Start Ordering
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onBeforeUnmount } from 'vue'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'
import axios from 'axios'
import VueFeather from 'vue-feather'
import { collection, query, where, orderBy, getDocs, limit } from 'firebase/firestore'
import { db } from '../config/firebase'

const auth = useAuthStore()
const { user } = storeToRefs(auth)

const profile = ref(null)
const loading = ref(true)
const error = ref(null)
const recentRestaurants = ref([])

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

// Carousel state
const currentSlide = ref(0)
const slidesPerView = computed(() => {
  // Responsive slides per view based on screen width
  if (window.innerWidth < 640) return 1
  if (window.innerWidth < 1024) return 2
  return 3
})

const maxSlide = computed(() => {
  return Math.max(0, Math.ceil(recentRestaurants.value.length / slidesPerView.value) - 1)
})

const updateSlidesPerView = () => {
  // Update currentSlide if we're past the max after resize
  if (currentSlide.value > maxSlide.value) {
    currentSlide.value = maxSlide.value
  }
}

const nextSlide = () => {
  if (currentSlide.value < maxSlide.value) {
    currentSlide.value++
  }
}

const prevSlide = () => {
  if (currentSlide.value > 0) {
    currentSlide.value--
  }
}

// Format date for display
const formatDate = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return new Intl.DateTimeFormat('en-SG', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  }).format(date)
}

onMounted(async () => {
  if (user.value) {
    await fetchUserProfile()
    await fetchRecentRestaurants()
  }
  
  // Add window resize listener for responsive carousel
  window.addEventListener('resize', updateSlidesPerView)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateSlidesPerView)
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

const fetchRecentRestaurants = async () => {
  try {
    // Get recent orders from the orders collection
    const ordersRef = collection(db, 'orders')
    const ordersQuery = query(
      ordersRef,
      where('customerId', '==', user.value.uid),
      orderBy('createdAt', 'desc'),
      limit(10)
    )
    
    const ordersSnapshot = await getDocs(ordersQuery)
    
    if (ordersSnapshot.empty) {
      console.log('No recent orders found')
      return
    }
    
    // Extract restaurant data from orders and deduplicate
    const restaurantMap = new Map()
    
    for (const doc of ordersSnapshot.docs) {
      const orderData = doc.data()
      const restaurantId = orderData.restaurantId
      
      if (restaurantId && !restaurantMap.has(restaurantId)) {
        // Add restaurant to map with order date
        restaurantMap.set(restaurantId, {
          id: restaurantId,
          name: orderData.restaurantName || 'Restaurant',
          lastOrderDate: orderData.createdAt?.toDate() || new Date(),
          orderId: doc.id
        })
      }
    }
    
    // Fetch more details for each restaurant
    const restaurantPromises = Array.from(restaurantMap.values()).map(async (restaurant) => {
      try {
        // Get restaurant details
        const restaurantDoc = await axios.get(`http://localhost:8000/restaurants/${restaurant.id}`)
        const restaurantData = restaurantDoc.data || {}
        
        return {
          id: restaurant.id,
          name: restaurant.name || restaurantData.name || 'Restaurant',
          cuisine: restaurantData.cuisine || 'Various',
          rating: restaurantData.rating || 4.5,
          imageUrl: restaurantData.imageUrl || 'https://via.placeholder.com/300x200?text=Restaurant',
          lastOrderDate: restaurant.lastOrderDate
        }
      } catch (err) {
        console.warn(`Error fetching details for restaurant ${restaurant.id}:`, err)
        
        // Return basic info even if full details can't be loaded
        return {
          id: restaurant.id,
          name: restaurant.name || 'Restaurant',
          cuisine: 'Various',
          rating: 4.5,
          imageUrl: 'https://via.placeholder.com/300x200?text=Restaurant',
          lastOrderDate: restaurant.lastOrderDate
        }
      }
    })
    
    const restaurantDetails = await Promise.all(restaurantPromises)
    recentRestaurants.value = restaurantDetails
    
    // If we couldn't get any details, use fallback data
    if (recentRestaurants.value.length === 0) {
      recentRestaurants.value = [
        {
          id: '1',
          name: 'Burger Palace',
          rating: 4.7,
          cuisine: 'American',
          imageUrl: 'https://images.unsplash.com/photo-1571091718767-18b5b1457add?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8MTB8fGJ1cmdlcnxlbnwwfHwwfHw%3D&auto=format&fit=crop&w=500&q=60'
        },
        {
          id: '2',
          name: 'Pizza Heaven',
          rating: 4.5,
          cuisine: 'Italian',
          imageUrl: 'https://images.unsplash.com/photo-1513104890138-7c749659a591?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8cGl6emF8ZW58MHwwfDB8fA%3D%3D&auto=format&fit=crop&w=500&q=60'
        },
        {
          id: '3',
          name: 'Sushi Express',
          rating: 4.8,
          cuisine: 'Japanese',
          imageUrl: 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8NXx8c3VzaGl8ZW58MHwwfDB8fA%3D%3D&auto=format&fit=crop&w=500&q=60'
        }
      ]
    }
  } catch (err) {
    console.error('Error fetching recent restaurants:', err)
    // Fallback to default data
    recentRestaurants.value = [
      {
        id: '1',
        name: 'Burger Palace',
        rating: 4.7,
        cuisine: 'American',
        imageUrl: 'https://images.unsplash.com/photo-1571091718767-18b5b1457add?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8MTB8fGJ1cmdlcnxlbnwwfHwwfHw%3D&auto=format&fit=crop&w=500&q=60'
      },
      {
        id: '2',
        name: 'Pizza Heaven',
        rating: 4.5,
        cuisine: 'Italian',
        imageUrl: 'https://images.unsplash.com/photo-1513104890138-7c749659a591?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8Mnx8cGl6emF8ZW58MHwwfDB8fA%3D%3D&auto=format&fit=crop&w=500&q=60'
      },
      {
        id: '3',
        name: 'Sushi Express',
        rating: 4.8,
        cuisine: 'Japanese',
        imageUrl: 'https://images.unsplash.com/photo-1579871494447-9811cf80d66c?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxzZWFyY2h8NXx8c3VzaGl8ZW58MHwwfDB8fA%3D%3D&auto=format&fit=crop&w=500&q=60'
      }
    ]
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

.recent-restaurants {
  background: linear-gradient(135deg, #f5f7ff 0%, #edf0ff 100%);
}

.restaurant-card {
  padding: 0 0.5rem;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.cta-section {
  padding: 80px 20px;
  background: linear-gradient(135deg, #4a6cf7 0%, #3452db 100%);
  color: white;
  margin-top: 3rem;
}

.cta-content {
  text-align: center;
  max-width: 800px;
  margin: 0 auto;
}

.cta-section h2 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 16px;
}

.cta-section p {
  font-size: 1.3rem;
  margin-bottom: 32px;
  opacity: 0.9;
}

.cta-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: white;
  color: #4a6cf7;
  padding: 16px 32px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1.1rem;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.cta-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.3);
}

.carousel-container {
  margin: 0 auto;
  max-width: 100%;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .section-title {
    font-size: 2rem;
  }
  
  .cta-section h2 {
    font-size: 2rem;
  }
  
  .cta-section p {
    font-size: 1.1rem;
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
