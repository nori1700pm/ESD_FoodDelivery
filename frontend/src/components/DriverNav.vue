<template>
  <div class="bg-white shadow-md mb-6 rounded-lg p-4">
    <div class="flex items-center justify-between">
      <h2 class="text-lg font-bold">Driver Dashboard</h2>
      
      <div class="flex space-x-4">
        <router-link 
          to="/activeOrder" 
          class="px-4 py-2 rounded-lg hover:bg-gray-100"
          :class="{ 'bg-blue-100 text-blue-700': $route.path === '/activeOrder' }"
        >
          <div class="flex items-center">
            <vue-feather type="truck" size="16" class="mr-2" />
            Active Delivery
          </div>
        </router-link>
        
        <router-link 
          to="/driver-orders" 
          class="px-4 py-2 rounded-lg hover:bg-gray-100"
          :class="{ 'bg-blue-100 text-blue-700': $route.path === '/driver-orders' }"
        >
          <div class="flex items-center">
            <vue-feather type="list" size="16" class="mr-2" />
            Delivery History
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import VueFeather from 'vue-feather'
</script>
