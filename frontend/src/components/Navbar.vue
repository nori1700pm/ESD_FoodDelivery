<template>
  <div class="sticky top-0 z-50">
    <nav class="bg-white shadow-lg">
      <div class="container mx-auto px-4">
        <div class="flex justify-between items-center h-16">
          <router-link to="/" class="flex items-center">
            <img src="@/assets/nomnomgo-logo.jpg" alt="NomNomGo Logo" class="h-10 w-auto mr-2">
            <span class="text-2xl font-bold text-blue-600">NomNomGo</span>
          </router-link>
          
          <div v-if="user" class="flex items-center space-x-4">
            <div class="md:flex md:items-center space-x-4 relative nav-links-container">
              <!-- Background slide indicator -->
              <div class="bg-indicator" ref="bgIndicator"></div>
              
              <!-- Show different nav links for drivers -->
              <template v-if="isDriver">
                <router-link to="/activeOrder" class="nav-link" :class="{ 'is-active': isActive('/activeOrder') }">
                  Active Delivery
                </router-link>
                <router-link to="/driver-orders" class="nav-link" :class="{ 'is-active': isActive('/driver-orders') }">
                  Delivery History
                </router-link>
              </template>
              
              <!-- Regular customer navigation -->
              <template v-else>
                <router-link to="/restaurants" class="nav-link" :class="{ 'is-active': isActive('/restaurants') }">
                  Restaurants
                </router-link>
                <router-link v-if="user" to="/orders" class="nav-link" :class="{ 'is-active': isActive('/orders') }">
                  Orders
                </router-link>
              </template>
            </div>
            
            <div v-if="loading" class="flex items-center">
              <loading-spinner type="spinner" size="small" :showText="false" />
            </div>
            <template v-else>
              <!-- Show cart and wallet only for customers, not drivers -->
              <template v-if="!isDriver">
                <div class="flex items-center space-x-4">
                  <router-link to="/cart" class="action-icon relative flex items-center" :class="{ 'text-blue-600': isActive('/cart') }">
                    <vue-feather type="shopping-cart" size="24"></vue-feather>
                    <span 
                      v-if="items.length > 0" 
                      class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs"
                    >
                      {{ items.length }}
                    </span>
                  </router-link>
                  
                  <router-link to="/wallet" class="action-icon flex items-center" :class="{ 'text-blue-600': isActive('/wallet') }">
                    <vue-feather type="credit-card" size="24"></vue-feather>
                  </router-link>
                </div>
              </template>
              
              <div class="relative">
                <button 
                  ref="buttonRef"
                  @click="toggleMenu"
                  class="action-icon flex items-center focus:outline-none"
                  :aria-expanded="isMenuOpen"
                  aria-haspopup="true"
                  :class="{ 'text-blue-600': isMenuOpen || isProfileActive() }"
                >
                  <vue-feather type="user" size="24" class="cursor-pointer"></vue-feather>
                </button>
                
                <div 
                  v-if="isMenuOpen" 
                  ref="menuRef"
                  class="absolute right-0 w-48 mt-2 bg-white rounded-md shadow-lg z-10"
                >
                  <template v-if="isDriver">
                    <router-link
                      to="/activeOrder"
                      class="block px-4 py-2 text-gray-800 hover:bg-gray-100"
                      :class="{ 'bg-blue-50 text-blue-600': isActive('/activeOrder') }"
                      @click="handleMenuItemClick"
                    >
                      Active Delivery
                    </router-link>
                    <router-link
                      to="/driver-orders"
                      class="block px-4 py-2 text-gray-800 hover:bg-gray-100"
                      :class="{ 'bg-blue-50 text-blue-600': isActive('/driver-orders') }"
                      @click="handleMenuItemClick"
                    >
                      Delivery History
                    </router-link>
                  </template>
                  <template v-else>
                    <router-link
                      to="/profile"
                      class="block px-4 py-2 text-gray-800 hover:bg-gray-100"
                      :class="{ 'bg-blue-50 text-blue-600': isActive('/profile') }"
                      @click="handleMenuItemClick"
                    >
                      My Profile
                    </router-link>
                    <router-link
                      to="/orders"
                      class="block px-4 py-2 text-gray-800 hover:bg-gray-100"
                      :class="{ 'bg-blue-50 text-blue-600': isActive('/orders') }"
                      @click="handleMenuItemClick"
                    >
                      My Orders
                    </router-link>
                    <router-link
                      to="/wallet"
                      class="block px-4 py-2 text-gray-800 hover:bg-gray-100"
                      :class="{ 'bg-blue-50 text-blue-600': isActive('/wallet') }"
                      @click="handleMenuItemClick"
                    >
                      My Wallet
                    </router-link>
                  </template>
                  <button
                    @click="handleLogout"
                    class="block w-full text-left px-4 py-2 text-gray-800 hover:bg-gray-100 border-t"
                  >
                    Sign Out
                  </button>
                </div>
              </div>
            </template>
          </div>
          
          <div v-else class="space-x-4">
            <router-link 
              to="/login"
              class="px-4 py-2 border border-blue-600 text-blue-600 rounded-md hover:bg-blue-50 transition-colors"
              :class="{ 'bg-blue-600 text-white hover:bg-blue-700': isActive('/login') }"
            >
              Sign In
            </router-link>
            <router-link 
              to="/register"
              class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              :class="{ 'bg-blue-700': isActive('/register') }"
            >
              Register
            </router-link>
          </div>
        </div>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted, watchEffect, onUnmounted, computed, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart'
import { storeToRefs } from 'pinia'
import VueFeather from 'vue-feather'
import LoadingSpinner from './LoadingSpinner.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const cart = useCartStore()

const { user, loading } = storeToRefs(auth)
const { items } = storeToRefs(cart)

const buttonRef = ref(null)
const menuRef = ref(null)
const bgIndicator = ref(null)
const isMenuOpen = ref(false)

const isDriver = computed(() => {
  return user.value && user.value.email && user.value.email.endsWith('@driver.com')
})

// Function to check if current route matches
const isActive = (path) => {
  // Handle exact matches
  if (route.path === path) return true
  
  // Handle child routes - if the current path starts with the given path
  if (path !== '/' && route.path.startsWith(path)) return true
  
  return false
}

// Check if any profile-related routes are active
const isProfileActive = () => {
  const profileRoutes = ['/profile', '/wallet', '/orders']
  if (isDriver.value) {
    profileRoutes.push('/activeOrder', '/driver-orders')
  }
  return profileRoutes.some(path => isActive(path))
}

// Update the background indicator position and size
const updateBgIndicator = async () => {
  await nextTick()
  
  if (!bgIndicator.value) return
  
  const activeLink = document.querySelector('.nav-link.is-active')
  if (!activeLink) {
    // If no active link, hide the indicator
    bgIndicator.value.style.opacity = '0'
    return
  }
  
  // Set the position and dimensions of the indicator
  const { offsetLeft, offsetWidth, offsetHeight } = activeLink
  bgIndicator.value.style.left = `${offsetLeft}px`
  bgIndicator.value.style.width = `${offsetWidth}px`
  bgIndicator.value.style.height = `${offsetHeight}px`
  bgIndicator.value.style.opacity = '1'
}

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

const handleMenuItemClick = () => {
  isMenuOpen.value = false
}

const handleLogout = async () => {
  try {
    isMenuOpen.value = false
    await auth.logout()
    router.push('/login')
  } catch (err) {
    console.error('Logout error:', err)
  }
}

const clickOutsideHandler = (event) => {
  if (
    isMenuOpen.value &&
    buttonRef.value &&
    menuRef.value &&
    !buttonRef.value.contains(event.target) &&
    !menuRef.value.contains(event.target)
  ) {
    isMenuOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', clickOutsideHandler)
  updateBgIndicator()
  
  // Add resize event listener to update indicator when window is resized
  window.addEventListener('resize', updateBgIndicator)
})

onUnmounted(() => {
  document.removeEventListener('click', clickOutsideHandler)
  window.removeEventListener('resize', updateBgIndicator)
})

// Initialize cart when component mounts
watchEffect(() => {
  if (user.value && !isDriver.value) {
    cart.initCart()
  }
})

// Watch for route changes to update the indicator
watch(
  () => route.path,
  () => {
    updateBgIndicator()
  }
)
</script>

<style scoped>
.nav-links-container {
  position: relative;
  display: flex;
  align-items: center;
}

.nav-link {
  @apply text-gray-800 hover:text-blue-600 px-3 py-2 rounded transition-colors duration-200 relative z-10;
}

.is-active {
  @apply text-blue-600 font-medium;
  /* Remove bg-blue-50 since we now have the animated background */
}

.bg-indicator {
  position: absolute;
  background-color: #EBF5FF; /* lighter blue, similar to blue-50 */
  border-radius: 0.375rem; /* rounded */
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  z-index: 1;
}

.action-icon {
  @apply hover:text-blue-600 transition-colors duration-200;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px; /* Fixed height for all icons */
}
</style>
