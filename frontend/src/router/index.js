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
import LandingPage from '../pages/LandingPage.vue'
import CustomerHome from '../pages/CustomerHome.vue'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: LandingPage,
    meta: { allowAnonymous: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { allowAnonymous: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { allowAnonymous: true }
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
  },
  {
    path: '/home',
    name: 'CustomerHome',
    component: CustomerHome,
    meta: { requiresAuth: true }
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
  const allowAnonymous = to.matched.some(record => record.meta.allowAnonymous)
  
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
  
  // Handle redirection based on auth status
  if (requiresAuth && !auth.user) {
    next('/')
  } else if (requiresDriver && auth.user && !auth.user.email.endsWith('@driver.com')) {
    next('/')
  } else if (to.path === '/' && auth.user && !allowAnonymous) {
    // If user is authenticated, redirect to restaurants page
    next('/restaurants')
  } else {
    next()
  }
})

export default router
