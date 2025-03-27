import { defineStore } from 'pinia'
import { ref } from 'vue'
import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  setPersistence,
  browserLocalPersistence  
} from 'firebase/auth'
import { auth } from '../config/firebase'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(true)
  setPersistence(auth, browserLocalPersistence)
    .then(() => {
      onAuthStateChanged(auth, (userData) => {
        user.value = userData
        loading.value = false
      })
    })
    .catch((error) => {
      console.error("Persistence setup failed:", error)
      loading.value = false
    })
  const login = async (email, password) => {
    return signInWithEmailAndPassword(auth, email, password)
  }

  const register = async (email, password) => {
    return createUserWithEmailAndPassword(auth, email, password)
  }

  const logout = async () => {
    return signOut(auth)
  }

  return { user, loading, login, register, logout }
})
