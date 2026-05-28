<template>
  <div class="hero-container">
    <div class="hero-content">
      <span class="hero-badge">🌸 Global Travel Planner</span>
      <h1 class="hero-title">
        Design your dream trip, from <span>Himeji</span> to the world
      </h1>
      <p class="hero-subtitle">
        Plan detailed itineraries, discover cultural gems worldwide, and calculate optimal travel routes with advanced spherical distance calculations effortlessly.
      </p>
      
      <div class="hero-actions">
        <template v-if="authStore.isAuthenticated">
          <BaseButton @click="router.push({ name: 'dashboard' })">
            Go to my Dashboard
          </BaseButton>
        </template>
        <template v-else>
          <BaseButton @click="router.push({ name: 'register' })">
            Get Started for Free
          </BaseButton>
          <BaseButton variant="secondary" @click="router.push({ name: 'login' })">
            Sign In
          </BaseButton>
        </template>
      </div>
    </div>
    
    <div class="hero-visual">
      <!-- High-end glowing glass container simulating an interactive planning layout card -->
      <div class="visual-card">
        <div class="card-glass-header">
          <span class="dot red"></span>
          <span class="dot yellow"></span>
          <span class="dot green"></span>
          <span class="card-tab-title">Itinerary - Day 1</span>
        </div>
        <div class="card-glass-body">
          <div class="timeline-item active">
            <span class="time">09:00</span>
            <div class="details">
              <h4>Arrival at Himeji Station 🚄</h4>
              <p>Shinkansen bullet train from Kyoto/Osaka</p>
            </div>
          </div>
          <div class="timeline-item">
            <span class="time">10:00</span>
            <div class="details">
              <h4>Himeji Castle (White Heron) 🏯</h4>
              <p>Guided tour of the main keep and fortresses</p>
            </div>
          </div>
          <div class="timeline-item">
            <span class="time">13:30</span>
            <div class="details">
              <h4>Lunch & Tea Ceremony at Koko-en 🍵</h4>
              <p>Traditional matcha tasting in the historic garden</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BaseButton from '@/components/BaseButton.vue'

const router = useRouter()
const authStore = useAuthStore()
</script>

<style scoped>
.hero-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 4rem;
  min-height: calc(100vh - 160px);
  padding: 2rem 0;
}

.hero-content {
  flex: 1.2;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 1.5rem;
}

.hero-badge {
  background: rgba(59, 130, 246, 0.08);
  border: 1px solid rgba(59, 130, 246, 0.2);
  color: #2563eb;
  padding: 0.5rem 1rem;
  border-radius: 2rem;
  font-size: 0.875rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  line-height: 1.15;
  color: #111827;
}

.hero-title span {
  background: linear-gradient(135deg, #2563eb, #db2777);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  font-size: 1.125rem;
  line-height: 1.6;
  color: #4b5563;
  max-width: 580px;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  flex-wrap: wrap;
}

.hero-visual {
  flex: 0.8;
  display: flex;
  justify-content: center;
  position: relative;
}

/* Beautiful dynamic planning layout visual */
.visual-card {
  width: 100%;
  max-width: 360px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(229, 231, 235, 0.5);
  border-radius: 1.25rem;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02);
  overflow: hidden;
  animation: float 4s ease-in-out infinite;
}

.card-glass-header {
  padding: 1rem 1.25rem;
  background: rgba(243, 244, 246, 0.6);
  border-bottom: 1px solid rgba(229, 231, 235, 0.5);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot.red { background-color: #ef4444; }
.dot.yellow { background-color: #f59e0b; }
.dot.green { background-color: #10b981; }

.card-tab-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: #6b7280;
  margin-left: 0.5rem;
}

.card-glass-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.timeline-item {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  position: relative;
}

.timeline-item::after {
  content: '';
  position: absolute;
  left: 21px;
  top: 30px;
  bottom: -20px;
  width: 2px;
  background: #e5e7eb;
}

.timeline-item:last-child::after {
  display: none;
}

.timeline-item .time {
  font-size: 0.75rem;
  font-weight: 700;
  color: #9ca3af;
  background: #f3f4f6;
  padding: 0.25rem 0.5rem;
  border-radius: 0.5rem;
  min-width: 42px;
  text-align: center;
}

.timeline-item.active .time {
  color: #2563eb;
  background: rgba(59, 130, 246, 0.1);
}

.timeline-item .details h4 {
  font-size: 0.9rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 0.15rem;
}

.timeline-item .details p {
  font-size: 0.75rem;
  color: #6b7280;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

@media (max-width: 1024px) {
  .hero-container {
    flex-direction: column;
    text-align: center;
    gap: 3rem;
  }
  
  .hero-content {
    align-items: center;
  }
  
  .hero-title {
    font-size: 2.75rem;
  }
  
  .hero-subtitle {
    margin: 0 auto;
  }
}
</style>