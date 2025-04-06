import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'
import axios from 'axios'

const WALLET_URL = 'http://localhost:5002'
const PAY_DELIVERY_URL = 'http://localhost:5004'


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
    // This function is deprecated as we now only support Stripe payments
    console.warn("Direct wallet funding is deprecated. Please use createStripeCheckout instead.");
    return false;
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

  // Create a Stripe checkout session for top-up
  const createStripeCheckout = async (amount) => {
    if (!auth.user) {
      error.value = "User not authenticated"
      return { success: false, error: "User not authenticated" }
    }

    try {
      error.value = null
      const response = await axios.post(`${WALLET_URL}/wallet/${auth.user.uid}/create-stripe-checkout`, {
        amount: parseFloat(amount)
      })
      
      return {
        success: true,
        checkoutUrl: response.data.url,
        sessionId: response.data.id
      }
    } catch (err) {
      console.error("Error creating Stripe checkout:", err)
      error.value = err.response?.data?.error || "Failed to create checkout session"
      return {
        success: false,
        error: error.value
      }
    }
  }

  // Process a successful Stripe payment after redirect
  const processStripeSuccess = async (sessionId, customerId, amount) => {
    if (!auth.user) {
      error.value = "User not authenticated"
      return { success: false, error: "User not authenticated" }
    }

    try {
      error.value = null
      const response = await axios.post(`${WALLET_URL}/wallet/process-stripe-success`, {
        session_id: sessionId,
        customer_id: customerId,
        amount: parseFloat(amount)
      })
      
      if (response.data.success) {
        balance.value = response.data.balance
        lastTransaction.value = {
          type: 'credit',
          amount: parseFloat(amount),
          timestamp: new Date(),
          status: 'success',
          method: 'stripe'
        }
        return { 
          success: true,
          balance: response.data.balance
        }
      }
      
      throw new Error("Payment verification failed")
    } catch (err) {
      console.error("Error processing Stripe success:", err)
      error.value = err.response?.data?.error || "Failed to verify payment"
      lastTransaction.value = {
        type: 'credit',
        amount: parseFloat(amount),
        timestamp: new Date(),
        status: 'failed',
        method: 'stripe',
        error: error.value
      }
      return {
        success: false,
        error: error.value
      }
    }
  }

  return { 
    balance, 
    loading, 
    error, 
    initWallet, 
    addMoney, 
    processPayment,
    createStripeCheckout,
    processStripeSuccess,
    lastTransaction
  }
})