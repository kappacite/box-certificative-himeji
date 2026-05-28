<template>
  <div class="places-container">
    <header class="places-header">
      <h1>Explore Popular Landmarks 🌸</h1>
      <p class="subtitle">A curated selection of must-see attractions to include in your customized travel itineraries.</p>
    </header>

    <div class="places-grid">
      <!-- Place 1 -->
      <BaseCard hoverable class="place-card">
        <div class="place-image castle-img">
          <span class="place-tag">Must-See</span>
        </div>
        <div class="place-content">
          <h3>Himeji Castle (Himeji-jo)</h3>
          <p>Nicknamed the "White Heron Castle" due to its brilliant white exterior walls. It is one of Japan's twelve original surviving castles and is recognized as a registered UNESCO World Heritage site.</p>
          <div class="place-meta">
            <span class="meta-item">⏱️ Visit: 2-3h</span>
            <span class="meta-item">⭐ 4.9/5</span>
          </div>
        </div>
      </BaseCard>

      <!-- Place 2 -->
      <BaseCard hoverable class="place-card">
        <div class="place-image garden-img">
          <span class="place-tag">Nature</span>
        </div>
        <div class="place-content">
          <h3>Koko-en Garden</h3>
          <p>A compact complex of nine beautiful traditional Japanese gardens adjoining the castle grounds. Recreating authentic Edo-period landscape styles, they feature gorgeous waterfalls and tea ceremony houses.</p>
          <div class="place-meta">
            <span class="meta-item">⏱️ Visit: 1-2h</span>
            <span class="meta-item">⭐ 4.7/5</span>
          </div>
        </div>
      </BaseCard>

      <!-- Place 3 -->
      <BaseCard hoverable class="place-card">
        <div class="place-image temple-img">
          <span class="place-tag">Culture</span>
        </div>
        <div class="place-content">
          <h3>Mount Shosha & Engyo-ji Temple</h3>
          <p>Located atop Mount Shosha, this sprawling Buddhist temple complex founded over 1,000 years ago offers a spiritual and peaceful atmosphere, made famous internationally as a filming location for "The Last Samurai".</p>
          <div class="place-meta">
            <span class="meta-item">⏱️ Visit: Half day</span>
            <span class="meta-item">⭐ 4.8/5</span>
          </div>
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup>
import BaseCard from '@/components/BaseCard.vue'
</script>

<style scoped>
.places-container {
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.places-header h1 {
  font-size: 2.25rem;
  color: #111827;
  font-weight: 800;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #047857, #10b981);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.places-header .subtitle {
  color: #6b7280;
  font-size: 1.05rem;
}

.places-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2.5rem;
}

.place-card {
  padding: 0 !important;
  overflow: hidden;
  gap: 0 !important;
}

.place-card:hover {
  border-color: rgba(16, 185, 129, 0.3) !important;
}

.place-image {
  height: 220px;
  background-size: cover;
  background-position: center;
  position: relative;
  transition: transform 0.5s ease;
}

/* Beautiful pure CSS placeholder gradients representing the sights */
.castle-img {
  background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #93c5fd 100%);
}

.garden-img {
  background: linear-gradient(135deg, #064e3b 0%, #10b981 50%, #a7f3d0 100%);
}

.temple-img {
  background: linear-gradient(135deg, #78350f 0%, #d97706 50%, #fde68a 100%);
}

.place-tag {
  position: absolute;
  top: 1rem;
  left: 1rem;
  background: rgba(17, 24, 39, 0.6);
  backdrop-filter: blur(8px);
  color: white;
  padding: 0.35rem 0.85rem;
  border-radius: 2rem;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.place-content {
  padding: 1.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  flex: 1;
}

.place-content h3 {
  font-size: 1.2rem;
  font-weight: 700;
  color: #111827;
  line-height: 1.4;
}

.place-content p {
  font-size: 0.925rem;
  color: #4b5563;
  line-height: 1.6;
  flex: 1;
}

.place-meta {
  display: flex;
  justify-content: space-between;
  border-top: 1px solid #f3f4f6;
  padding-top: 1rem;
  margin-top: 0.5rem;
}

.meta-item {
  font-size: 0.825rem;
  color: #6b7280;
  font-weight: 600;
}
</style>