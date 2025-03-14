<template>
  <div v-if="items.length === 0" class="text-center py-16">
    <vue-feather type="shopping-bag" size="64" class="mx-auto text-gray-400 mb-4"></vue-feather>
    <h2 class="text-2xl font-bold mb-2">Your cart is empty</h2>
    <p class="text-gray-600 mb-6">Add items from a restaurant to get started</p>
    <router-link to="/restaurants" class="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold">
      Browse Restaurants
    </router-link>
  </div>

  <div v-else class="max-w-3xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Your Cart</h1>
    
    <div v-if="restaurantInfo" class="mb-6">
      <p class="text-lg">
        From <router-link :to="`/restaurants/${restaurantInfo.id}`" class="text-blue-600 font-medium">{{ restaurantInfo.name }}</router-link>
      </p>
    </div>
    
    <div class="bg-white rounded-lg shadow-lg mb-6">
      <div v-for="item in items" :key="item.id" class="flex items-center justify-between p-4 border-b last:border-0">
        <div class="flex-1">
          <h3 class="font-medium">{{ item.name }}</h3>
          <p class="text-gray-600">${{ item.price.toFixed(2) }}</p>
        </div>
        
        <div class="flex items-center">
          <button 
            @click="cart.removeItem(item.id)"
            class="p-1 rounded-full hover:bg-gray-100"
          >
            <vue-feather type="minus" size="18"></vue-feather>
          </button>
          
          <span class="mx-3 font-medium">{{ item.quantity }}</span>
          
          <button 
            @click="cart.addItem({
              id: item.id,
              name: item.name,
              price: item.price,
              restaurantId: item.restaurantId
            })"
            class="p-1 rounded-full hover:bg-gray-100"
          >
            <vue-feather type="plus" size="18"></vue-feather>
          </button>
          
          <button 
            @click="removeItemCompletely(item.id, item.quantity)"
            class="ml-4 p-1 rounded-full hover:bg-gray-100 text-red-500"
          >
            <vue-feather type="trash-2" size="18"></vue-feather>
          </button>
        </div>
      </div>
    </div>
    
    <div class="bg-white rounded-lg shadow-lg p-6 mb-6">
      <div class="flex justify-between mb-2">
        <span>Subtotal</span>
        <span>${{ total.toFixed(2) }}</span>
      </div>
      <div class="flex justify-between mb-2">
        <span>Delivery Fee</span>
        <span>$2.99</span>
      </div>
      <div class="flex justify-between font-bold text-lg pt-2 border-t mt-2">
        <span>Total</span>
        <span>${{ (total + 2.99).toFixed(2) }}</span>
      </div>
    </div>
    
    <div class="flex space-x-4">
      <button
        @click="cart.clearCart"
        class="flex-1 py-3 text-center border border-gray-300 rounded-lg hover:bg-gray-100"
      >
        Clear Cart
      </button>
      
      <button
        @click="handleCheckout"
        class="flex-1 bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700"
      >
        Proceed to Checkout
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watchEffect, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCartStore } from '../stores/cart'
import { doc, getDoc } from 'firebase/firestore'
import { db } from '../config/firebase'
import VueFeather from 'vue-feather'
import { storeToRefs } from 'pinia'

const router = useRouter()
const cart = useCartStore()
const { items, total } = storeToRefs(cart)
const restaurantInfo = ref(null)

const handleCheckout = () => {
  router.push('/checkout')
}

const removeItemCompletely = (itemId, quantity) => {
  for (let i = 0; i < quantity; i++) {
    cart.removeItem(itemId)
  }
}

// Fetch restaurant information when items change
watchEffect(async () => {
  if (items.value.length > 0) {
    // Assuming all items are from the same restaurant
    const restaurantId = items.value[0].restaurantId
    
    try {
      const restaurantDoc = await getDoc(doc(db, 'restaurants', restaurantId))
      
      if (restaurantDoc.exists()) {
        restaurantInfo.value = {
          id: restaurantDoc.id,
          name: restaurantDoc.data().name
        }
      }
    } catch (error) {
      console.error("Error fetching restaurant info:", error)
    }
  } else {
    restaurantInfo.value = null
  }
})

onMounted(() => {
  cart.initCart()
})
</script>
