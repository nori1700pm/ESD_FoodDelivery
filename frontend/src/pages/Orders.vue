<template>
  <!-- loading animation while fetching orders ; error if fetchOrders failed -->
  <div v-if="loading" class="flex justify-center items-center h-64">
    <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
  </div>

  <div v-else-if="error" class="text-center py-10">
    <p class="text-red-500 text-lg">{{ error }}</p>
    <button @click="fetchOrders" class="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
      Try Again
    </button>
  </div>

  <!-- If all goes well, load all user's orders -->
  <div v-else class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold mb-6 flex items-center">
      <vue-feather type="package" size="28" class="mr-2" /> My Orders
    </h1>

    <!-- if user has no order history  -->
    <div v-if="orders.length === 0" class="text-center py-16 bg-white rounded-lg shadow-lg">
      <vue-feather type="package" size="64" class="mx-auto text-gray-400 mb-4" />
      <h2 class="text-2xl font-bold mb-2">No orders yet</h2>
      <p class="text-gray-600 mb-6">Your order history will appear here</p>
    </div>

    <div v-else class="space-y-6">
      <div v-for="order in orders" :key="order.id" class="bg-white rounded-lg shadow-lg overflow-hidden">
        <div class="p-6">
          <div class="flex justify-between items-start mb-4">
            <div>
              <h2 class="text-xl font-bold">
                {{ getRestaurantDisplay(order) }}
              </h2>
              <p class="text-gray-600 flex items-center mt-1">
                <vue-feather type="clock" size="16" class="mr-1" />
                {{ formatDate(order.createdAt) }}
              </p>
            </div>

            <div :class="`px-3 py-1 rounded-full ${getStatusColor(order.status)}`">
              {{ order.status }}
            </div>
          </div>

          <div class="border-t border-b py-4 mb-4">
            <div v-for="(item, index) in order.items" :key="index" class="flex justify-between mb-2">
              <span>{{ item.quantity }} × {{ item.name }}</span>
              <span>${{ (item.price * item.quantity).toFixed(2) }}</span>
            </div>
          </div>

          <div class="flex items-start mb-4">
            <vue-feather type="map-pin" size="18" class="mr-2 mt-1 flex-shrink-0" />
            <p class="text-gray-700">{{ order.deliveryAddress }}</p>
          </div>

          <div class="flex justify-between items-center">
            <span class="font-bold">Total</span>
            <span class="font-bold">${{ order.price.toFixed(2) }}</span>
          </div>

          <!-- show all order info -->
          <div>
            <div class="mb-4">
              <b> temporarily show all user's orders - will add a filter later </b>
            </div>
            {{ order }}
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { collection, query, where, getDocs, orderBy, Timestamp } from 'firebase/firestore'
import { db } from '../config/firebase'
import { useAuthStore } from '../stores/auth'
import VueFeather from 'vue-feather'
import { storeToRefs } from 'pinia'
import axios from 'axios' // Changed from { axios } to axios

const auth = useAuthStore()
const { user } = storeToRefs(auth)

const orders = ref([])
const loading = ref(true)
const error = ref(null)

const orderServiceURL = "http://localhost:3001/orders"

const pollInterval = ref(null)
//const AUTO_REFRESH_INTERVAL = 10000 // 10 seconds

onMounted(async () => {
  if (user.value) {
    await fetchOrders()
    // Start polling for updates
    //startPolling()
  }
})

// Cleanup on component unmount
onUnmounted(() => {
  stopPolling()
})

// const startPolling = () => {
//   pollInterval.value = setInterval(async () => {
//     await fetchOrders()
//   }, AUTO_REFRESH_INTERVAL)
// }

const stopPolling = () => {
  if (pollInterval.value) {
    clearInterval(pollInterval.value)
    pollInterval.value = null
  }
}

const fetchOrders = async () => {
  if (!user.value) return

  try {
    loading.value = true
    error.value = null

    const response = await axios.get(`${orderServiceURL}?customerId=${user.value.uid}`)
    console.log('Raw orders response:', response.data) // Debug raw response

    if (response.data && Array.isArray(response.data)) {
      orders.value = response.data.map(order => {
        // Better restaurant name handling
        const restaurantName =
          order.restaurantName ||
          order.items?.[0]?.restaurantName ||
          (order.restaurantId ? `Restaurant ${order.restaurantId}` : 'Restaurant')

        return {
          id: order.orderId || order.id,
          createdAt: new Date(order.createdAt),
          deliveryAddress: order.deliveryAddress || '',
          items: order.items || [],
          paymentMethod: order.paymentMethod || '',
          paymentStatus: order.paymentStatus || 'PENDING',
          price: order.price || 0,
          restaurantId: order.restaurantId || '',
          restaurantName: restaurantName,
          status: order.status || 'PENDING',
          updatedAt: new Date(order.updatedAt),
          driverId: order.driverId || null
        }
      })
      console.log('Processed orders:', orders.value) // Debug processed orders
    } else {
      orders.value = []
    }
  } catch (err) {
    console.error("Error fetching orders:", err)
    error.value = "Failed to load your orders. Please try again later."
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
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
      timeZone: 'Asia/Singapore'
    }

    // Convert the timestamp to Singapore time
    if (timestamp instanceof Date) {
      const sgTime = new Date(timestamp.toLocaleString('en-US', { timeZone: 'Asia/Singapore' }))
      return new Intl.DateTimeFormat('en-SG', options).format(sgTime)
    }

    // Handle string dates
    if (typeof timestamp === 'string') {
      const date = new Date(timestamp)
      const sgTime = new Date(date.toLocaleString('en-US', { timeZone: 'Asia/Singapore' }))
      return new Intl.DateTimeFormat('en-SG', options).format(sgTime)
    }

    return 'Unknown date'
  } catch (error) {
    console.error('Error formatting date:', error, 'for timestamp:', timestamp)
    return 'Unknown date'
  }
}

const getRestaurantDisplay = (order) => {
  // First try the order's restaurantName
  console.log('Order data for restaurant display:', order); // Debug log

  if (order.restaurantName && order.restaurantName !== 'Restaurant') {
    return order.restaurantName;
  }

  // Then try the first item's restaurant info
  if (order.items && order.items[0]) {
    const firstItem = order.items[0];
    if (firstItem.restaurantName) {
      return firstItem.restaurantName;
    }
    if (firstItem.restaurant?.name) {
      return firstItem.restaurant.name;
    }
  }

  // Finally, use restaurantId if available
  if (order.restaurantId && order.restaurantId !== 'unknown') {
    return `${order.restaurantName}`;
  }

  return 'Restaurant';
}
</script>