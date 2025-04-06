<template>
  <div class="max-w-md mx-auto mt-8">
    <h1 class="text-2xl font-bold mb-6 text-center">Create an Account</h1>
    
    <div v-if="error" class="bg-red-100 text-red-700 p-3 rounded-lg mb-4">
      {{ error }}
    </div>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <div>
        <label for="userType" class="block mb-1 text-gray-700">Register as</label>
        <select
          id="userType"
          v-model="userType"
          class="w-full p-3 border border-gray-300 rounded-md"
        >
          <option value="customer">Customer</option>
          <option value="driver">Driver</option>
        </select>
      </div>

      <div>
        <label for="name" class="block mb-1 text-gray-700">Full Name</label>
        <input
          id="name"
          type="text"
          v-model="name"
          class="w-full p-3 border border-gray-300 rounded-md"
        />
      </div>
      
      <div>
        <label for="email" class="block mb-1 text-gray-700">Email</label>
        <input
          id="email"
          type="email"
          v-model="email"
          class="w-full p-3 border border-gray-300 rounded-md"
        />
      </div>
      
      <div>
        <label for="password" class="block mb-1 text-gray-700">Password</label>
        <input
          id="password"
          type="password"
          v-model="password"
          class="w-full p-3 border border-gray-300 rounded-md"
        />
      </div>
      
      <div>
        <label for="phone" class="block mb-1 text-gray-700">Phone Number</label>
        <input
          id="phone"
          type="tel"
          v-model="phone"
          class="w-full p-3 border border-gray-300 rounded-md"
        />
      </div>
      
      <div v-if="userType === 'customer'">
        <label for="address" class="block mb-1 text-gray-700">Delivery Address</label>
        <textarea
          id="address"
          v-model="address"
          class="w-full p-3 border border-gray-300 rounded-md"
          rows="3"
        ></textarea>
      </div>
      
      <button
        type="submit"
        :disabled="loading"
        class="w-full bg-blue-600 text-white p-3 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
      >
        {{ loading ? 'Creating account...' : 'Register' }}
      </button>
    </form>
    
    <p class="mt-4 text-center text-gray-600">
      Already have an account?
      <router-link to="/login" class="text-blue-600 hover:underline">
        Login
      </router-link>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { getAuth, createUserWithEmailAndPassword } from 'firebase/auth'

const router = useRouter()

const email = ref('')
const password = ref('')
const name = ref('')
const phone = ref('')
const address = ref('')
const driverLocation = ref('Somewhere') // Default driver location
const userType = ref('customer') // Default to 'customer'
const driverStatus = ref('Busy') // Default driver status
const error = ref(null)
const loading = ref(false)

const handleSubmit = async () => {
  if (!email.value || !password.value || !name.value || !phone.value || 
      (userType.value === 'customer' && !address.value)) {
    error.value = 'Please fill in all fields'
    return
  }

  // Email domain validation
  const emailDomain = email.value.split('@')[1];
  if (userType.value === 'driver' && emailDomain !== 'driver.com') {
    error.value = 'Drivers must use an email with the domain @driver.com';
    return;
  }
  if (userType.value === 'customer' && emailDomain === 'driver.com') {
    error.value = 'Customers cannot use an email with the domain @driver.com';
    return;
  }

  try {
    loading.value = true
    error.value = null

    const auth = getAuth()

    if (userType.value === 'customer') {

      const response = await axios.post('http://localhost:8000/customers', {
        name: name.value,
        email: email.value,
        phone: phone.value,
        password: password.value,
        address: address.value
      })
      console.log("Customer registration complete:", response.data)
      router.push('/')
    } else if (userType.value === 'driver') {
      // Create Firebase Auth record for driver
      await createUserWithEmailAndPassword(auth, email.value, password.value)

      try {
        // Call the OutSystems API for driver registration with correct field names
        const response = await axios.post('http://localhost:8000/createDriver', {
          DriverName: name.value, 
          DriverStatus: driverStatus.value, 
          DriverNumber: phone.value, 
          DriverLocation: driverLocation.value, 
          DriverEmail: email.value 
        })
        console.log("Driver registration complete in OutSystems:", response.data)
      } catch (outsystemsError) {
        console.error("OutSystems API error:", outsystemsError.response?.data || outsystemsError.message)
        error.value = "Failed to save driver in OutSystems. Please contact support."
        return
      }

      router.push('/activeorder') // Redirect drivers to activeorder.vue
    }
  } catch (err) {
    console.error('Registration failed:', err)
    error.value = err.response?.data?.message || 'Failed to register. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>