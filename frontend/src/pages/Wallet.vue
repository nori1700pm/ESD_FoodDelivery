<template>
  <div class="max-w-2xl mx-auto">
    <div class="flex items-center mb-6">
      <vue-feather type="credit-card" size="28" class="mr-2"></vue-feather>
      <h1 class="text-3xl font-bold">My Wallet</h1>
    </div>
    
    <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
      <p class="text-gray-600 mb-1">Current Balance</p>
      <template v-if="loading">
        <div class="animate-pulse h-10 w-32 bg-gray-200 rounded"></div>
      </template>
      <template v-else>
        <h2 class="text-4xl font-bold text-blue-600">${{ (balance ?? 0).toFixed(2) }}</h2>
      </template>
    </div>
    
    <div class="bg-white rounded-lg shadow-lg p-6">
      <h3 class="text-xl font-bold mb-4 flex items-center">
        <vue-feather type="dollar-sign" size="20" class="mr-1"></vue-feather> Add Money
      </h3>
      
      <div v-if="error" class="mb-4 p-3 bg-red-100 text-red-700 rounded-lg">
        {{ error }}
      </div>
      
      <div v-if="success" class="mb-4 p-3 bg-green-100 text-green-700 rounded-lg">
        {{ success }}
      </div>
      
      <form @submit.prevent="handleAddMoney" class="space-y-4">
        <div>
          <label for="amount" class="block mb-1 text-gray-700">Amount</label>
          <div class="relative mt-1">
            <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
              <span class="text-gray-500">$</span>
            </div>
            <input
              id="amount"
              type="number"
              min="0.01"
              step="0.01"
              v-model="amount"
              placeholder="0.00"
              class="block w-full pl-8 pr-12 py-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            />
          </div>
        </div>
        
        <div class="space-y-2">
          <button
            type="button"
            @click="amount = '10.00'"
            class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            $10
          </button>
          <button
            type="button"
            @click="amount = '20.00'"
            class="ml-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            $20
          </button>
          <button
            type="button"
            @click="amount = '50.00'"
            class="ml-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            $50
          </button>
          <button
            type="button"
            @click="amount = '100.00'"
            class="ml-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            $100
          </button>
        </div>
        
        <button
          type="submit"
          :disabled="isAdding || loading"
          class="w-full py-3 bg-blue-600 text-white rounded-md font-medium hover:bg-blue-700 disabled:bg-gray-400"
        >
          {{ isAdding ? 'Adding...' : 'Add Money' }}
        </button>
      </form>
    </div>
    
    <div v-if="user" class="mt-4 text-sm text-gray-500">
      User ID: {{ user.uid }}
    </div>
  </div>
  <div v-if="lastTransaction" 
       :class="[
         'mt-4 p-4 rounded-lg',
         lastTransaction.status === 'success' 
           ? 'bg-green-100 text-green-700' 
           : 'bg-red-100 text-red-700'
       ]">
    <h4 class="font-bold">Last Transaction</h4>
    <p>Type: {{ lastTransaction.type === 'credit' ? 'Add Money' : 'Payment' }}</p>
    <p>Amount: ${{ lastTransaction.amount.toFixed(2) }}</p>
    <p>Status: {{ lastTransaction.status }}</p>
    <p v-if="lastTransaction.error">Error: {{ lastTransaction.error }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useWalletStore } from '../stores/wallet'
import { useAuthStore } from '../stores/auth'
import VueFeather from 'vue-feather'
import { storeToRefs } from 'pinia'
import { watch } from 'vue'

const wallet = useWalletStore()
const auth = useAuthStore()
const { user } = storeToRefs(auth)
const { balance, loading } = storeToRefs(wallet)

// Initialize balance with a default value
balance.value = balance.value ?? 0

const amount = ref('')
const isAdding = ref(false)
const error = ref('')
const success = ref('')

watch(() => user.value, (newUser) => {
  if (newUser) {
    wallet.initWallet()
  } else {
    balance.value = 0
  }
}, { immediate: true })

onMounted(() => {
  wallet.initWallet()
})

const handleAddMoney = async () => {
  if (!amount.value || isNaN(Number(amount.value)) || Number(amount.value) <= 0) {
    error.value = 'Please enter a valid amount'
    return
  }
  
  try {
    isAdding.value = true
    error.value = ''
    
    const amountNumber = Number(amount.value)
    console.log("Adding money:", amountNumber)
    const result = await wallet.addMoney(amountNumber)
    
    if (result) {
      success.value = `Successfully added $${amountNumber.toFixed(2)} to your wallet`
      amount.value = ''
      await wallet.initWallet() // Refresh the balance
    } else {
      error.value = 'Failed to add money to your wallet'
    }
  } catch (err) {
    error.value = 'An error occurred while adding money'
    console.error(err)
  } finally {
    isAdding.value = false
    // Clear success message after 5 seconds
    if (success.value) {
      setTimeout(() => {
        success.value = ''
      }, 5000)
    }
  }
}
</script>