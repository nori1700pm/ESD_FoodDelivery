import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { useAuthStore } from './auth'
import { doc, getDoc, updateDoc, setDoc, serverTimestamp } from 'firebase/firestore'
import { db } from '../config/firebase'

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
      const cartRef = doc(db, 'carts', auth.user.uid)
      const existingItemIndex = items.value.findIndex(i => i.id === item.id)

      if (existingItemIndex >= 0) {
        const updatedItems = [...items.value]
        updatedItems[existingItemIndex].quantity += 1
        await updateDoc(cartRef, {
          items: updatedItems,
          updatedAt: serverTimestamp()
        })
        items.value = updatedItems
      } else {
        const newItem = { ...item, quantity: 1 }
        const newItems = [...items.value, newItem]
        await updateDoc(cartRef, {
          items: newItems,
          updatedAt: serverTimestamp()
        })
        items.value = newItems
      }
    } catch (err) {
      console.error("Error adding to cart:", err)
      error.value = "Failed to add item to cart"
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
