<template>

  <!-- loading animation while fetching orders ; error if fetchOrders failed -->
  <div v-if="loading" class="flex justify-center items-center h-64">
    <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
  </div>

  <div v-else-if="error" class="text-center py-10">
    <p class="text-red-500 text-lg">{{ error }}</p>
    <button 
      @click="fetchOrders"
      class="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
    >
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
              <h2 class="text-xl font-bold">{{ order.restaurantName }}</h2>
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
import { ref, onMounted } from 'vue'
import { collection, query, where, getDocs, orderBy, Timestamp } from 'firebase/firestore'
import { db } from '../config/firebase'
import { useAuthStore } from '../stores/auth'
import VueFeather from 'vue-feather'
import { storeToRefs } from 'pinia'
// import { axios } from 'axios'

const auth = useAuthStore()
const { user } = storeToRefs(auth)

const orders = ref([])
const loading = ref(true)
const error = ref(null)

const localURL = "http://localhost:5173/";


onMounted(async () => {
  if (user.value) {
    await fetchOrders()
  }
})

// to use actually
// const fetchOrders = async () => {
//     const response = await axios.get(`${localURL}/orders`);
//     return response.data;
//   };

// to replace this function to fetch directly from backend after app.py is completed
const fetchOrders = async () => {
  if (!user.value) return
  
  try {
    loading.value = true
    error.value = null
    
    // Firestore must have an index to process both "where" and "orderBy" operations together efficiently
    const ordersQuery = query(
      collection(db, 'orders'),
      where('customerId', '==', user.value.uid),
      orderBy('createdAt', 'desc')
    )
    
    const ordersSnapshot = await getDocs(ordersQuery)
    
    if (ordersSnapshot.empty) {
      orders.value = []
      return
    }
    
    orders.value = ordersSnapshot.docs.map(doc => {
      const data = doc.data()
      return {
        orderID: doc.id,
        createdAt: data.createdAt,
        deliveryAddress: data.deliveryAddress || '',
        items: data.items,
        paymentMethod: data.paymentMethod,
        paymentStatus: data.paymentStatus,
        price: data.price || 0,
        restaurantID: data.restaurantId,
        restaurantName: data.restaurantName || 'Unknown Restaurant',
        serviceCallError: data.serviceCallError, 
        status: data.status || 'PENDING',
        items: data.items || [],
        updatedAt: data.updatedAt
      }
    })
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
      return 'bg-green-100 text-green-800'
    case 'PENDING':
      return 'bg-yellow-100 text-yellow-800'
    case 'ASSIGNED':
    case 'IN_PROGRESS':
      return 'bg-blue-100 text-blue-800'
    case 'CANCELLED':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

const formatDate = (timestamp) => {
  if (!timestamp || !timestamp.toDate) {
    return 'Unknown date'
  }
  
  const date = timestamp.toDate()
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}
</script>
