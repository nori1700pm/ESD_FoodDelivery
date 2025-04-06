<template>
  <div>
    <!-- Back Button -->
    <div class="mt-4 ml-4">
      <button 
        @click="$router.push('/restaurants')" 
        class="text-gray-600 hover:text-blue-500 font-semibold"
      >
        ← Back to Restaurants
      </button>
    </div>
    

    <!-- Toast Notification -->
    <div 
      v-if="toastMessage" 
      class="fixed top-16 right-4 bg-green-500 text-white px-4 py-2 rounded shadow-lg z-50"
    >
      {{ toastMessage }}
    </div>

    <div v-if="loading" class="flex justify-center items-center h-64">
      <loading-spinner size="large" />
    </div>

    <div v-else-if="error || !restaurant" class="text-center py-10">
      <p class="text-red-500 text-lg">{{ error || "Failed to load restaurant details" }}</p>
      <button 
        @click="$router.back()"
        class="mt-4 bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
      >
        Go Back
      </button>
    </div>

    <div v-else>
      <div class="relative h-64 mb-6">
        <img 
          :src="restaurant.imageUrl" 
          :alt="restaurant.name" 
          class="w-full h-full object-cover rounded-lg" 
        />
        <div class="absolute inset-0 bg-black opacity-40 rounded-lg"></div>
        <div class="absolute bottom-0 left-0 p-6 text-white">
          <h1 class="text-3xl font-bold">{{ restaurant.name }}</h1>
          <p class="text-lg">{{ restaurant.cuisine }}</p>
          <div class="flex items-center mt-2">
            <span class="text-yellow-400 mr-1">★</span>
            <span>{{ restaurant.rating }}</span>
            <span class="mx-2">•</span>
            <span>{{ restaurant.deliveryTime }}</span>
            <span class="mx-2">•</span>
            <span>Delivery: ${{ restaurant.deliveryFee.toFixed(2) }}</span>
          </div>
        </div>
      </div>

      <p class="mb-6 text-gray-700">{{ restaurant.description }}</p>
      <p class="mb-6 text-gray-600">{{ restaurant.address }}</p>

      <h2 class="text-2xl font-bold mb-4">Menu</h2>

      <div class="bg-white rounded-lg shadow-md">
        <div v-if="menuItems.length > 0">
          <div v-for="item in menuItems" :key="item.id" class="border-b last:border-0">
            <div class="flex items-center gap-4 p-4">
              <img
                :src="item.image"
                :alt="item.name"
                class="w-24 h-24 object-cover rounded-lg"
              />
              <div class="flex-1">
                <h3 class="text-lg font-semibold">{{ item.name }}</h3>
                <p class="text-gray-600 text-sm">{{ item.description }}</p>
                <div class="flex items-center justify-between mt-2">
                  <span class="font-semibold">${{ item.price.toFixed(2) }}</span>
                  <button
                    @click="handleAddToCart(item)"
                    class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                  >
                    Add to Cart
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <p v-else class="p-4 text-center text-gray-500">No menu items available.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { doc, getDoc, collection, query, where, getDocs } from 'firebase/firestore'
import { db } from '../config/firebase'
import { useCartStore } from '../stores/cart'
import { useAuthStore } from '../stores/auth'
import { storeToRefs } from 'pinia'
import VueFeather from 'vue-feather'
import LoadingSpinner from '../components/LoadingSpinner.vue'

const route = useRoute()
const router = useRouter()
const cart = useCartStore()
const auth = useAuthStore()

const { user } = storeToRefs(auth)

const restaurant = ref(null)
const menuItems = ref([])
const loading = ref(true)
const error = ref(null)
const toastMessage = ref(null);

const showToast = (message) => {
  toastMessage.value = message;
  setTimeout(() => {
    toastMessage.value = null;
  }, 3000); // Toast disappears after 3 seconds
};

const handleAddToCart = (menuItem) => {
  if (!user.value) {
    alert("Please log in to add items to your cart");
    return;
  }

  const cartItems = cart.items; // Access items in the cart
  if (cartItems.length > 0) {
    const existingRestaurantId = cartItems[0].restaurant.id;
    if (existingRestaurantId !== restaurant.value.id) {
      alert("You can only add items from the same restaurant.");
      return;
    }
  }

  const itemWithRestaurant = {
    id: menuItem.id,
    name: menuItem.name,
    price: menuItem.price,
    image: menuItem.image,
    restaurantId: restaurant.value.id,
    restaurantName: restaurant.value.name,
    restaurant: {
      id: restaurant.value.id,
      name: restaurant.value.name,
      deliveryFee: restaurant.value.deliveryFee,
    },
  };

  cart.addItem(itemWithRestaurant);
  showToast(`${menuItem.name} added to cart!`);
}

onMounted(async () => {
  const id = route.params.id
  if (!id) return

  try {
    loading.value = true
    error.value = null

    // Get restaurant details
    const restaurantDoc = await getDoc(doc(db, 'restaurants', id))
    
    if (!restaurantDoc.exists()) {
      error.value = "Restaurant not found."
      loading.value = false
      return
    }
    
    const restaurantData = restaurantDoc.data()
    restaurant.value = {
      id: restaurantDoc.id,
      name: restaurantData.name,
      ...restaurantData
    }
    
    console.log('Loaded restaurant:', restaurant.value)
    
    // Get menu items for this restaurant
    const menuItemsQuery = query(
      collection(db, 'menu_items'), 
      where('restaurantId', '==', id)
    )
    
    const menuItemsSnapshot = await getDocs(menuItemsQuery)
    
    // Add restaurant info to menu items
    menuItems.value = menuItemsSnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data(),
      restaurantId: restaurant.value.id,
      restaurantName: restaurant.value.name
    }))
    
    console.log('Loaded menu items:', menuItems.value)
  } catch (err) {
    console.error("Error fetching restaurant details:", err)
    error.value = "Failed to load restaurant details. Please try again later."
  } finally {
    loading.value = false
  }
})
</script>
