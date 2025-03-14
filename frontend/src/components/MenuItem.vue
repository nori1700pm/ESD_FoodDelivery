<template>
  <div class="flex items-center gap-4 p-4 border-b">
    <img
      :src="image"
      :alt="name"
      class="w-24 h-24 object-cover rounded-lg"
    />
    
    <div class="flex-1">
      <h3 class="text-lg font-semibold">{{ name }}</h3>
      <p class="text-gray-600 text-sm">{{ description }}</p>
      <div class="flex items-center justify-between mt-2">
        <span class="font-semibold">${{ price.toFixed(2) }}</span>
        <button
          @click="$emit('addToCart', id)"
          class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Add to Cart
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  id: {
    type: String,
    required: true
  },
  name: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  price: {
    type: Number,
    required: true
  },
  image: {
    type: String,
    required: true
  }
})

defineEmits(['addToCart'])
</script>
