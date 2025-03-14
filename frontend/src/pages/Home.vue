<template>
  <div class="max-w-5xl mx-auto">
    <div class="bg-blue-600 text-white rounded-lg p-8 mb-8">
      <h1 class="text-3xl font-bold mb-4">Food Delivery App</h1>
      <p class="text-xl mb-6">Order food from your favorite restaurants</p>
      <router-link 
        to="/restaurants" 
        class="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-blue-50"
      >
        Browse Restaurants
      </router-link>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="bg-white p-6 rounded-lg shadow-md">
        <h2 class="text-xl font-semibold mb-2">Fast Delivery</h2>
        <p class="text-gray-600">Get your food delivered quickly to your doorstep</p>
      </div>
      <div class="bg-white p-6 rounded-lg shadow-md">
        <h2 class="text-xl font-semibold mb-2">Wide Selection</h2>
        <p class="text-gray-600">Choose from hundreds of restaurants</p>
      </div>
      <div class="bg-white p-6 rounded-lg shadow-md">
        <h2 class="text-xl font-semibold mb-2">Easy Payments</h2>
        <p class="text-gray-600">Pay with your digital wallet securely</p>
      </div>
    </div>
  </div>
</template>
