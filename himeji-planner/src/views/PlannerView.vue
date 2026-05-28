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
        <div v-if="availablePlaces.length === 0" class="empty-state">
          No places available. Please add places first.
        </div>
        
        <div v-else class="places-list">
          <label 
            v-for="place in availablePlaces" 
            :key="place.id" 
            class="place-item"
          >
            <input
              type="checkbox"
              :value="place.id"
              v-model="selectedPlaceIds"
            />
            <div class="place-info">
              <strong>{{ place.name }}</strong>
              <span class="coordinates">Lat: {{ place.latitude }} | Lng: {{ place.longitude }}</span>
            </div>
          </label>
        </div>

        <button
          @click="handleGenerateTour"
          :disabled="loading || selectedPlaceIds.length < 2"
          class="generate-btn"
        >
          <span v-if="loading">⏳ Generating optimal route...</span>
          <span v-else>🚀 Generate Optimized Tour</span>
        </button>
        <p v-if="selectedPlaceIds.length < 2" class="help-text">
          * Please select at least 2 places to generate a tour.
        </p>
      </section>

      <section v-if="activeTour && !loading" class="result-section">
        <h2>2. Your Optimized Tour</h2>
        
        <div class="tour-summary">
          <p class="distance-metric">
            Total Distance: <strong>{{ activeTour.totalDistance }} km</strong>
          </p>
        </div>

        <ul class="tour-route">
          <li v-for="(stop, index) in activeTour.route" :key="index" class="route-stop">
            <span class="stop-number">{{ index + 1 }}</span>
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

/* =========================================================================
   VRAIE LOGIQUE API (EN ATTENTE)
   Décommentez ces lignes une fois le backend et les composables prêts.
   =========================================================================
import { usePlacesStore } from '@/stores/placesStore'
import { useTours } from '@/composables/useTours'
import AlertBanner from '@/components/ui/AlertBanner.vue'

const placesStore = usePlacesStore()
const { generateTour, loading, error } = useTours()
const availablePlaces = computed(() => placesStore.places)
*/

// =========================================================================
// DONNÉES FACTICES POUR LA VISUALISATION (MOCK)
// À supprimer une fois la vraie logique décommentée.
// =========================================================================

// 1. Faux lieux pour tester la sélection
const availablePlaces = ref([
  { id: 1, name: 'Himeji Castle', latitude: 34.8394, longitude: 134.6939 },
  { id: 2, name: 'Koko-en Garden', latitude: 34.8373, longitude: 134.6888 },
  { id: 3, name: 'Mount Shosha', latitude: 34.8912, longitude: 134.6558 }
])

// 2. Faux états pour remplacer le composable useTours()
const loading = ref(false)
const error = ref(null)
const selectedPlaceIds = ref([])
const activeTour = ref(null)

// 3. Fausse action pour simuler le comportement du bouton
const handleGenerateTour = () => {
  if (selectedPlaceIds.value.length < 2) return

  loading.value = true
  error.value = null
  activeTour.value = null

  // Simulation d'un délai réseau de 1.5 secondes
  setTimeout(() => {
    loading.value = false
    
    // Faux résultat généré pour tester l'affichage de la section 2
    activeTour.value = {
      totalDistance: 12.4, // Distance factice
      route: availablePlaces.value.filter(p => selectedPlaceIds.value.includes(p.id))
    }
  }, 1500)
}
</script>

<style scoped>
/* Les styles restent identiques, j'ai juste ajouté une classe temporaire pour l'erreur */
.planner-container {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  padding: 1rem 0;
}

.planner-header h1 {
  font-size: 2.25rem;
  color: #111827;
  font-weight: 800;
  margin-bottom: 0.5rem;
}

.planner-header p {
  color: #6b7280;
  font-size: 1.05rem;
}

.planner-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

@media (min-width: 768px) {
  .planner-content {
    grid-template-columns: 1fr 1fr;
  }
}

.selection-section, .result-section {
  background: #ffffff;
  padding: 1.5rem;
  border-radius: 1rem;
  border: 1px solid #e5e7eb;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

h2 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 1.25rem;
  border-bottom: 2px solid #f3f4f6;
  padding-bottom: 0.5rem;
}

.places-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.place-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.place-item:hover {
  background-color: #f9fafb;
}

.place-info {
  display: flex;
  flex-direction: column;
}

.coordinates {
  font-size: 0.75rem;
  color: #9ca3af;
  font-family: monospace;
}

.generate-btn {
  width: 100%;
  padding: 0.75rem;
  background-color: #2563eb;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.generate-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}

.generate-btn:hover:not(:disabled) {
  background-color: #1d4ed8;
}

.help-text {
  font-size: 0.8rem;
  color: #6b7280;
  margin-top: 0.5rem;
  text-align: center;
}

.tour-summary {
  background-color: #ecfdf5;
  border: 1px solid #10b981;
  padding: 1rem;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
}

.distance-metric {
  color: #065f46;
  font-size: 1.1rem;
}

.tour-route {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.route-stop {
  display: flex;
  align-items: center;
  gap: 1rem;
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

.stop-details h3 {
  margin: 0;
  font-size: 1rem;
  color: #1f2937;
}

.stop-details p {
  margin: 0;
  font-size: 0.8rem;
  color: #6b7280;
}

/* Style temporaire pour remplacer le AlertBanner */
.temp-error-banner {
  background-color: #fee2e2;
  color: #991b1b;
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #f87171;
}
</style>