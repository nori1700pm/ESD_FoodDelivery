import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAuthStore } from './auth'
import { doc, getDoc, updateDoc, setDoc, serverTimestamp } from 'firebase/firestore'
import { db } from '../config/firebase'

// Add this helper function at the top of your store
const cleanObject = (obj) => {
  const cleaned = {}
  Object.entries(obj).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      if (typeof value === 'object' && !Array.isArray(value)) {
        cleaned[key] = cleanObject(value)
      } else {
        cleaned[key] = value
      }
    }
  })
  return cleaned
}

// Then modify your initCart function to ensure clean data:
const initCart = async () => {


  try {
    const cartRef = doc(db, 'carts', auth.user.uid)
    const cartDoc = await getDoc(cartRef)

    if (cartDoc.exists()) {
      const data = cartDoc.data()
      items.value = (data.items || []).map(item => cleanObject({
        id: item.id,
        name: item.name || 'Unknown Item',
        price: item.price || 0,
        quantity: item.quantity || 1,
        restaurantId: item.restaurantId || 'unknown',
        restaurantName: item.restaurantName || 'Restaurant',
        restaurant: {
          id: item.restaurantId || 'unknown',
          name: item.restaurantName || 'Restaurant'
        }
      }))
    } else {
      await setDoc(cartRef, {
        items: [],
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp()
      })
      items.value = []
    }
    loading.value = false
    error.value = null
  } catch (err) {
    console.error("Error fetching cart:", err)
    error.value = "Failed to load your cart"
    loading.value = false
  }
}

export const useCartStore = defineStore('cart', () => {
  const items = ref([])
  const loading = ref(true)
  const error = ref(null)
  const auth = useAuthStore()

  const total = computed(() =>
    items.value.reduce((sum, item) => sum + item.price * item.quantity, 0)
  )

  const initCart = async () => {
    if (!auth.user) {
      items.value = []
      loading.value = false
      return
    }

    try {
      const cartRef = doc(db, 'carts', auth.user.uid)
      const cartDoc = await getDoc(cartRef)

      if (cartDoc.exists()) {
        items.value = cartDoc.data().items || []
      } else {
        await setDoc(cartRef, {
          items: [],
          createdAt: serverTimestamp(),
          updatedAt: serverTimestamp()
        })
        items.value = []
      }
      loading.value = false
      error.value = null
    } catch (err) {
      console.error("Error fetching cart:", err)
      error.value = "Failed to load your cart"
      loading.value = false
    }
  }

  const addItem = async (item) => {
    if (!auth.user) return
    error.value = null

    try {
      console.log('=== Adding Item to Cart ===')
      console.log('Original item:', item)
      console.log('Restaurant info in item:', {
        id: item.restaurantId,
        name: item.restaurantName,
        restaurant: item.restaurant
      })
      const cartRef = doc(db, 'carts', auth.user.uid)
      const existingItemIndex = items.value.findIndex(i => i.id === item.id)

      // Log incoming item for debugging
      console.log('Adding item:', item)

      // Ensure restaurant info is captured with default values
      const restaurantId = item.restaurantId || item.restaurant?.id || 'unknown'
      const restaurantName = item.restaurantName || item.restaurant?.name || 'Restaurant'

      // Create a clean item object without undefined values
      const itemWithRestaurant = {
        id: item.id,
        name: item.name || 'Unknown Item',
        price: item.price || 0,
        restaurantId: item.restaurantId || item.restaurant?.id || 'unknown',
        restaurantName: item.restaurantName || item.restaurant?.name || 'Restaurant',
        restaurant: {
          id: item.restaurantId || item.restaurant?.id || 'unknown',
          name: item.restaurantName || item.restaurant?.name || 'Restaurant'
        },
        quantity: 1
      }

      console.log('Processed item:', itemWithRestaurant)

      if (existingItemIndex >= 0) {
        const updatedItems = [...items.value]
        updatedItems[existingItemIndex] = {
          ...updatedItems[existingItemIndex],
          quantity: (updatedItems[existingItemIndex].quantity || 0) + 1
        }

        // Clean the items array before updating Firestore
        const cleanItems = updatedItems.map(item => ({
          id: item.id,
          name: item.name || 'Unknown Item',
          price: item.price || 0,
          quantity: item.quantity || 1,
          restaurantId: item.restaurantId || 'unknown',
          restaurantName: item.restaurantName || 'Restaurant',
          restaurant: {
            id: item.restaurantId || 'unknown',
            name: item.restaurantName || 'Restaurant'
          }
        }))

        await updateDoc(cartRef, {
          items: cleanItems,
          updatedAt: serverTimestamp()
        })
        items.value = updatedItems
      } else {
        const newItem = {
          ...itemWithRestaurant,
          quantity: 1
        }
        const newItems = [...items.value, newItem]

        // Clean the items array before updating Firestore
        const cleanItems = newItems.map(item => ({
          id: item.id,
          name: item.name || 'Unknown Item',
          price: item.price || 0,
          quantity: item.quantity || 1,
          restaurantId: item.restaurantId || 'unknown',
          restaurantName: item.restaurantName || 'Restaurant',
          restaurant: {
            id: item.restaurantId || 'unknown',
            name: item.restaurantName || 'Restaurant'
          }
        }))

        await updateDoc(cartRef, {
          items: cleanItems,
          updatedAt: serverTimestamp()
        })
        items.value = newItems
      }

      console.log('Updated cart items:', items.value)
    } catch (err) {
      console.error("Error adding to cart:", err)
      error.value = "Failed to add item to cart"
      // Log full error details
      console.log('Full error:', {
        message: err.message,
        code: err.code,
        details: err
      })
    }
  }

  const removeItem = async (itemId) => {
    if (!auth.user) return
    error.value = null

    try {
      const cartRef = doc(db, 'carts', auth.user.uid)
      const existingItemIndex = items.value.findIndex(i => i.id === itemId)

      if (existingItemIndex >= 0) {
        const updatedItems = [...items.value]
        if (updatedItems[existingItemIndex].quantity > 1) {
          // Reduce quantity if more than 1
          updatedItems[existingItemIndex].quantity -= 1
        } else {
          // Remove item if quantity is 1
          updatedItems.splice(existingItemIndex, 1)
        }

        await updateDoc(cartRef, {
          items: updatedItems,
          updatedAt: serverTimestamp()
        })
        items.value = updatedItems
      }
    } catch (err) {
      console.error("Error removing from cart:", err)
      error.value = "Failed to remove item from cart"
    }
  }

  const clearCart = async () => {
    if (!auth.user) return
    error.value = null

    try {
      const cartRef = doc(db, 'carts', auth.user.uid)

      await updateDoc(cartRef, {
        items: [],
        updatedAt: serverTimestamp()
      })

      items.value = []
    } catch (err) {
      console.error("Error clearing cart:", err)
      error.value = "Failed to clear your cart"
    }
  }

  return {
    items,
    total,
    loading,
    error,
    initCart,
    addItem,
    removeItem,
    clearCart
  }
})
