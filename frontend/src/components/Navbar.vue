<template>
  <div class="sticky top-0 z-50">
    <nav class="bg-white shadow-lg">
      <div class="container mx-auto px-4">
        <div class="flex justify-between items-center h-16">
          <router-link to="/" class="text-2xl font-bold text-blue-600">
            FoodDelivery
          </router-link>
          
          <div v-if="user" class="flex items-center space-x-4">
            <div class="md:flex md:items-center space-x-4">
              <!-- Show different nav links for drivers -->
              <template v-if="isDriver">
                <router-link to="/activeOrder" class="text-gray-800 hover:text-blue-600 px-3 py-2">
                  Active Delivery
                </router-link>
                <router-link to="/driver-orders" class="text-gray-800 hover:text-blue-600 px-3 py-2">
                  Delivery History
                </router-link>
              </template>
              
              <!-- Regular customer navigation -->
              <template v-else>
                <router-link to="/restaurants" class="text-gray-800 hover:text-blue-600 px-3 py-2">
                  Restaurants
                </router-link>
                <router-link v-if="user" to="/orders" class="text-gray-800 hover:text-blue-600 px-3 py-2">
                  Orders
                </router-link>
              </template>
            </div>
            
            <div v-if="loading">Loading...</div>
            <template v-else>
              <!-- Show cart and wallet only for customers, not drivers -->
              <template v-if="!isDriver">
                <router-link to="/cart" class="relative">
                  <vue-feather type="shopping-cart" size="24"></vue-feather>
                  <span 
                    v-if="items.length > 0" 
                    class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs"
                  >
                    {{ items.length }}
                  </span>
                </router-link>
                
                <router-link to="/wallet">
                  <vue-feather type="credit-card" size="24"></vue-feather>
                </router-link>
              </template>
              
              <div class="relative">
                <button 
                  ref="buttonRef"
                  @click="toggleMenu"
                  class="flex items-center focus:outline-none"
                  :aria-expanded="isMenuOpen"
                  aria-haspopup="true"
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
                      @click="handleMenuItemClick"
                    >
                      Active Delivery
                    </router-link>
                    <router-link
                      to="/driver-orders"
                      class="block px-4 py-2 text-gray-800 hover:bg-gray-100"
                      @click="handleMenuItemClick"
                    >
                      Delivery History
                    </router-link>
                  </template>
                  <template v-else>
                    <router-link
                      to="/profile"
                      class="block px-4 py-2 text-gray-800 hover:bg-gray-100"
                      @click="handleMenuItemClick"
                    >
                      My Profile
                    </router-link>
                    <router-link
                      to="/orders"
                      class="block px-4 py-2 text-gray-800 hover:bg-gray-100"
                      @click="handleMenuItemClick"
                    >
                      My Orders
                    </router-link>
                    <router-link
                      to="/wallet"
                      class="block px-4 py-2 text-gray-800 hover:bg-gray-100"
                      @click="handleMenuItemClick"
                    >
                      My Wallet
                    </router-link>
                  </template>
                  <button
                    @click="handleLogout"
                    class="block w-full text-left px-4 py-2 text-gray-800 hover:bg-gray-100"
                  >
                    Logout
                  </button>
                </div>
              </div>
            </template>
          </div>
        </div>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useCartStore } from '../stores/cart'
import VueFeather from 'vue-feather'
import { storeToRefs } from 'pinia'

const auth = useAuthStore()
const cart = useCartStore()

const { user, loading } = storeToRefs(auth)
const { items } = storeToRefs(cart)

// Initialize the cart when the navbar mounts
cart.initCart()

const isMenuOpen = ref(false)
const menuRef = ref(null)
const buttonRef = ref(null)

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
}

// Close the menu when an option is selected
const handleMenuItemClick = () => {
  isMenuOpen.value = false
}

// Handle logout with menu close
const handleLogout = async () => {
  try {
    await auth.logout()
    isMenuOpen.value = false
    // Redirect to login page after logout
    window.location.href = '/login'
  } catch (error) {
    console.error("Logout error:", error)
  }
}

// Handle click outside to close the menu
const handleClickOutside = (event) => {
  if (
    menuRef.value && 
    buttonRef.value && 
    !menuRef.value.contains(event.target) &&
    !buttonRef.value.contains(event.target)
  ) {
    isMenuOpen.value = false
  }
}

const isDriver = computed(() => {
  return user.value && user.value.email && user.value.email.endsWith('@driver.com')
})

onMounted(() => {
  document.addEventListener('mousedown', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('mousedown', handleClickOutside)
})
</script>
