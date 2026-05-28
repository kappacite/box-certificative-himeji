<template>
  <div class="planner-container">
    <header class="planner-header">
      <h1>Route Planner 🗺️</h1>
      <p>Select the places you want to visit and generate an optimized tour based on the shortest total distance.</p>
    </header>

    <div v-if="error" class="temp-error-banner">
      {{ error.message }}
    </div>

    <div class="planner-content">
      <section class="selection-section">
        <h2>1. Select Places</h2>
        <div class="places-list">
          <label v-for="place in availablePlaces" :key="place.id" class="place-item">
            <input type="checkbox" :value="place.id" v-model="selectedPlaceIds" />
            <div class="place-info">
              <strong>{{ place.name }}</strong>
              <span class="coordinates">Lat: {{ place.latitude }} | Lng: {{ place.longitude }}</span>
            </div>
          </label>
        </div>

        <button @click="handleGenerateTour" :disabled="loading || selectedPlaceIds.length < 2" class="generate-btn">
          <span v-if="loading">⏳ Generating optimal route...</span>
          <span v-else>🚀 Generate Optimized Tour</span>
        </button>
      </section>

      <section v-if="activeTour && !loading" class="result-section">
        <h2>2. Your Optimized Tour</h2>
        
        <div class="tour-summary">
          <p class="distance-metric">
            Total Distance: <strong>{{ activeTour.totalDistance }} km</strong>
          </p>
        </div>

        <div class="map-section">
          <TourMap :route="activeTour.route" />
        </div>

        <ul class="tour-route">
          <li v-for="(stop, index) in activeTour.route" :key="index" class="route-stop">
            <div class="stop-indicator">
              <span class="stop-number">{{ index + 1 }}</span>
            </div>
            <div class="stop-details">
              <h3>{{ stop.name }}</h3>
              <p>Lat: {{ stop.latitude }} | Lng: {{ stop.longitude }}</p>
            </div>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import TourMap from '@/views/TourMap.vue'

// ... [Garder toute la logique JavaScript / Mock data précédente] ...
const availablePlaces = ref([
  { id: 1, name: 'Himeji Castle', latitude: 34.8394, longitude: 134.6939 },
  { id: 2, name: 'Koko-en Garden', latitude: 34.8373, longitude: 134.6888 },
  { id: 3, name: 'Mount Shosha', latitude: 34.8912, longitude: 134.6558 }
])

const loading = ref(false)
const error = ref(null)
const selectedPlaceIds = ref([])
const activeTour = ref(null)

const handleGenerateTour = () => {
  if (selectedPlaceIds.value.length < 2) return
  loading.value = true
  error.value = null
  activeTour.value = null

  setTimeout(() => {
    loading.value = false
    activeTour.value = {
      totalDistance: 12.4,
      route: availablePlaces.value.filter(p => selectedPlaceIds.value.includes(p.id))
    }
  }, 1500)
}
</script>

<style scoped>
/* ... [Garder les styles précédents] ... */

/* --- NOUVEAUX STYLES POUR LA TIMELINE --- */
.map-section {
  margin-bottom: 2rem;
}

.tour-route {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
}

.route-stop {
  display: flex;
  align-items: flex-start; /* Align top so the line starts exactly at the circle */
  gap: 1rem;
  position: relative;
  padding-bottom: 1.5rem; /* Space between the stops */
}

/* The vertical line connecting the dots */
.route-stop:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 2rem; /* Start just below the number circle */
  left: 1rem; /* Center of the 2rem circle */
  width: 2px;
  height: calc(100% - 2rem); /* Stretch to the bottom of the padding */
  background-color: #cbd5e1; /* Light gray line */
  transform: translateX(-50%);
  z-index: 0;
}

.stop-indicator {
  position: relative;
  z-index: 1; /* Keep the circle above the line */
}

.stop-number {
  background-color: #111827;
  color: white;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-weight: bold;
}

.stop-details {
  padding-top: 0.25rem; /* Vertically align text with the circle */
}

.stop-details h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #1f2937;
  font-weight: 700;
}

.stop-details p {
  margin: 0;
  font-size: 0.85rem;
  color: #6b7280;
}
</style>