<template>
  <div class="App min-h-screen flex flex-col bg-gray-50">
    <Navbar />
    <main class="container mx-auto px-4 py-8 flex-grow">
      <router-view />
    </main>
    <Footer />
  </div>
</template>

<script setup>
import Navbar from '@/components/Navbar.vue'
import Footer from '@/components/Footer.vue'
</script>
