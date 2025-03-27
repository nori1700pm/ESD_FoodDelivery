<template>
    <div class="max-w-4xl mx-auto">
        <h1 class="text-3xl font-bold mb-6 flex items-center">
            <vue-feather type="truck" size="28" class="mr-2" /> Driver Dashboard
        </h1>
        
        <!-- Loading state -->
        <div v-if="loading" class="flex justify-center items-center h-64">
            <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
        
        <!-- Error state -->
        <div v-else-if="error" class="bg-red-100 p-4 rounded-lg mb-6 text-red-700">
            {{ error }}
        </div>
        
        <!-- No active orders state -->
        <div v-else-if="!activeOrder" class="bg-yellow-50 p-6 rounded-lg shadow-md text-center">
            <vue-feather type="coffee" size="48" class="mx-auto mb-4 text-yellow-500" />
            <h2 class="text-2xl font-bold mb-2">No Active Orders</h2>
            <p class="text-gray-600">You don't have any assigned deliveries at the moment.</p>
            <p class="text-gray-500 mt-2">Please wait for the system to assign you a delivery.</p>
        </div>
        
        <!-- Active order -->
        <div v-else class="bg-white rounded-lg shadow-lg overflow-hidden">
            <!-- Order header with restaurant info -->
            <div class="bg-blue-50 p-5 border-b flex items-start justify-between">
                <div>
                    <h2 class="text-xl font-bold mb-1">{{ activeOrder.restaurantName || "Restaurant" }}</h2>
                    <div class="flex items-center text-blue-600">
                        <vue-feather type="map-pin" size="16" class="mr-2" />
                        <p>Restaurant #{{ activeOrder.restaurantId }}</p>
                    </div>
                </div>
                
                <div :class="`px-3 py-1 rounded-full ${getStatusColor(activeOrder.status)}`">
                    {{ activeOrder.status }}
                </div>
            </div>
            
            <!-- Restaurant image if available -->
            <div v-if="restaurantImage" class="h-48 overflow-hidden relative">
                <img :src="restaurantImage" alt="Restaurant Image" class="w-full object-cover">
            </div>
            
            <!-- Customer details section -->
            <div class="p-5 border-b">
                <h3 class="font-bold mb-3 flex items-center">
                    <vue-feather type="user" size="18" class="mr-2" />
                    Delivery Information
                </h3>
                
                <div class="flex items-start mb-4">
                    <vue-feather type="map-pin" size="18" class="mr-3 mt-1 flex-shrink-0" />
                    <div>
                        <h4 class="font-semibold">Delivery Address</h4>
                        <p class="text-gray-700">{{ activeOrder.deliveryAddress }}</p>
                    </div>
                </div>
                
                <div class="flex items-start mb-4">
                    <vue-feather type="clock" size="18" class="mr-3 mt-1 flex-shrink-0" />
                    <div>
                        <h4 class="font-semibold">Order Time</h4>
                        <p class="text-gray-700">{{ formatDate(activeOrder.createdAt) }}</p>
                    </div>
                </div>
                
                <div class="flex items-start">
                    <vue-feather type="hash" size="18" class="mr-3 mt-1 flex-shrink-0" />
                    <div>
                        <h4 class="font-semibold">Order ID</h4>
                        <p class="text-gray-700">{{ activeOrder.orderId }}</p>
                    </div>
                </div>
            </div>
            
            <!-- Order items -->
            <div class="p-5 border-b">
                <h3 class="font-bold mb-3">Order Items</h3>
                <ul class="divide-y">
                    <li v-for="item in activeOrder.items" :key="item.id" class="py-3 flex justify-between">
                        <div>
                            <span class="font-medium">{{ item.name }}</span>
                            <span class="text-gray-500 ml-2">x{{ item.quantity }}</span>
                        </div>
                        <span>${{ (item.price * item.quantity).toFixed(2) }}</span>
                    </li>
                </ul>
            </div>
            
            <!-- Order totals -->
            <div class="p-5 bg-gray-50">
                <div class="flex justify-between font-bold text-lg">
                    <span>Total</span>
                    <span>${{ activeOrder.price.toFixed(2) }}</span>
                </div>
            </div>
            
            <!-- Customer info -->
            <div class="p-5 border-t">
                <h3 class="font-bold mb-3 flex items-center">
                    <vue-feather type="user" size="18" class="mr-2" />
                    Customer Information
                </h3>
                <div v-if="customerInfo" class="space-y-2">
                    <p><span class="font-semibold">Name:</span> {{ customerInfo.name }}</p>
                    <p><span class="font-semibold">Email:</span> {{ customerInfo.email }}</p>
                    <p v-if="customerInfo.phone"><span class="font-semibold">Phone:</span> {{ customerInfo.phone }}</p>
                </div>
                <div v-else class="italic text-gray-500">Customer information not available</div>
            </div>
            
            <!-- Delivery actions -->
            <div class="p-5 border-t">
                <h3 class="font-bold mb-3">Delivery Status</h3>
                <div class="flex space-x-4">
                    <button 
                        @click="updateOrderStatus('IN_PROGRESS')" 
                        class="flex-1 bg-blue-600 text-white p-3 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
                        :disabled="activeOrder.status !== 'ASSIGNED' && activeOrder.status !== 'PENDING' && activeOrder.status !== 'PAID'"
                    >
                        Start Delivery
                    </button>
                    
                    <button 
                        @click="updateOrderStatus('DELIVERED')" 
                        class="flex-1 bg-green-600 text-white p-3 rounded-md hover:bg-green-700 disabled:bg-green-300"
                        :disabled="activeOrder.status !== 'IN_PROGRESS'"
                    >
                        Complete Delivery
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'
import axios from 'axios'
import { db } from '@/config/firebase'
import { doc, getDoc } from "firebase/firestore"
import VueFeather from 'vue-feather'

const orders = ref([])
const activeOrder = ref(null)
const driverId = ref('')
const restaurantDetails = ref(null)
const restaurantImage = ref('')
const customerInfo = ref(null)
const loading = ref(true)
const error = ref(null)

const auth = useAuthStore()
const { user } = storeToRefs(auth)

const GETDRIVERBYEMAIL_SERVICE_URL = 'https://personal-shkrtsry.outsystemscloud.com/DriverServiceModule/rest/NomNomGo/drivers/'
const ORDER_SERVICE_URL = 'http://localhost:5001'
const CUSTOMER_SERVICE_URL = 'http://localhost:4000'

const fetchDriverInfo = async (email) => {
    try {
        loading.value = true
        const response = await axios.get(`${GETDRIVERBYEMAIL_SERVICE_URL}${email}/`)
        driverId.value = response.data["Driver"]["DriverId"]
        await fetchAllOrders()
    } catch (error) {
        console.error('Error fetching driver data', error.message)
        error.value = "Failed to load driver information. Please try again later."
    } finally {
        loading.value = false
    }
}

// Watch for user changes
watch(user, (newUser) => {
    if (newUser && newUser.email) {
        console.log('User email:', newUser.email)
        fetchDriverInfo(newUser.email)
    }
}, { immediate: true })

const fetchAllOrders = async () => {
    try {
        loading.value = true
        // Get orders assigned to this driver specifically
        const response = await axios.get(`${ORDER_SERVICE_URL}/orders?driverId=${driverId.value}`)
        orders.value = response.data
        await processOrders()
    } catch (error) {
        console.error('Error fetching orders', error.message)
        error.value = "Failed to load orders. Please try again later."
    } finally {
        loading.value = false
    }
}

const processOrders = async () => {
    if (!driverId.value || !orders.value.length) {
        activeOrder.value = null
        return
    }
    
    // Find the first active order assigned to this driver - non-completed orders
    const assignedOrder = orders.value.find(order => 
        order.driverId === driverId.value && 
        ['ASSIGNED', 'PENDING', 'PAID', 'IN_PROGRESS'].includes(order.status)
    )
    
    if (assignedOrder) {
        console.log('Found assigned order:', assignedOrder)
        activeOrder.value = assignedOrder
        
        // If we have a restaurant ID, fetch its details
        if (assignedOrder.restaurantId) {
            await fetchRestaurantById(assignedOrder.restaurantId)
        }
        
        // Fetch customer information
        if (assignedOrder.customerId) {
            await fetchCustomerInfo(assignedOrder.customerId)
        }
    } else {
        activeOrder.value = null
        restaurantImage.value = ''
        customerInfo.value = null
    }
}

const fetchRestaurantById = async (restaurantId) => {
    try {
        const docRef = doc(db, 'restaurants', restaurantId)
        const docSnap = await getDoc(docRef)

        if (!docSnap.exists()) {
            console.warn("Restaurant not found")
            return
        }

        restaurantDetails.value = { id: docSnap.id, ...docSnap.data() }
        restaurantImage.value = restaurantDetails.value.imageUrl 
    } catch (err) {
        console.error("Error fetching restaurant:", err)
    }
}

const fetchCustomerInfo = async (customerId) => {
    try {
        const response = await axios.get(`${CUSTOMER_SERVICE_URL}/customers/${customerId}`)
        customerInfo.value = response.data
        console.log("Fetched customer info:", customerInfo.value)
    } catch (err) {
        console.error("Error fetching customer info:", err)
        customerInfo.value = null
    }
}

const updateOrderStatus = async (newStatus) => {
    if (!activeOrder.value) return
    
    try {
        loading.value = true
        error.value = null
        
        const response = await axios.patch(
            `${ORDER_SERVICE_URL}/orders/${activeOrder.value.orderId}/status`,
            { 
                status: newStatus,
                driverStatus: newStatus
            }
        )
        
        console.log('Order status updated:', response.data)
        
        // Refresh order data
        await fetchAllOrders()
        
    } catch (err) {
        console.error('Error updating order status:', err)
        error.value = `Failed to update order status: ${err.message}`
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

// Set up auto-refresh to check for newly assigned orders
const AUTO_REFRESH_INTERVAL = 30000 // 30 seconds
let pollInterval = null

const startPolling = () => {
    pollInterval = setInterval(async () => {
        if (user.value && user.value.email) {
            await fetchAllOrders()
        }
    }, AUTO_REFRESH_INTERVAL)
}

const stopPolling = () => {
    if (pollInterval) {
        clearInterval(pollInterval)
        pollInterval = null
    }
}

onMounted(() => {
    // Ensure the fetch functions are called once the component is mounted
    if (user.value && user.value.email) {
        fetchDriverInfo(user.value.email)
    }
    // Start polling for updates
    startPolling()
})

onUnmounted(() => {
    // Clean up the polling interval when component is destroyed
    stopPolling()
})
</script>
