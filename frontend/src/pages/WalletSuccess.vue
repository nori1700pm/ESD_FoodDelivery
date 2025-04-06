<template>
  <div class="max-w-2xl mx-auto my-10 text-center">
    <div v-if="loading" class="p-10 bg-white rounded-lg shadow-lg">
      <div class="animate-pulse">
        <div class="h-10 w-32 bg-gray-200 rounded mb-4 mx-auto"></div>
        <div class="h-4 w-1/2 bg-gray-200 rounded mb-3 mx-auto"></div>
        <div class="h-4 w-1/3 bg-gray-200 rounded mx-auto"></div>
      </div>
    </div>
    
    <div v-else-if="error" class="p-10 bg-white rounded-lg shadow-lg">
      <vue-feather type="alert-circle" size="60" class="text-red-500 mx-auto mb-4"></vue-feather>
      <h1 class="text-2xl font-bold mb-4">Payment Verification Failed</h1>
      <p class="text-gray-700 mb-6">{{ error }}</p>
      <button 
        @click="$router.push('/wallet')" 
        class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        Return to Wallet
      </button>
    </div>
    
    <div v-else class="p-10 bg-white rounded-lg shadow-lg">
      <vue-feather type="check-circle" size="60" class="text-green-500 mx-auto mb-4"></vue-feather>
      <h1 class="text-2xl font-bold mb-4">Payment Successful!</h1>
      <p class="text-gray-700 mb-2">Your wallet has been topped up with</p>
      <p class="text-3xl font-bold text-green-600 mb-6">${{ amount }}</p>
      
      <div class="mb-6 p-4 bg-gray-50 rounded-lg inline-block">
        <p class="text-gray-700">New Balance: <span class="font-bold">${{ balance }}</span></p>
      </div>
      
      <button 
        @click="$router.push('/wallet')" 
        class="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        Return to Wallet
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useWalletStore } from '../stores/wallet'
import { useAuthStore } from '../stores/auth'
import VueFeather from 'vue-feather'

const route = useRoute()
const router = useRouter()
const wallet = useWalletStore()
const auth = useAuthStore()

const loading = ref(true)
const error = ref(null)
const success = ref(false)
const amount = ref(0)
const balance = ref(0)

onMounted(async () => {
  // Check if user is authenticated
  if (!auth.user) {
    error.value = "You must be logged in to verify payments"
    loading.value = false
    return
  }

  // Check for required query parameters
  const sessionId = route.query.session_id
  const customerId = route.query.customer_id
  const paymentAmount = route.query.amount

  if (!sessionId || !customerId || !paymentAmount) {
    error.value = "Missing payment information"
    loading.value = false
    return
  }

  // Verify that the customer ID matches the logged-in user
  if (customerId !== auth.user.uid) {
    error.value = "Payment verification failed: user mismatch"
    loading.value = false
    return
  }

  try {
    // Process the successful payment
    const result = await wallet.processStripeSuccess(
      sessionId,
      customerId,
      paymentAmount
    )

    if (result.success) {
      success.value = true
      amount.value = parseFloat(paymentAmount).toFixed(2)
      balance.value = result.balance.toFixed(2)
    } else {
      error.value = result.error || "Payment verification failed"
    }
  } catch (err) {
    console.error("Error verifying payment:", err)
    error.value = "An unexpected error occurred"
  } finally {
    loading.value = false
  }
})
</script>
