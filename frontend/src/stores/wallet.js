import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useAuthStore } from './auth'
import { doc, getDoc, updateDoc, setDoc, onSnapshot, serverTimestamp, collection, addDoc } from 'firebase/firestore'
import { db } from '../config/firebase'

export const useWalletStore = defineStore('wallet', () => {
  const balance = ref(0)
  const loading = ref(true)
  const error = ref(null)
  const auth = useAuthStore()

  let unsubscribe = null

  const initWallet = async () => {
    if (!auth.user) {
      balance.value = 0
      loading.value = false
      return
    }

    try {
      const walletRef = doc(db, 'wallets', auth.user.uid)
      const walletDoc = await getDoc(walletRef)

      if (!walletDoc.exists()) {
        await setDoc(walletRef, {
          balance: 0,
          createdAt: serverTimestamp(),
          updatedAt: serverTimestamp()
        })
      }

      unsubscribe = onSnapshot(walletRef, (snapshot) => {
        if (snapshot.exists()) {
          balance.value = snapshot.data().balance || 0
          loading.value = false
          error.value = null
        }
      })
    } catch (err) {
      console.error("Error initializing wallet:", err)
      error.value = "Failed to initialize wallet"
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
      
      const walletRef = doc(db, 'wallets', auth.user.uid)
      const walletDoc = await getDoc(walletRef)
      
      if (!walletDoc.exists()) {
        await setDoc(walletRef, {
          balance: amount,
          createdAt: serverTimestamp(),
          updatedAt: serverTimestamp()
        })
      } else {
        const currentBalance = walletDoc.data().balance || 0
        await updateDoc(walletRef, {
          balance: currentBalance + amount,
          updatedAt: serverTimestamp()
        })
      }

      // Record the transaction in transaction history
      await addDoc(collection(db, 'transactions'), {
        userId: auth.user.uid,
        amount: amount,
        type: 'DEPOSIT',
        timestamp: serverTimestamp(),
        status: 'COMPLETED'
      })

      return true
    } catch (err) {
      console.error("Error adding money:", err)
      error.value = "Failed to add money to wallet"
      return false
    }
  }

  const processPayment = async (amount) => {
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
      
      const walletRef = doc(db, 'wallets', auth.user.uid)
      const walletDoc = await getDoc(walletRef)
      
      if (!walletDoc.exists()) {
        error.value = "Wallet not found"
        return false
      }
      
      const currentBalance = walletDoc.data().balance || 0
      
      if (currentBalance < amount) {
        error.value = "Insufficient balance"
        return false
      }
      
      await updateDoc(walletRef, {
        balance: currentBalance - amount,
        updatedAt: serverTimestamp()
      })
      
      // Record the transaction
      await addDoc(collection(db, 'transactions'), {
        userId: auth.user.uid,
        amount: -amount,
        type: 'PAYMENT',
        timestamp: serverTimestamp(),
        status: 'COMPLETED'
      })
      
      return true
    } catch (err) {
      console.error("Error processing payment:", err)
      error.value = "Failed to process payment"
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
