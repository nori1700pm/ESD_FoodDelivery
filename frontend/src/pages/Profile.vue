<template>
  <div v-if="loading" class="flex justify-center items-center h-64">
    <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
  </div>

  <div v-else-if="error && !profile" class="text-center py-10">
    <p class="text-red-500 text-lg">{{ error }}</p>
    <button 
      @click="$router.go(0)"
      class="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
    >
      Try Again
    </button>
  </div>

  <div v-else class="max-w-2xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center">
        <vue-feather type="user" size="28" class="mr-2"></vue-feather>
        <h1 class="text-3xl font-bold">My Profile</h1>
      </div>
      <div class="flex items-center space-x-2">
        <button
          @click="handleRepairData"
          :disabled="repairing"
          class="flex items-center text-sm bg-green-50 text-green-700 px-2 py-1 rounded hover:bg-green-100"
        >
          <vue-feather type="refresh-cw" size="16" class="mr-1" :class="{ 'animate-spin': repairing }"></vue-feather>
          {{ repairing ? 'Repairing...' : 'Repair Data' }}
        </button>
        <button
          @click="handleDebugClick"
          class="flex items-center text-sm text-gray-500 hover:text-gray-700"
        >
          <vue-feather type="tool" size="16" class="mr-1"></vue-feather> Debug
        </button>
      </div>
    </div>
    
    <div v-if="debugInfo" class="bg-blue-50 p-4 rounded-lg mb-6 whitespace-pre-line">
      <h3 class="font-semibold mb-1">Debug Information:</h3>
      <p class="text-sm font-mono">{{ debugInfo }}</p>
    </div>
    
    <div v-if="error" class="bg-red-100 text-red-700 p-4 rounded-lg mb-6">
      {{ error }}
    </div>
    
    <div v-if="successMessage" class="bg-green-100 text-green-700 p-4 rounded-lg mb-6">
      {{ successMessage }}
    </div>
    
    <div class="bg-white rounded-lg shadow-lg p-6">
      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label for="name" class="block mb-1 text-gray-700">Full Name</label>
          <input
            id="name"
            v-model="profile.name"
            type="text"
            class="w-full p-3 border border-gray-300 rounded-md"
          />
        </div>
        
        <div>
          <label for="email" class="block mb-1 text-gray-700">Email</label>
          <input
            id="email"
            v-model="profile.email"
            type="email"
            disabled
            class="w-full p-3 border border-gray-300 rounded-md bg-gray-50"
          />
          <p class="text-xs text-gray-500 mt-1">Email cannot be changed</p>
        </div>
        
        <div>
          <label for="phone" class="block mb-1 text-gray-700">Phone Number</label>
          <input
            id="phone"
            v-model="profile.phone"
            type="tel"
            class="w-full p-3 border border-gray-300 rounded-md"
          />
        </div>
        
        <div>
          <label for="address" class="block mb-1 text-gray-700">Delivery Address</label>
          <textarea
            id="address"
            v-model="profile.address"
            class="w-full p-3 border border-gray-300 rounded-md"
            rows="3"
          ></textarea>
        </div>
        
        <button
          type="submit"
          :disabled="saving"
          class="flex items-center justify-center w-full py-2 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 disabled:bg-gray-400"
        >
          <template v-if="saving">
            <vue-feather type="loader" size="18" class="mr-2 animate-spin"></vue-feather> Saving...
          </template>
          <template v-else>
            <vue-feather type="save" size="18" class="mr-2"></vue-feather> Save Changes
          </template>
        </button>
      </form>
    </div>
    
    <div v-if="user" class="mt-4 text-xs text-gray-400">
      User ID: {{ user.uid }}
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { doc, getDoc, updateDoc, serverTimestamp } from 'firebase/firestore'
import { db } from '../config/firebase'
import VueFeather from 'vue-feather'
import { storeToRefs } from 'pinia'
import { checkUserWallet, createUserWalletIfNotExists, checkUserProfile, repairUserData } from '../utils/userUtils'

const auth = useAuthStore()
const { user } = storeToRefs(auth)

const profile = ref(null)
const loading = ref(true)
const saving = ref(false)
const repairing = ref(false)
const error = ref(null)
const successMessage = ref(null)
const debugInfo = ref(null)

onMounted(async () => {
  await fetchUserProfile()
})

const fetchUserProfile = async () => {
  if (!user.value) return
  
  try {
    loading.value = true
    const userDoc = await getDoc(doc(db, 'users', user.value.uid))
    
    if (userDoc.exists()) {
      const userData = userDoc.data()
      profile.value = {
        name: userData.name || '',
        email: userData.email || user.value.email || '',
        phone: userData.phone || '',
        address: userData.address || '',
      }
    } else {
      // Initialize with empty profile if not found
      profile.value = {
        name: user.value.displayName || '',
        email: user.value.email || '',
        phone: '',
        address: '',
      }
    }
  } catch (err) {
    console.error("Error fetching user profile:", err)
    error.value = "Failed to load your profile. Please try repairing your data."
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  if (!user.value || !profile.value) return
  
  try {
    saving.value = true
    error.value = null
    
    const userRef = doc(db, 'users', user.value.uid)
    
    await updateDoc(userRef, {
      name: profile.value.name,
      phone: profile.value.phone,
      address: profile.value.address,
      updatedAt: serverTimestamp()
    })
    
    successMessage.value = "Profile updated successfully"
    setTimeout(() => successMessage.value = null, 3000)
  } catch (err) {
    console.error("Error updating profile:", err)
    error.value = "Failed to update profile"
  } finally {
    saving.value = false
  }
}

const handleDebugClick = async () => {
  if (!user.value) return

  try {
    debugInfo.value = "Running diagnostics..."
    
    // Check user profile
    const profileData = await checkUserProfile(user.value.uid)
    
    // Check wallet
    const walletData = await checkUserWallet(user.value.uid)
    
    // Create wallet if it doesn't exist
    if (!walletData) {
      await createUserWalletIfNotExists(user.value.uid, 100)
      const newWalletData = await checkUserWallet(user.value.uid)
      
      debugInfo.value = `
        Profile: ${profileData ? 'Found' : 'Not found'}
        Wallet: Initially not found, created with $100
        New wallet balance: $${newWalletData?.balance || 0}
      `
    } else {
      debugInfo.value = `
        Profile: ${profileData ? 'Found' : 'Not found'}
        Wallet: Found with balance $${walletData.balance}
      `
    }
    
    // Wait 5 seconds then clear debug info
    setTimeout(() => debugInfo.value = null, 5000)
    
  } catch (error) {
    console.error("Debug error:", error)
    debugInfo.value = "Error during diagnostics. See console for details."
  }
}

const handleRepairData = async () => {
  if (!user.value) return
  
  try {
    repairing.value = true
    error.value = null
    
    const result = await repairUserData(user.value.uid)
    
    if (result.success) {
      successMessage.value = "User data has been repaired successfully."
      
      // Refresh profile data
      const userDoc = await getDoc(doc(db, 'users', user.value.uid))
      if (userDoc.exists()) {
        const userData = userDoc.data()
        profile.value = {
          name: userData.name || profile.value?.name || '',
          email: userData.email || user.value.email || '',
          phone: userData.phone || profile.value?.phone || '',
          address: userData.address || profile.value?.address || '',
        }
      }
    } else {
      error.value = `Failed to repair user data: ${result.message}`
    }
    
    setTimeout(() => successMessage.value = null, 3000)
  } catch (err) {
    console.error("Error repairing user data:", err)
    error.value = "Failed to repair user data"
  } finally {
    repairing.value = false
  }
}
</script>
