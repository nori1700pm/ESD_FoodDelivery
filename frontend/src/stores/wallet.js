import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'
import axios from 'axios'

const API_URL = 'http://localhost:3000' // or your deployed backend URL

export const useWalletStore = defineStore('wallet', () => {
  const balance = ref(0)
  const loading = ref(true)
  const error = ref(null)
  const auth = useAuthStore()

  const initWallet = async () => {
    if (!auth.user) {
      balance.value = 0
      loading.value = false
      return
    }

    try {
      loading.value = true
      const response = await axios.get(`${API_URL}/wallet/${auth.user.uid}`)
      balance.value = response.data.balance || 0
      error.value = null
    } catch (err) {
      console.error("Error initializing wallet:", err)
      error.value = "Failed to initialize wallet"
      balance.value = 0
    } finally {
      loading.value = false
    }
  }

  const addMoney = async (amount) => {
    if (!auth.user) {
      error.value = "User not authenticated"
      return false
    }

    try {
      error.value = null
      const response = await axios.put(`${API_URL}/wallet/${auth.user.uid}`, {
        balance: balance.value + amount
      })
      
      balance.value = response.data.balance || balance.value
      return true
    } catch (err) {
      console.error("Error adding money:", err)
      error.value = "Failed to add money to wallet"
      return false
    }
  }

  const processPayment = async (amount, orderId) => {
    if (!auth.user) {
      error.value = "User not authenticated"
      return false
    }

    if (balance.value < amount) {
      error.value = "Insufficient balance"
      return false
    }

    try {
      error.value = null
      const response = await axios.post(`${API_URL}/wallet/${auth.user.uid}/process-payment`, {
        amount: amount,
        orderId: orderId
      })
      
      balance.value = response.data.newBalance
      return true
    } catch (err) {
      console.error("Error processing payment:", err)
      error.value = err.response?.data?.error || "Failed to process payment"
      return false
    }
  }

  return { 
    balance, 
    loading, 
    error, 
    initWallet, 
    addMoney, 
    processPayment 
  }
})