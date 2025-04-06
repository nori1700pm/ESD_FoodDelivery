<template>
  <div class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold mb-6 flex items-center">
      <vue-feather type="list" size="28" class="mr-2" /> My Delivery History
    </h1>

    <!-- Loading animation while fetching orders -->
    <div v-if="loading" class="flex justify-center items-center h-64">
      <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>

    <!-- Error state -->
    <div v-else-if="error" class="text-center py-10">
      <p class="text-red-500 text-lg">{{ error }}</p>
      <button @click="fetchDriverOrders" class="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
        Try Again
      </button>
    </div>

    <!-- No orders state -->
    <div v-else-if="orders.length === 0" class="text-center py-16 bg-white rounded-lg shadow-lg">
      <vue-feather type="package" size="64" class="mx-auto text-gray-400 mb-4" />
      <h2 class="text-2xl font-bold mb-2">No delivery history</h2>
      <p class="text-gray-600 mb-6">Your completed and cancelled deliveries will appear here</p>
      <p class="text-gray-500 mb-2">Check the Active Delivery page for current assignments</p>
    </div>

    <!-- Orders list -->
    <div v-else class="space-y-6">
      <div v-for="order in completedOrders" :key="order.orderId" class="bg-white rounded-lg shadow-lg overflow-hidden">
        <div class="p-6">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h2 class="text-xl font-bold">
                {{ order.restaurantName || "Restaurant" }}
              </h2>
              <p class="text-gray-600 flex items-center mt-1">
                <vue-feather type="clock" size="16" class="mr-1" />
                {{ formatDate(order.createdAt) }}
              </p>
            </div>

            <!-- Status badges -->
            <div :class="`px-3 py-1 rounded-full ${getStatusColor(order.status)}`">
              {{ order.status }}
            </div>
          </div>

          <!-- Order details -->
          <div class="border-t border-b py-4 mb-4">
            <div class="mb-3">
              <span class="text-gray-500">Order ID: </span>
              <span class="font-medium">{{ order.orderId }}</span>
            </div>

            <div class="mb-3">
              <span class="text-gray-500">Delivered on: </span>
              <span class="font-medium">{{ formatDate(order.updatedAt) }}</span>
            </div>

            <!-- Order items -->
            <h3 class="font-medium text-gray-700 mb-2">Items:</h3>
            <div v-for="(item, index) in order.items" :key="index" class="flex justify-between mb-2 pl-2">
              <span>{{ item.quantity }} × {{ item.name }}</span>
              <span>${{ (item.price * item.quantity).toFixed(2) }}</span>
            </div>
          </div>

          <!-- Delivery address -->
          <div class="flex items-start mb-4">
            <vue-feather type="map-pin" size="18" class="mr-2 mt-1 flex-shrink-0" />
            <p class="text-gray-700">{{ order.deliveryAddress }}</p>
          </div>

          <!-- Total price -->
          <div class="flex justify-between items-center">
            <span class="font-bold">Total</span>
            <span class="font-bold">${{ order.price.toFixed(2) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import VueFeather from 'vue-feather'
import { storeToRefs } from 'pinia'
import axios from 'axios'

const auth = useAuthStore()
const { user } = storeToRefs(auth)

const orders = ref([])
const loading = ref(true)
const error = ref(null)
const pollInterval = ref(null)
const driverId = ref('')

// Compute the completed orders only
const completedOrders = computed(() => {
  return orders.value
    .filter(order => ['DELIVERED', 'COMPLETED', 'CANCELLED'].includes(order.status))
    .sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
})

const ORDER_SERVICE_URL = 'http://localhost:8000'
const GETDRIVERBYEMAIL_SERVICE_URL = 'http://localhost:8000'
const AUTO_REFRESH_INTERVAL = 120000 // 2 minutes - longer interval for history page

onMounted(async () => {
  if (user.value && user.value.email) {
    await fetchDriverId(user.value.email)
    startPolling()
  }
})

onUnmounted(() => {
  stopPolling()
})

const fetchDriverId = async (email) => {
  try {
    loading.value = true
    const response = await axios.get(`${GETDRIVERBYEMAIL_SERVICE_URL}${email}/`)
    driverId.value = response.data["Driver"]["DriverId"]
    await fetchDriverOrders()
  } catch (error) {
    console.error('Error fetching driver data:', error)
    error.value = "Failed to load driver information. Please try again later."
    loading.value = false
  }
}

const startPolling = () => {
  pollInterval.value = setInterval(async () => {
    await fetchDriverOrders()
  }, AUTO_REFRESH_INTERVAL)
}

const stopPolling = () => {
  if (pollInterval.value) {
    clearInterval(pollInterval.value)
    pollInterval.value = null
  }
}

const fetchDriverOrders = async () => {
  if (!driverId.value) return

  try {
    loading.value = true
    error.value = null

    const response = await axios.get(`${ORDER_SERVICE_URL}/orders?driverId=${driverId.value}`)
    console.log('Raw orders response:', response.data)

    if (response.data && Array.isArray(response.data)) {
      // Process orders
      orders.value = response.data
        .map(order => {
          const orderId = order.orderId || order.id
          console.log('Processing order:', { orderId, order })

          const parseSGDate = (dateStr) => {
            if (!dateStr) return new Date()
            if (!dateStr.includes('Z') && !dateStr.includes('+')) {
              return new Date(dateStr + '+08:00')
            }
            return new Date(dateStr)
          }

          return {
            orderId: orderId,
            id: orderId,
            customerId: order.customerId,
            createdAt: parseSGDate(order.createdAt),
            updatedAt: parseSGDate(order.updatedAt),
            deliveryAddress: order.deliveryAddress || '',
            items: order.items || [],
            paymentStatus: order.paymentStatus || 'PENDING',
            driverStatus: order.driverStatus || 'PENDING',
            price: parseFloat(order.price) || 0,
            restaurantId: order.restaurantId || '',
            restaurantName: order.restaurantName || 'Restaurant',
            status: order.status || 'PENDING',
            driverId: order.driverId || null
          }
        })
    } else {
      orders.value = []
    }
  } catch (err) {
    console.error("Error fetching orders:", err)
    error.value = "Failed to load your delivery history. Please try again later."
  } finally {
    loading.value = false
  }
}

const getStatusColor = (status) => {
  switch (status) {
    case 'COMPLETED':
    case 'DELIVERED':
    case 'PAID':
      return 'bg-green-100 text-green-800'
    case 'PENDING':
      return 'bg-yellow-100 text-yellow-800'
    case 'ASSIGNED':
    case 'IN_PROGRESS':
      return 'bg-blue-100 text-blue-800'
    case 'CANCELLED':
    case 'PAYMENT_FAILED':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const formatDate = (timestamp) => {
  try {
    const options = {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
      timeZone: 'Asia/Singapore'
    }

    // Parse the ISO timestamp
    let date
    if (typeof timestamp === 'string') {
      // If the timestamp doesn't include timezone info, assume it's in SGT
      if (!timestamp.includes('Z') && !timestamp.includes('+')) {
        date = new Date(timestamp + '+08:00')
      } else {
        date = new Date(timestamp)
      }
    } else if (timestamp instanceof Date) {
      date = timestamp
    } else {
      return 'Unknown date'
    }

    // Validate the date
    if (isNaN(date.getTime())) {
      return 'Unknown date'
    }

    return new Intl.DateTimeFormat('en-SG', options).format(date)
  } catch (error) {
    console.error('Error formatting date:', error)
    return 'Unknown date'
  }
}
</script>
