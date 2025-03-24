<template>
    <h1 v-if="restaurantImage" class="text-3xl font-bold mb-6">Active Order</h1>
    <h1 v-else class="text-3xl font-bold mb-6">You have no active orders!</h1>
    <p>{{ destination }}</p>
    <p>{{ restaurantName }}</p>
    <img v-if="restaurantImage" :src="restaurantImage" alt="Restaurant Image">
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'
import axios from 'axios'
import { db } from '@/config/firebase'

const orders = ref([])
const driverId = ref('')
const destination = ref('')
const restaurantId = ref('')
const restaurantName = ref('')
const restaurantDetails = ref([])
const restaurantImage = ref('')
const loading = ref(false)
const error = ref(null)
// const restaurantAddress = ref('')
// const restaurantImage = ref('')



const auth = useAuthStore()
const { user } = storeToRefs(auth)
const GETDRIVERBYEMAIL_SERVICE_URL = 'https://personal-shkrtsry.outsystemscloud.com/DriverServiceModule/rest/NomNomGo/drivers/'

// Watch for changes to `user` and make the API call once the user is populated
watch(user, (newUser) => {
    if (newUser && newUser.email) {
        console.log('User email:', newUser.email)
        fetchDriverInfo(newUser.email) // Pass the email to fetch orders
    }
}, { immediate: true })

const fetchDriverInfo = async (email) => {
    try {
        const response = await axios.get(`${GETDRIVERBYEMAIL_SERVICE_URL}${email}/`)
        driverId.value = response.data["Driver"]["DriverId"]
        fetchAllOrders()
    } catch (error) {
        console.error('Error fetching driver data', error.message)
    }
}

const fetchAllOrders = async () => {
    try {
        const response = await axios.get('http://localhost:5001/orders')
        orders.value = response.data
        fetchActiveOrder()
    } catch (error) {
        console.error('Error fetching orders', error.message)
    }
}

const fetchActiveOrder = async () => {
    try {
        for (let index = 0; index < orders.value.length; index++) {
            const element = orders.value[index];
            if (orders.value[index].driverId == driverId.value && orders.value[index].status == "PENDING") {
                destination.value = orders.value[index].deliveryAddress
                restaurantId.value = orders.value[index].restaurantId
                restaurantName.value = orders.value[index].restaurantName
                fetchRestaurantById(restaurantId.value)
            }

        }
    } catch (error) {
        console.error('Error fetching orders', error.message)
    }
}

import { doc, getDoc } from "firebase/firestore"

const fetchRestaurantById = async (restaurantId) => {
    try {
        loading.value = true
        error.value = null

        const docRef = doc(db, 'restaurants', restaurantId)
        const docSnap = await getDoc(docRef)

        if (!docSnap.exists()) {
            error.value = "Restaurant not found. Please check the ID and try again."
            return
        }

        restaurantDetails.value = { id: docSnap.id, ...docSnap.data() }
        restaurantImage.value = restaurantDetails.value.imageUrl 

    } catch (err) {
        console.error("Error fetching restaurant:", err)
        error.value = "Failed to load restaurant. Please try again later."
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    // Ensure the fetchAllOrders function is called once the user is set
    if (user.value && user.value.email) {
        fetchDriverInfo(user.value.email)
    }
})
</script>
