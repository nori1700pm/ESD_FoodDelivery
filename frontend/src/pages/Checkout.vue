<template>
  <div v-if="success" class="max-w-md mx-auto text-center py-16">
    <div class="bg-green-100 rounded-full w-24 h-24 mx-auto flex items-center justify-center mb-6">
      <vue-feather type="check" size="40" class="text-green-600" />
    </div>
    <h2 class="text-2xl font-bold mb-2">Order Placed Successfully!</h2>
    <p class="text-gray-600 mb-6">
      Your order has been placed and is being processed.
    </p>
    <p class="text-gray-600">
      You'll be redirected to your orders page in a few seconds...
    </p>
  </div>

  <div v-else class="max-w-3xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Checkout</h1>
    
    <div v-if="error" class="bg-red-100 text-red-700 p-4 rounded-lg mb-6">
      {{ error }}
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div>
        <div class="bg-white p-6 rounded-lg shadow-lg mb-6">
          <h2 class="text-xl font-semibold mb-4 flex items-center">
            <vue-feather type="map-pin" class="mr-2" /> Delivery Address
          </h2>
          <form>
            <textarea 
              v-model="address"
              class="w-full p-3 border border-gray-300 rounded-md"
              rows="3"
              placeholder="Enter your delivery address"
            ></textarea>
          </form>
        </div>
        
        <div class="bg-white p-6 rounded-lg shadow-lg">
          <h2 class="text-xl font-semibold mb-4 flex items-center">
            <vue-feather type="credit-card" class="mr-2" /> Payment Method
          </h2>
          <div>
            <label class="flex items-center mb-4">
              <input 
                type="radio" 
                name="payment" 
                value="wallet"
                v-model="paymentMethod"
                class="mr-2"
              />
              <span>Wallet (Balance: ${{ balance.toFixed(2) }})</span>
            </label>
            
            <label class="flex items-center">
              <input 
                type="radio" 
                name="payment" 
                value="cod"
                v-model="paymentMethod"
                class="mr-2"
              />
              <span>Cash on Delivery</span>
            </label>
          </div>
        </div>
      </div>
      
      <div class="bg-white p-6 rounded-lg shadow-lg h-fit">
        <h2 class="text-xl font-semibold mb-4">Order Summary</h2>
        
        <div class="space-y-4 mb-4">
          <div v-for="item in items" :key="item.id" class="flex justify-between">
            <span>{{ item.quantity }} × {{ item.name }}</span>
            <span>${{ (item.price * item.quantity).toFixed(2) }}</span>
          </div>
        </div>
        
        <div class="border-t pt-4 mb-4">
          <div class="flex justify-between mb-2">
            <span>Subtotal</span>
            <span>${{ total.toFixed(2) }}</span>
          </div>
          <div class="flex justify-between mb-2">
            <span>Delivery Fee</span>
            <span>${{ deliveryFee.toFixed(2) }}</span>
          </div>
          <div class="flex justify-between font-bold text-lg">
            <span>Total</span>
            <span>${{ totalWithDelivery.toFixed(2) }}</span>
          </div>
        </div>
        
        <button
          @click="handleSubmit"
          :disabled="loading"
          class="w-full bg-blue-600 text-white p-3 rounded-md hover:bg-blue-700 disabled:bg-blue-300"
        >
          {{ loading ? 'Processing...' : 'Place Order' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watchEffect } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'
import { useWalletStore } from '../stores/wallet'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'
import VueFeather from 'vue-feather'
import { doc, getDoc, collection, addDoc, serverTimestamp, updateDoc } from 'firebase/firestore'
import { db } from '../config/firebase'

const router = useRouter()
const cart = useCartStore()
const wallet = useWalletStore()
const auth = useAuthStore()

// Initialize stores
onMounted(() => {
  cart.initCart()
  wallet.initWallet()
})

const { items, total } = storeToRefs(cart)
const { balance } = storeToRefs(wallet)
const { user } = storeToRefs(auth)

const address = ref('')
const paymentMethod = ref('wallet')
const loading = ref(false)
const error = ref(null)
const success = ref(false)
const userProfile = ref(null)
const deliveryFee = ref(2.99)
const totalWithDelivery = computed(() => total.value + deliveryFee.value)

watchEffect(() => {
  if (items.value.length === 0 && !success.value) {
    router.push('/cart')
  }
})

// Fetch user profile
onMounted(async () => {
  if (!user.value) return
  
  try {
    const userDoc = await getDoc(doc(db, 'users', user.value.uid))
    
    if (userDoc.exists()) {
      userProfile.value = userDoc.data()
      address.value = userDoc.data().address || ''
    }
  } catch (err) {
    console.error('Error fetching user profile:', err)
  }
})

const handleSubmit = async () => {
  if (!address.value) {
    error.value = 'Please provide a delivery address'
    return
  }
  
  if (items.value.length === 0) {
    error.value = 'Your cart is empty'
    return
  }
  
  if (paymentMethod.value === 'wallet' && balance.value < totalWithDelivery.value) {
    error.value = 'Insufficient balance in your wallet'
    return
  }
  
  try {
    loading.value = true
    error.value = null
    
    // First, get restaurant info
    if (items.value.length > 0 && user.value) {
      const restaurantId = items.value[0].restaurantId
      const restaurantDoc = await getDoc(doc(db, 'restaurants', restaurantId))
      
      if (!restaurantDoc.exists()) {
        throw new Error('Restaurant not found')
      }
      
      const restaurantData = restaurantDoc.data()
      
      // Process payment if using wallet
      let paymentSuccess = true
      
      if (paymentMethod.value === 'wallet') {
        // Process the payment
        console.log('Processing wallet payment for amount:', totalWithDelivery.value)
        paymentSuccess = await wallet.processPayment(totalWithDelivery.value)
        
        if (!paymentSuccess) {
          throw new Error('Payment processing failed. Please check your wallet balance.')
        }
        console.log('Wallet payment successful')
      }
      
      // Create order in Firestore with customerId included
      console.log('Creating order in Firestore')
      const orderData = {
        customerId: user.value.uid,
        items: items.value,
        restaurantId: restaurantId,
        restaurantName: restaurantData.name,
        deliveryAddress: address.value,
        price: totalWithDelivery.value,
        status: 'PENDING',
        paymentMethod: paymentMethod.value,
        paymentStatus: paymentMethod.value === 'wallet' ? 'PAID' : 'PENDING',
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp()
      }
      
      // Create the order in Firestore
      const orderRef = await addDoc(collection(db, 'orders'), orderData)
      const orderId = orderRef.id
      console.log('Order created with ID:', orderId)
      
      // Call the delivery-food service to orchestrate the delivery
      try {
        const deliveryServiceUrl = import.meta.env.VITE_DELIVERY_SERVICE_URL || 'http://localhost:3000'
        console.log('Calling delivery service at:', deliveryServiceUrl)
        
        const response = await fetch(`${deliveryServiceUrl}/place-order`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            ...orderData,
            id: orderId,
          }),
        })
        
        let responseData
        if (!response.ok) {
          responseData = await response.json()
          console.error('Delivery service error:', responseData)
          
          // Update order status to indicate an issue
          await updateDoc(doc(db, 'orders', orderId), {
            status: 'DELIVERY_SERVICE_ERROR',
            serviceError: responseData.error || 'Unknown error',
            updatedAt: serverTimestamp()
          })
        } else {
          responseData = await response.json()
          console.log('Delivery service response:', responseData)
          
          // Update order with driver information if assigned
          if (responseData.status === 'ASSIGNED' && responseData.driver) {
            await updateDoc(doc(db, 'orders', orderId), {
              status: 'ASSIGNED',
              driverId: responseData.driver.id,
              driverName: responseData.driver.name,
              updatedAt: serverTimestamp()
            })
          }
        }
      } catch (err) {
        console.error('Error calling delivery service:', err)
        
        // Don't fail the checkout if the delivery service fails
        // Just update the order status
        await updateDoc(doc(db, 'orders', orderId), {
          status: 'PENDING_DRIVER_ASSIGNMENT',
          serviceCallError: true,
          updatedAt: serverTimestamp()
        })
      }
      
      // Clear the cart
      await cart.clearCart()
      
      // Show success message
      success.value = true
      
      // Redirect to orders page after a delay
      setTimeout(() => {
        router.push('/orders')
      }, 3000)
    }
  } catch (err) {
    console.error('Checkout error:', err)
    error.value = err.message || 'An error occurred during checkout'
  } finally {
    loading.value = false
  }
}
</script>
