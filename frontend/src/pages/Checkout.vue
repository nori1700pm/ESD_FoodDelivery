<template>
  <div v-if="success" class="max-w-md mx-auto text-center py-16">
    <div class="bg-green-100 rounded-full w-24 h-24 mx-auto flex items-center justify-center mb-6">
      <vue-feather type="check" size="40" class="text-green-600" />
    </div>
    <h2 class="text-2xl font-bold mb-2">Order Placed Successfully!</h2>
    <p class="text-gray-600 mb-6">
      Your order has been placed and is being processed.
    </p>
    <p class="text-gray-600">
      You'll be redirected to your orders page in a few seconds...
    </p>
  </div>

  <div v-else class="max-w-3xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Checkout</h1>
    
    <div v-if="error" class="bg-red-100 text-red-700 p-4 rounded-lg mb-6">
      {{ error }}
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <div class="bg-white p-6 rounded-lg shadow-lg mb-6">
          <h2 class="text-xl font-semibold mb-4 flex items-center">
            <vue-feather type="map-pin" class="mr-2" /> Delivery Address
          </h2>
          <form>
            <textarea 
              v-model="address"
              class="w-full p-3 border border-gray-300 rounded-md"
              rows="3"
              placeholder="Enter your delivery address"
            ></textarea>
          </form>
        </div>
        
        <div class="bg-white p-6 rounded-lg shadow-lg">
          <h2 class="text-xl font-semibold mb-4 flex items-center">
            <vue-feather type="credit-card" class="mr-2" /> Payment Method
          </h2>
          <div>
            <label class="flex items-center mb-4">
              <input 
                type="radio" 
                name="payment" 
                value="wallet"
                v-model="paymentMethod"
                class="mr-2"
              />
              <span>Wallet (Balance: ${{ balance.toFixed(2) }})</span>
            </label>
            
            <label class="flex items-center">
              <input 
                type="radio" 
                name="payment" 
                value="cod"
                v-model="paymentMethod"
                class="mr-2"
              />
              <span>Cash on Delivery</span>
            </label>
          </div>
        </div>
      </div>
      
      <div class="bg-white p-6 rounded-lg shadow-lg h-fit">
        <h2 class="text-xl font-semibold mb-4">Order Summary</h2>
        
        <div class="space-y-4 mb-4">
          <div v-for="item in items" :key="item.id" class="flex justify-between">
            <span>{{ item.quantity }} × {{ item.name }}</span>
            <span>${{ (item.price * item.quantity).toFixed(2) }}</span>
          </div>
        </div>
        
        <div class="border-t pt-4 mb-4">
          <div class="flex justify-between mb-2">
            <span>Subtotal</span>
            <span>${{ total.toFixed(2) }}</span>
          </div>
          <div class="flex justify-between mb-2">
            <span>Delivery Fee</span>
            <span>${{ deliveryFee.toFixed(2) }}</span>
          </div>
          <div class="flex justify-between font-bold text-lg">
            <span>Total</span>
            <span>${{ totalWithDelivery.toFixed(2) }}</span>
          </div>
        </div>
        
        <button
          @click="handleSubmit"
          :disabled="loading"
          class="w-full bg-blue-600 text-white p-3 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
        >
          {{ loading ? 'Processing...' : 'Place Order' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watchEffect, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'
import VueFeather from 'vue-feather'
import { useCartStore } from '../stores/cart'
import axios from 'axios'

const router = useRouter()
const auth = useAuthStore()
const cart = useCartStore()

const { user } = storeToRefs(auth)
const { items } = storeToRefs(cart)

const address = ref('')
const paymentMethod = ref('wallet')
const loading = ref(false)
const error = ref(null)
const success = ref(false)
const deliveryFee = ref(2.99)
const balance = ref(0)

const total = computed(() => 
  items.value.reduce((sum, item) => sum + (item.price * item.quantity), 0)
)
const totalWithDelivery = computed(() => total.value + deliveryFee.value)

// Configure API endpoint for pay-for-delivery service
const PAY_DELIVERY_SERVICE_URL = 'http://localhost:5003'

const getProfileAndBalance = async () => {
  if (!user.value) {
    console.log('No user found, skipping profile and balance fetch')
    return
  }

  try {
    console.log(`Fetching user profile and balance for user ID: ${user.value.uid}`)
    const response = await fetch(`${PAY_DELIVERY_SERVICE_URL}/user-profile/${user.value.uid}`)
    const result = await response.json()
    console.log('Raw profile response:', result)

    if (!response.ok) {
      throw new Error(result.message || 'Failed to fetch user profile')
    }
    
    if (result.code === 200 && result.data) {
      console.log('Profile data received:', result.data)
      // Set address if available
      if (result.data.address) {
        console.log('Setting address:', result.data.address)
        address.value = result.data.address
      }
      // Set balance if available
      if (result.data.balance !== undefined) {
        console.log('Setting balance:', result.data.balance)
        balance.value = result.data.balance
      }
    } else {
      console.warn('Invalid profile data format:', result)
      throw new Error('Invalid profile data format')
    }
  } catch (err) {
    console.error('Error fetching user data:', err)
    error.value = `Unable to load user data: ${err.message}`
  }
}

// Single watcher for user changes
watch(user, async (newUser) => {
  if (newUser) {
    await getProfileAndBalance()
  } else {
    balance.value = 0
    address.value = ''
  }
}, { immediate: true })

onMounted(() => {
  console.log('Component mounted')
  cart.initCart() 
})

const handleSubmit = async () => {
  if (!address.value) {
    error.value = 'Please provide a delivery address'
    return
  }
  
  if (!user.value) {
    error.value = 'User not authenticated'
    return
  }
  
  try {
    loading.value = true
    error.value = null
    console.log('=== Starting Checkout Process ===')
    
    const tempOrderId = `order-${Date.now()}-${user.value.uid.slice(0, 8)}`
    
    const paymentResponse = await fetch(`${PAY_DELIVERY_SERVICE_URL}/pay-delivery`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        custId: user.value.uid,
        orderId: tempOrderId,
        amount: totalWithDelivery.value
      })
    })
    
    const paymentResult = await paymentResponse.json()
    console.log('Payment result:', paymentResult)
    
    if (paymentResult.code !== 200) {
      throw new Error(paymentResult.message || 'Payment processing failed')
    }

    // Update balance from pay-for-delivery response
    if (paymentResult.data?.wallet_result?.newBalance !== undefined) {
      balance.value = paymentResult.data.wallet_result.newBalance
    }
    
    await cart.clearCart()
    success.value = true
    setTimeout(() => {
      router.push('/orders')
    }, 3000)
    
  } catch (err) {
    console.error('Checkout error:', err)
    error.value = err.message || 'An error occurred during checkout'
  } finally {
    loading.value = false
  }
}
</script>