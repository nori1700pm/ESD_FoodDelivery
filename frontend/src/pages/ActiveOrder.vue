<template>
    <div class="max-w-4xl mx-auto">
        <h1 class="text-3xl font-bold mb-6 flex items-center justify-between">
            <div class="flex items-center">
                <vue-feather type="truck" size="28" class="mr-2" /> Driver Dashboard
            </div>
            <div class="flex items-center">
                <span class="mr-3 text-sm font-medium text-gray-700">{{ isAvailable ? 'Available' : 'Busy' }}</span>
                <label class="relative inline-flex items-center cursor-pointer">
                    <input 
                        type="checkbox" 
                        v-model="isAvailable" 
                        class="sr-only peer" 
                        @change="toggleDriverStatus"
                    >
                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
            </div>
        </h1>

        <!-- Show content only if driver is Available -->
        <div v-if="isAvailable">
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
                            <p>{{ restaurantDetails.address }}</p>
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
                        <!-- Start Delivery button - shows when status is PREPARING -->
                        <button v-if="activeOrder.status === 'PREPARING'" @click="updateOrderStatus('READY FOR PICKUP')"
                            class="flex-1 bg-blue-600 text-white p-3 rounded-md hover:bg-blue-700">
                            Start Delivery
                        </button>

                        <!-- Reject Delivery button - shows only when status is PREPARING -->
                        <button v-if="activeOrder.status === 'PREPARING'" @click="rejectDelivery"
                            class="flex-1 bg-gray-600 text-white p-3 rounded-md hover:bg-gray-700">
                            Reject Delivery
                        </button>

                        <!-- Pick Up Order button - shows when status is READY FOR PICKUP -->
                        <button v-if="activeOrder.status === 'READY FOR PICKUP'"
                            @click="updateOrderStatus('OUT FOR DELIVERY')"
                            class="flex-1 bg-blue-600 text-white p-3 rounded-md hover:bg-blue-700">
                            Picked up order
                        </button>

                        <!-- Complete Delivery button - shows when status is OUT FOR DELIVERY -->
                        <button v-if="activeOrder.status === 'OUT FOR DELIVERY'" @click="updateOrderStatus('DELIVERED')"
                            class="flex-1 bg-green-600 text-white p-3 rounded-md hover:bg-green-700">
                            Complete Delivery
                        </button>

                        <!-- Cancel Delivery button - shows when status is READY FOR PICKUP or OUT FOR DELIVERY -->
                        <button v-if="['READY FOR PICKUP', 'OUT FOR DELIVERY'].includes(activeOrder.status)"
                            @click="cancelDelivery" class="flex-1 bg-red-600 text-white p-3 rounded-md hover:bg-red-700">
                            Cancel Delivery
                        </button>

                    </div>
                </div>
            </div>
        </div>
        
        <!-- Message when driver is Busy -->
        <div v-else class="bg-gray-50 p-6 rounded-lg shadow-md text-center mt-4">
            <vue-feather type="moon" size="48" class="mx-auto mb-4 text-gray-500" />
            <h2 class="text-2xl font-bold mb-2">You're Currently Offline</h2>
            <p class="text-gray-600">Toggle the switch above to become available for deliveries.</p>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch, onUnmounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'
import axios from 'axios'
import { db } from '@/config/firebase'
import { doc, getDoc } from "firebase/firestore"
import VueFeather from 'vue-feather'

const orders = ref([])
const activeOrder = ref(null)
const driverId = ref('')
const driverDetails = ref({
    DriverName: '',
    DriverStatus: '',
    DriverNumber: 0,
    DriverLocation: '',
    DriverEmail: ''
})
const restaurantDetails = ref(null)
const restaurantImage = ref('')
const customerInfo = ref(null)
const loading = ref(true)
const error = ref(null)

const auth = useAuthStore()
const { user } = storeToRefs(auth)

// const DRIVER_SERVICE_URL = 'https://personal-shkrtsry.outsystemscloud.com/DriverServiceModule/rest/NomNomGo'
// const ORDER_SERVICE_URL = 'http://localhost:5001'
// const CUSTOMER_SERVICE_URL = 'http://localhost:4000'
// const DELIVERY_FOOD_SERVICE_URL = 'http://localhost:5005'
// const REJECT_DELIVERY_SERVICE_URL = 'http://localhost:5008'  

const DRIVER_SERVICE_URL = 'http://localhost:8000'
const ORDER_SERVICE_URL = 'http://localhost:8000'
const CUSTOMER_SERVICE_URL = 'http://localhost:8000'
const DELIVERY_FOOD_SERVICE_URL = 'http://localhost:8000'
const REJECT_DELIVERY_SERVICE_URL = 'http://localhost:8000'

const fetchDriverInfo = async (email) => {
    try {
        loading.value = true
        const response = await axios.get(`${DRIVER_SERVICE_URL}/drivers/${email}/`)
        const driver = response.data["Driver"]  // Get the driver object

        driverId.value = driver.DriverId
        driverDetails.value = {
            DriverName: driver.DriverName,
            DriverStatus: driver.DriverStatus,
            DriverNumber: driver.DriverNumber,
            DriverLocation: driver.DriverLocation,
            DriverEmail: driver.DriverEmail
        }
        console.log(driverDetails)
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
        !['COMPLETED', 'DELIVERED', 'CANCELLED'].includes(order.status)
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

// Add a computed property to determine if driver is available
const isAvailable = computed({
    get: () => {
        return driverDetails.value.DriverStatus?.toLowerCase() === 'available'
    },
    set: (value) => {
        // This will be triggered by v-model
        driverDetails.value.DriverStatus = value ? 'Available' : 'Busy'
    }
})

// Replace the takeBreak function with toggleDriverStatus
const toggleDriverStatus = async () => {
    try {
        loading.value = true
        const status = isAvailable.value ? 'Available' : 'Busy'
        
        const driverResponse = await axios.put(
            `${DRIVER_SERVICE_URL}/drivers`,
            {
                "DriverId": driverId.value,
                "DriverStatus": status,
                "DriverName": driverDetails.value.DriverName,
                "DriverNumber": driverDetails.value.DriverNumber,
                "DriverLocation": driverDetails.value.DriverLocation,
                "DriverEmail": driverDetails.value.DriverEmail
            }
        )
        
        console.log('Driver status updated:', driverResponse.data)
        
        // Refresh orders if the driver becomes available
        if (isAvailable.value) {
            await fetchAllOrders()
        }
    } catch (err) {
        console.error('Error updating driver status:', err)
        error.value = `Failed to update availability: ${err.message}`
        
        // Revert the toggle if there was an error
        isAvailable.value = !isAvailable.value
    } finally {
        loading.value = false
    }
}

const updateOrderStatus = async (newStatus) => {
    if (!activeOrder.value) return

    try {
        loading.value = true
        error.value = null

        let driverStatusUpdate = 'ASSIGNED'
        if (newStatus === 'DELIVERED') {
            // driverStatusUpdate = 'AVAILABLE'
            try {
                const driverResponse = await axios.put(
                    `${DRIVER_SERVICE_URL}/drivers`,
                    {
                        "DriverId": driverId.value,
                        "DriverStatus": "Available",
                        "DriverName": driverDetails.value.DriverName,
                        "DriverNumber": driverDetails.value.DriverNumber,
                        "DriverLocation": driverDetails.value.DriverLocation,
                        "DriverEmail": driverDetails.value.DriverEmail
                    }
                )
                console.log('Driver status updated:', driverResponse.data)
            } catch (driverErr) {
                console.error('Error updating driver status:', driverErr)
                throw new Error('Failed to update driver availability')
            }
        }
        const response = await axios.put(
            `${ORDER_SERVICE_URL}/orders/${activeOrder.value.orderId}/status`,
            {
                status: newStatus,
                driverStatus: driverStatusUpdate
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
        case 'PREPARING':
            return 'bg-yellow-100 text-yellow-800'
        case 'READY FOR PICKUP':
        case 'OUT FOR DELIVERY':
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

const rejectDelivery = async () => {
    if (!activeOrder.value) return

    // might want to change from window alert (but only if have time)
    const confirmed = window.confirm( 
        'Are you sure you want to reject this delivery? This action cannot be undone.'
    )
    if (!confirmed) return

    try {
        loading.value = true
        error.value = null

        // Call the reject-delivery microservice
        const response = await axios.post(
            `${REJECT_DELIVERY_SERVICE_URL}/reject-delivery/${activeOrder.value.orderId}/${driverId.value}`
        )

        console.log('Reject delivery response:', response.data)

        if (response.data.code === 200) {
            window.alert('Delivery rejected successfully. Finding new driver.')

            await fetchAllOrders()
        } else {
            throw new Error(response.data.message || 'Failed to reject delivery')
        }

    } catch (err) {
        console.error('Error rejecting delivery:', err)
        error.value = `Failed to reject delivery: ${err.response?.data?.message || err.message}`
        window.alert(`Failed to reject delivery: ${err.response?.data?.message || err.message}`)
    } finally {
        loading.value = false
    }
}

const cancelDelivery = async () => {
    if (!activeOrder.value) return;

    const confirmed = window.confirm(
        'Are you sure you want to cancel this delivery? This action cannot be undone and the customer will be refunded.'
    );
    if (!confirmed) return;

    try {
        loading.value = true;
        error.value = null;

        console.log('Cancelling delivery for order:', activeOrder.value.orderId);

        // Call the delivery-food composite service
        const response = await axios.post(
            `${DELIVERY_FOOD_SERVICE_URL}/deliver-food/cancel/${activeOrder.value.orderId}`
        );

        console.log('Cancel delivery response:', response.data);

        if (response.data.code === 200) {
            // Show success message
            window.alert('Delivery cancelled successfully. Customer has been notified and refunded.');
            // Refresh order data
            await fetchAllOrders();
        } else {
            throw new Error(response.data.message || 'Failed to cancel delivery');
        }

    } catch (err) {
        console.error('Error cancelling delivery:', err);
        error.value = `Failed to cancel delivery: ${err.response?.data?.message || err.message}`;
        window.alert(`Failed to cancel delivery: ${err.response?.data?.message || err.message}`);
    } finally {
        loading.value = false;
    }
};


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
