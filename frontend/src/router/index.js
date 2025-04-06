import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { watch } from 'vue' 
// Page components
import Home from '../pages/Home.vue'
import Login from '../pages/Login.vue'
import Register from '../pages/Register.vue'
import RestaurantList from '../pages/RestaurantList.vue'
import RestaurantDetails from '../pages/RestaurantDetails.vue'
import Cart from '../pages/Cart.vue'
import Checkout from '../pages/Checkout.vue'
import Orders from '../pages/Orders.vue'
import Profile from '../pages/Profile.vue'
import Wallet from '../pages/Wallet.vue'
import NotFound from '../pages/NotFound.vue'
import ActiveOrder from '../pages/ActiveOrder.vue'

const routes = [
  {
    path: '/',
    redirect: (to) => {
      const auth = useAuthStore()
      return auth.user ? '/restaurants' : '/login'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/restaurants',
    name: 'RestaurantList',
    component: RestaurantList,
    meta: { requiresAuth: true }
  },
  {
    path: '/restaurants/:id',
    name: 'RestaurantDetails',
    component: RestaurantDetails
  },
  {
    path: '/cart',
    name: 'Cart',
    component: Cart,
    meta: { requiresAuth: true }
  },
  {
    path: '/checkout',
    name: 'Checkout',
    component: Checkout,
    meta: { requiresAuth: true }
  },
  {
    path: '/orders',
    name: 'Orders',
    component: Orders,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/wallet',
    name: 'Wallet',
    component: Wallet,
    meta: { requiresAuth: true }
  },
  {
    path: '/wallet-success',
    name: 'WalletSuccess',
    component: () => import('../pages/WalletSuccess.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  },
  {
    path: '/activeOrder',
    name: 'ActiveOrder',
    component: ActiveOrder,
    meta: { requiresAuth: true, requiresDriver: true }
  },
  {
    path: '/driver-orders',
    name: 'DriverOrders',
    component: () => import('../pages/DriverOrders.vue'),
    meta: { requiresAuth: true, requiresDriver: true, title: 'Delivery History' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach(async (to, from, next) => {
  const auth = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresDriver = to.matched.some(record => record.meta.requiresDriver)
  
  // Wait for auth to initialize
  if (auth.loading) {
    // Wait for the auth state to be ready
    await new Promise(resolve => {
      const unsubscribe = watch(() => auth.loading, (loading) => {
        if (!loading) {
          unsubscribe()
          resolve()
        }
      })
    })
  }
  
  if (requiresAuth && !auth.user) {
    next('/login')
  } else if (requiresDriver && auth.user && !auth.user.email.endsWith('@driver.com')) {
    next('/')
  } else {
    next()
  }
})
export default router
