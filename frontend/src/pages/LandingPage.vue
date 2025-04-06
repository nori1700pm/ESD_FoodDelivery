<template>
  <div class="landing-page">
    <!-- Hero Section -->
    <div class="hero-section">
      <div class="overlay">
        <div class="hero-content">
          <div class="logo-container">
            <img :src="logoImg" alt="nomnomGO logo" class="logo animate-bounce-slow" />
          </div>
          <h1 class="title">nomnomGO!</h1>
          <p class="subtitle">Delicious food delivered to your doorstep</p>
          <div class="btn-container">
            <router-link to="/login" class="btn btn-primary">
              <vue-feather type="log-in" size="18" class="mr-2"></vue-feather>
              Sign In
            </router-link>
            <router-link to="/register" class="btn btn-secondary">
              <vue-feather type="user-plus" size="18" class="mr-2"></vue-feather>
              Create Account
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="features-section">
      <div class="container">
        <h2 class="section-title">Why Choose <span class="text-gradient">nomnomGO</span>?</h2>
        
        <div class="features-grid">
          <div class="feature-card">
            <div class="icon-container">
              <vue-feather type="truck" size="48" class="feature-icon"></vue-feather>
            </div>
            <h3>Fast Delivery</h3>
            <p>Get your food delivered quickly right to your doorstep</p>
          </div>
          
          <div class="feature-card">
            <div class="icon-container">
              <custom-icons type="utensils" size="48" class="feature-icon"></custom-icons>
            </div>
            <h3>Wide Selection</h3>
            <p>Choose from hundreds of restaurants in your area</p>
          </div>
          
          <div class="feature-card">
            <div class="icon-container">
              <vue-feather type="credit-card" size="48" class="feature-icon"></vue-feather>
            </div>
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

    <!-- Testimonials Section -->
    <div class="testimonials-section">
      <div class="container">
        <h2 class="section-title">What Our Customers Say</h2>
        
        <div class="testimonials-grid">
          <div class="testimonial-card">
            <div class="quote-icon">
              <vue-feather type="message-circle" size="24"></vue-feather>
            </div>
            <p class="testimonial-text">"The food arrived hot and fresh. The delivery was super quick and the driver was very polite!"</p>
            <div class="testimonial-author">
              <div class="avatar">JD</div>
              <div class="author-name">John Doe</div>
            </div>
          </div>
          
          <div class="testimonial-card">
            <div class="quote-icon">
              <vue-feather type="message-circle" size="24"></vue-feather>
            </div>
            <p class="testimonial-text">"I love how easy it is to track my orders. The variety of restaurants available is amazing!"</p>
            <div class="testimonial-author">
              <div class="avatar">JS</div>
              <div class="author-name">Jane Smith</div>
            </div>
          </div>
          
          <div class="testimonial-card">
            <div class="quote-icon">
              <vue-feather type="message-circle" size="24"></vue-feather>
            </div>
            <p class="testimonial-text">"Great app with excellent customer service. I had an issue with my order and it was resolved immediately."</p>
            <div class="testimonial-author">
              <div class="avatar">RJ</div>
              <div class="author-name">Robert Johnson</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- CTA Section -->
    <div class="cta-section">
      <div class="container">
        <div class="cta-content">
          <h2>Ready to Order?</h2>
          <p>Sign up now and get $5 off your first order!</p>
          <router-link to="/register" class="cta-button">
            <vue-feather type="user-plus" size="18" class="mr-2"></vue-feather>
            Create Account
          </router-link>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="landing-footer">
      <div class="container">
        <div class="footer-grid">
          <div class="footer-logo">
            <img :src="logoImg" alt="nomnomGO logo" class="footer-logo-img" />
            <h3>nomnomGO!</h3>
            <p>Delicious food delivered to your doorstep</p>
          </div>
          
          <div class="footer-links">
            <h4>Quick Links</h4>
            <ul>
              <li><router-link to="/login">Sign In</router-link></li>
              <li><router-link to="/register">Create Account</router-link></li>
              <li><a href="#">About Us</a></li>
              <li><a href="#">Contact</a></li>
            </ul>
          </div>
          
          <div class="footer-contact">
            <h4>Contact Us</h4>
            <p><vue-feather type="mail" size="14" class="mr-2"></vue-feather> support@nomnomgo.com</p>
            <p><vue-feather type="phone" size="14" class="mr-2"></vue-feather> +65 9123 4567</p>
            <div class="social-icons">
              <a href="#" class="social-icon"><vue-feather type="facebook" size="18"></vue-feather></a>
              <a href="#" class="social-icon"><vue-feather type="instagram" size="18"></vue-feather></a>
              <a href="#" class="social-icon"><vue-feather type="twitter" size="18"></vue-feather></a>
            </div>
          </div>
        </div>
        
        <div class="footer-bottom">
          <p>&copy; {{ new Date().getFullYear() }} nomnomGO! All rights reserved.</p>
        </div>
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
  background-image: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)), url('https://images.unsplash.com/photo-1504674900247-0877df9cc836?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=2070&q=80');
  background-size: cover;
  background-position: center;
  background-attachment: fixed;
  position: relative;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.7) 0%, rgba(0, 0, 0, 0.5) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
}

.logo-container {
  position: relative;
  width: 140px;
  height: 140px;
  margin: 0 auto 28px;
}

.logo {
  width: 140px;
  height: 140px;
  object-fit: cover;
  border-radius: 50%;
  border: 4px solid white;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
}

@keyframes bounceSlow {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.animate-bounce-slow {
  animation: bounceSlow 5s infinite ease-in-out;
}

.hero-content {
  max-width: 800px;
  padding: 0 20px;
  z-index: 2;
}

.title {
  font-size: 5rem;
  font-weight: 800;
  color: white;
  margin-bottom: 16px;
  letter-spacing: -1px;
  text-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

.subtitle {
  font-size: 1.8rem;
  color: rgba(255, 255, 255, 0.95);
  margin-bottom: 40px;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
}

.btn-container {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 24px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 14px 28px;
  border-radius: 8px;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
  font-size: 1.1rem;
  min-width: 180px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-primary {
  background: linear-gradient(135deg, #4a6cf7 0%, #3452db 100%);
  color: white;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #3452db 0%, #2a3eb1 100%);
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  color: white;
  border: 2px solid white;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25);
}

/* Features Section */
.features-section {
  padding: 100px 20px;
  background: linear-gradient(135deg, #f9f9f9 0%, #f5f5f5 100%);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  text-align: center;
  font-size: 2.8rem;
  font-weight: 700;
  margin-bottom: 70px;
  color: #333;
  position: relative;
}

.section-title:after {
  content: '';
  display: block;
  width: 80px;
  height: 4px;
  background: linear-gradient(90deg, #4a6cf7 0%, #3452db 100%);
  margin: 24px auto 0;
  border-radius: 2px;
}

.text-gradient {
  background: linear-gradient(90deg, #4a6cf7, #5e17eb);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: #4a6cf7;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 40px;
}

.feature-card {
  background: white;
  padding: 40px 30px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  text-align: center;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.feature-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.feature-card:before {
  content: '';
  position: absolute;
  width: 100%;
  height: 6px;
  background: linear-gradient(90deg, #4a6cf7, #3452db);
  top: 0;
  left: 0;
  transform: scaleX(0);
  transform-origin: right;
  transition: transform 0.4s ease;
}

.feature-card:hover:before {
  transform: scaleX(1);
  transform-origin: left;
}

.icon-container {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, rgba(74, 108, 247, 0.1) 0%, rgba(52, 82, 219, 0.1) 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 24px;
}

.feature-icon {
  color: #4a6cf7;
}

.feature-card h3 {
  font-size: 1.6rem;
  font-weight: 600;
  margin-bottom: 16px;
  color: #333;
}

.feature-card p {
  color: #666;
  line-height: 1.7;
  font-size: 1.1rem;
}

/* How It Works Section */
.how-it-works-section {
  padding: 100px 20px;
  background: white;
}

.steps-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 30px;
  position: relative;
}

.steps-container:before {
  content: '';
  position: absolute;
  top: 60px;
  left: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, #4a6cf7, #3452db);
  z-index: 0;
  opacity: 0.3;
}

.step {
  flex: 1;
  min-width: 200px;
  text-align: center;
  padding: 20px;
  position: relative;
  background: white;
  z-index: 1;
}

.step-number {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #4a6cf7 0%, #3452db 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 600;
  margin: 0 auto 24px;
  box-shadow: 0 8px 20px rgba(74, 108, 247, 0.3);
}

.step h3 {
  font-size: 1.4rem;
  font-weight: 600;
  margin-bottom: 12px;
  color: #333;
}

.step p {
  color: #666;
  font-size: 1.1rem;
}

/* Testimonials Section */
.testimonials-section {
  padding: 100px 20px;
  background: linear-gradient(135deg, #f5f7ff 0%, #edf0ff 100%);
}

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 40px;
}

.testimonial-card {
  background: white;
  padding: 30px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  position: relative;
  transition: all 0.3s ease;
}

.testimonial-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.quote-icon {
  position: absolute;
  top: -15px;
  left: 30px;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #4a6cf7 0%, #3452db 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 20px rgba(74, 108, 247, 0.3);
}

.testimonial-text {
  font-size: 1.1rem;
  line-height: 1.6;
  color: #555;
  margin-bottom: 24px;
  font-style: italic;
}

.testimonial-author {
  display: flex;
  align-items: center;
}

.avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #4a6cf7 0%, #3452db 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  margin-right: 12px;
}

.author-name {
  font-weight: 600;
  color: #333;
}

/* CTA Section */
.cta-section {
  padding: 80px 20px;
  background: linear-gradient(135deg, #4a6cf7 0%, #3452db 100%);
  color: white;
}

.cta-content {
  text-align: center;
  max-width: 800px;
  margin: 0 auto;
}

.cta-section h2 {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 16px;
}

.cta-section p {
  font-size: 1.3rem;
  margin-bottom: 32px;
  opacity: 0.9;
}

.cta-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: white;
  color: #4a6cf7;
  padding: 16px 32px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1.1rem;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
}

.cta-button:hover {
  transform: translateY(-3px);
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.3);
}

/* Footer */
.landing-footer {
  background: #222;
  color: white;
  padding: 80px 20px 40px;
}

.footer-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 40px;
  margin-bottom: 40px;
}

.footer-logo {
  text-align: center;
}

.footer-logo-img {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  margin-bottom: 16px;
  border: 3px solid rgba(255, 255, 255, 0.2);
}

.footer-logo h3 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 8px;
}

.footer-logo p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.footer-links h4, .footer-contact h4 {
  font-size: 1.2rem;
  font-weight: 600;
  margin-bottom: 20px;
}

.footer-links ul {
  list-style: none;
  padding: 0;
}

.footer-links li {
  margin-bottom: 12px;
}

.footer-links a {
  color: rgba(255, 255, 255, 0.7);
  text-decoration: none;
  transition: color 0.3s ease;
}

.footer-links a:hover {
  color: white;
}

.footer-contact p {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.social-icons {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.social-icon {
  width: 36px;
  height: 36px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  transition: all 0.3s ease;
}

.social-icon:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-3px);
}

.footer-bottom {
  text-align: center;
  padding-top: 30px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-bottom p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.9rem;
}

/* Responsive Adjustments */
@media (max-width: 768px) {
  .title {
    font-size: 3.5rem;
  }
  
  .subtitle {
    font-size: 1.4rem;
  }
  
  .btn-container {
    flex-direction: column;
    gap: 16px;
  }
  
  .section-title {
    font-size: 2.2rem;
  }
  
  .feature-card, .testimonial-card {
    padding: 30px 20px;
  }
  
  .step {
    min-width: 100%;
  }
  
  .steps-container:before {
    display: none;
  }
  
  .cta-section h2 {
    font-size: 2rem;
  }
  
  .cta-section p {
    font-size: 1.1rem;
  }
}

@media (max-width: 480px) {
  .title {
    font-size: 2.8rem;
  }
  
  .subtitle {
    font-size: 1.2rem;
  }
  
  .logo {
    width: 100px;
    height: 100px;
  }
  
  .logo-container {
    width: 100px;
    height: 100px;
  }
  
  .btn {
    width: 100%;
  }
  
  .feature-card h3, .step h3 {
    font-size: 1.3rem;
  }
  
  .section-title {
    font-size: 1.8rem;
  }
}
</style>