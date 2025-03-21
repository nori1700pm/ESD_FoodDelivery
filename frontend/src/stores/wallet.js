import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'
import axios from 'axios'

const WALLET_URL = 'http://localhost:3000'
const PAY_DELIVERY_URL = 'http://localhost:5003'


export const useWalletStore = defineStore('wallet', () => {
  const balance = ref(0)
  const loading = ref(true)
  const error = ref(null)
  const lastTransaction = ref(null)
  const auth = useAuthStore()

  const initWallet = async () => {
    if (!auth.user) {
      balance.value = 0
      loading.value = false
      return
    }

    try {
      loading.value = true
      const response = await axios.get(`${WALLET_URL}/wallet/${auth.user.uid}`)
      balance.value = response.data.balance
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
      const response = await axios.put(`${WALLET_URL}/wallet/${auth.user.uid}`, {
        balance: balance.value + amount
      })
      
      balance.value = response.data.balance
      lastTransaction.value = {
        type: 'credit',
        amount,
        timestamp: new Date(),
        status: 'success'
      }
      return true
    } catch (err) {
      console.error("Error adding money:", err)
      error.value = "Failed to add money to wallet"
      lastTransaction.value = {
        type: 'credit',
        amount,
        timestamp: new Date(),
        status: 'failed',
        error: err.response?.data?.error
      }
      return false
    }
  }

  const processPayment = async (amount, orderId) => {
    if (!auth.user) {
      error.value = "User not authenticated"
      return { success: false, error: "User not authenticated" }
    }

    try {
      error.value = null
      // Call pay-for-delivery service instead of wallet directly
      const response = await axios.post(`${PAY_DELIVERY_URL}/pay-delivery`, {
        custId: auth.user.uid,
        orderId: orderId,
        amount: amount
      })
      
      // Handle successful response
      if (response.data.code === 200) {
        balance.value = response.data.data.wallet_result.newBalance
        return {
          success: true,
          data: response.data
        }
      } else {
        throw new Error(response.data.message)
      }
    } catch (err) {
      console.error("Payment processing error:", err)
      error.value = err.response?.data?.message || "Failed to process payment"
      return {
        success: false,
        error: error.value,
        data: err.response?.data
      }
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