<template>
  <div class="landing-page">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="overlay">
        <div class="hero-content">
          <img :src="logoImg" alt="nomnomGO logo" class="logo" />
          <h1 class="title">nomnomGO!</h1>
          <p class="subtitle">Delicious food delivered to your doorstep</p>
          <div class="btn-container">
            <router-link to="/login" class="btn btn-primary">
              Sign In
            </router-link>
            <router-link to="/register" class="btn btn-secondary">
              Create Account
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="features-section">
      <div class="container">
        <h2 class="section-title">Why Choose nomnomGO?</h2>
        
        <div class="features-grid">
          <div class="feature-card">
            <vue-feather type="truck" size="48" class="feature-icon"></vue-feather>
            <h3>Fast Delivery</h3>
            <p>Get your food delivered quickly right to your doorstep</p>
          </div>
          
          <div class="feature-card">
            <custom-icons type="utensils" size="48" class="feature-icon"></custom-icons>
            <h3>Wide Selection</h3>
            <p>Choose from hundreds of restaurants in your area</p>
          </div>
          
          <div class="feature-card">
            <vue-feather type="credit-card" size="48" class="feature-icon"></vue-feather>
            <h3>Easy Payments</h3>
            <p>Securely pay with your digital wallet or credit card</p>
          </div>
        </div>
      </div>
    </div>

    <!-- How It Works Section -->
    <div class="how-it-works-section">
      <div class="container">
        <h2 class="section-title">How It Works</h2>
        
        <div class="steps-container">
          <div class="step">
            <div class="step-number">1</div>
            <h3>Browse Restaurants</h3>
            <p>Find your favorite restaurants and dishes</p>
          </div>
          
          <div class="step">
            <div class="step-number">2</div>
            <h3>Place Your Order</h3>
            <p>Select items and customize your order</p>
          </div>
          
          <div class="step">
            <div class="step-number">3</div>
            <h3>Delivery</h3>
            <p>Track your delivery in real-time</p>
          </div>
          
          <div class="step">
            <div class="step-number">4</div>
            <h3>Enjoy!</h3>
            <p>Receive your food and enjoy your meal</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="landing-footer">
      <div class="container">
        <p>&copy; {{ new Date().getFullYear() }} nomnomGO! All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import VueFeather from 'vue-feather';
import CustomIcons from '../components/CustomIcons.vue';
// Import the image
import logoImg from '../assets/nomnomgo-logo.jpg';
</script>

<style scoped>
.landing-page {
  font-family: 'Roboto', sans-serif;
  color: #333;
  overflow-x: hidden; /* Prevent horizontal scroll */
}

/* Hero Section */
.hero-section {
  height: 100vh;
  background-image: url('https://images.unsplash.com/photo-1504674900247-0877df9cc836?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80'); /* Changed to food dish image */
  background-size: cover;
  background-position: center;
  background-attachment: fixed; /* This creates the parallax effect */
  position: relative;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.logo {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 50%;
  margin: 0 auto 24px;  /* Changed from margin-bottom to margin with auto for left/right */
  border: 3px solid white;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  display: block;  /* Added display block for proper centering */
}

.hero-content {
  max-width: 800px;
  padding: 0 20px;
}

.title {
  font-size: 4rem;
  font-weight: 700;
  color: white;
  margin-bottom: 16px;
  letter-spacing: -0.5px;
}

.subtitle {
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 32px;
}

.btn-container {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}

.btn {
  display: inline-block;
  padding: 12px 24px;
  border-radius: 4px;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.3s ease;
  font-size: 1rem;
  min-width: 160px;
}

.btn-primary {
  background-color: #3f51b5;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.btn-primary:hover {
  background-color: #303f9f;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.btn-secondary {
  background-color: transparent;
  color: white;
  border: 2px solid white;
}

.btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

/* Features Section */
.features-section {
  padding: 80px 20px;
  background-color: #f5f5f5;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  margin-bottom: 60px;
  color: #333;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.feature-card {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  margin-bottom: 20px;
  color: #3f51b5;
  display: block;
}

.feature-card h3 {
  font-size: 1.5rem;
  margin-bottom: 12px;
  color: #333;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

/* How It Works Section */
.how-it-works-section {
  padding: 80px 20px;
  background-color: white;
}

.steps-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 20px;
}

.step {
  flex: 1;
  min-width: 200px;
  text-align: center;
  padding: 20px;
}

.step-number {
  width: 50px;
  height: 50px;
  background-color: #3f51b5;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 auto 20px;
}

.step h3 {
  font-size: 1.3rem;
  margin-bottom: 10px;
  color: #333;
}

.step p {
  color: #666;
}

/* Footer */
.landing-footer {
  background-color: #333;
  color: white;
  padding: 20px;
  text-align: center;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
  .logo {
    width: 80px;
    height: 80px;
  }
  
  .title {
    font-size: 2.5rem;
  }
  
  .subtitle {
    font-size: 1.2rem;
  }
  
  .btn-container {
    flex-direction: column;
  }
  
  .step {
    min-width: 100%;
  }
}
</style>