<template>
  <div class="max-w-md mx-auto mt-8">
    <h1 class="text-2xl font-bold mb-6 text-center">Create an Account</h1>
    
    <div v-if="error" class="bg-red-100 text-red-700 p-3 rounded-lg mb-4">
      {{ error }}
    </div>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
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
      
      <div>
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
import { useAuthStore } from '../stores/auth'
import { doc, setDoc, serverTimestamp } from 'firebase/firestore'
import { db } from '../config/firebase'

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const name = ref('')
const phone = ref('')
const address = ref('')
const loading = ref(false)
const error = ref(null)

const handleSubmit = async () => {
  if (!email.value || !password.value || !name.value || !phone.value || !address.value) {
    error.value = 'Please fill in all fields'
    return
  }

  try {
    loading.value = true
    error.value = null
    
    // Register the user
    const userCredential = await auth.register(email.value, password.value)
    const userId = userCredential.user.uid
    
    // Create all required collections for this user in a batch
    const timestamp = serverTimestamp()
    const batch = [
      // User profile
      setDoc(doc(db, 'users', userId), {
        uid: userId,
        email: email.value,
        name: name.value,
        phone: phone.value,
        address: address.value,
        createdAt: timestamp,
        updatedAt: timestamp
      }),
      
      // Wallet with initial balance of 100
      setDoc(doc(db, 'wallets', userId), {
        balance: 100,
        createdAt: timestamp,
        updatedAt: timestamp
      }),
      
      // Empty cart
      setDoc(doc(db, 'carts', userId), {
        items: [],
        createdAt: timestamp,
        updatedAt: timestamp
      })
    ]
    
    // Execute all promises
    await Promise.all(batch)
    
    console.log("User registration complete with all collections initialized")
    router.push('/')
  } catch (err) {
    console.error('Registration failed:', err)
    error.value = err.message || 'Failed to register. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>
