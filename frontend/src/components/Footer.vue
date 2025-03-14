<template>
  <footer class="bg-gray-800 text-white mt-12">
    <div class="container mx-auto px-4 py-8">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div>
          <h2 class="text-xl font-bold mb-4">FoodDelivery</h2>
          <p class="text-gray-300">
            Order food from your favorite restaurants and have it delivered to your doorstep.
          </p>
        </div>
        
        <div>
          <h3 class="text-lg font-semibold mb-4">Quick Links</h3>
          <ul class="space-y-2">
            <li><router-link to="/" class="text-gray-300 hover:text-white">Home</router-link></li>
            <li><router-link to="/restaurants" class="text-gray-300 hover:text-white">Restaurants</router-link></li>
            <li><router-link to="/orders" class="text-gray-300 hover:text-white">My Orders</router-link></li>
            <li><router-link to="/profile" class="text-gray-300 hover:text-white">My Profile</router-link></li>
          </ul>
        </div>
        
        <div>
          <h3 class="text-lg font-semibold mb-4">Contact Us</h3>
          <ul class="space-y-2">
            <li class="flex items-center">
              <vue-feather type="phone" size="16" class="mr-2"></vue-feather>
              <span class="text-gray-300">+65 9123 4567</span>
            </li>
            <li class="flex items-center">
              <vue-feather type="mail" size="16" class="mr-2"></vue-feather>
              <span class="text-gray-300">support@fooddelivery.com</span>
            </li>
            <li class="flex items-center">
              <vue-feather type="map-pin" size="16" class="mr-2"></vue-feather>
              <span class="text-gray-300">80 Stamford Road, Singapore 178902</span>
            </li>
          </ul>
        </div>
      </div>
      
      <div class="border-t border-gray-700 mt-8 pt-6 text-center">
        <p class="text-gray-400">&copy; {{ new Date().getFullYear() }} FoodDelivery. All rights reserved.</p>
      </div>
    </div>
  </footer>
</template>

<script setup>
import VueFeather from 'vue-feather'
</script>
