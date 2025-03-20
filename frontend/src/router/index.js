import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

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
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  
  if (to.meta.requiresAuth && !auth.user && !auth.loading) {
    next('/login')
  } else if (to.path === '/logout') {
    auth.logout().then(() => {
      next('/login')
    })
  } else {
    next()
  }
},
)


export default router
