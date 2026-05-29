<template>
  <div class="planner-container">
    <!-- Header -->
    <header class="planner-header">
      <span class="header-badge">🗺️ Advanced Route Optimizer</span>
      <h1>Planify Travel</h1>
      <p class="subtitle">Select the places you want to visit and let our optimizer compute the shortest closed-loop route for you.</p>
    </header>

    <!-- Error Alert -->
    <div v-if="friendlyError" class="alert-banner error-alert">
      <span class="alert-icon">⚠️</span>
      <div class="alert-content">
        <h3>Routing Error</h3>
        <p>{{ friendlyError }}</p>
      </div>
    </div>

    <!-- Main Workspace -->
    <div class="planner-content">
      <!-- Section 1: Selection -->
      <section class="planner-section selection-section">
        <div class="section-title-wrapper">
          <span class="section-num">1</span>
          <h2>Select Places</h2>
        </div>
        
        <div class="selection-card">
          <div class="input-group">
            <label for="placeSelector">Choose places to include in your tour</label>
            <div class="select-wrapper">
              <select 
                :key="availableUnselectedPlaces.length"
                id="placeSelector" 
                name="placeSelector" 
                @change="togglePlace(selectedPlace)" 
                v-model="selectedPlace"
                :disabled="loading"
              >
                <option value="" disabled>-- Choose a place to add --</option>
                <option 
                  v-for="place in availableUnselectedPlaces" 
                  :key="place.id" 
                  :value="place"
                >
                  {{ place.name }}
                </option>
              </select>
              <span class="select-chevron">▼</span>
            </div>
          </div>

          <div class="stops-container">
            <h3>Selected Stops ({{ selectedPlaceIds.length }})</h3>
            
            <p v-if="selectedPlaceIds.length === 0" class="empty-stops-text">
              No places selected yet. Select at least 2 places from the dropdown above to start.
            </p>
            
            <div v-else id="trip-log" class="stops-grid">
              <StopDetails 
                v-for="(place, index) in selectedPlaceIds" 
                :key="place.id" 
                :index="index" 
                :hasIndex="true" 
                :stop="place" 
                @delete="deleteFromTour(index)"
              />
            </div>
          </div>

          <!-- Max Distance Slider/Input for Hotel Clustering -->
          <div class="input-group max-distance-group">
            <div class="label-wrapper">
              <label for="maxDistance">Max Hotel-to-Stop Distance</label>
              <span class="max-distance-val">{{ maxDistance }} km</span>
            </div>
            <p class="input-desc">Maximum distance for round trips from selected hotels. Lower values create more hotel hubs.</p>
            <input 
              id="maxDistance" 
              type="range" 
              min="10" 
              max="500" 
              step="10" 
              v-model.number="maxDistance"
              :disabled="loading"
              class="slider"
            />
          </div>

          <div class="action-footer">
            <BaseButton 
              class="w-full text-center" 
              @click="handleGenerateTour" 
              :loading="loading" 
              :disabled="selectedPlaceIds.length < 2"
            >
              🚀 Generate Optimized Tour
            </BaseButton>
          </div>
        </div>
      </section>

      <!-- Section 2: Results -->
      <section class="planner-section result-section">
        <div class="section-title-wrapper">
          <span class="section-num">2</span>
          <h2>Your Optimized Tour</h2>
        </div>

        <div v-if="loading" class="result-placeholder loading-card">
          <div class="spinner-large"></div>
          <p>Calculating the most optimal route with Google OR-Tools...</p>
        </div>

        <div v-else-if="!activeTour" class="result-placeholder empty-result-card">
          <div class="placeholder-icon">🗺️</div>
          <p>Add places and click "Generate Optimized Tour" to calculate your route.</p>
        </div>

        <div v-else class="result-card">
          <div class="tour-summary-badge">
            <span class="badge-icon">⚡</span>
            <div class="badge-text">
              <span class="label">Total Distance</span>
              <span class="value">{{ activeTour.totalDistance.toFixed(2) }} km</span>
            </div>
          </div>

          <div class="map-wrapper-container">
            <TourMap :route="activeTour.route" />
          </div>

          <!-- Save Tour Form -->
          <div class="save-tour-form">
            <h3>Save Itinerary</h3>
            <p class="form-desc">Save this optimized tour to your profile for easy access later.</p>
            
            <div v-if="friendlySaveError" class="alert-banner error-alert-inline">
              <span class="alert-icon">⚠️</span>
              <p>{{ friendlySaveError }}</p>
            </div>

            <div class="save-inputs">
              <BaseInput
                id="tourName"
                v-model="tourName"
                label="Give your tour a name"
                placeholder="e.g. My Himeji Itinerary"
                :disabled="saving"
                required
              />
              <BaseButton 
                @click="handleSaveTour" 
                :loading="saving" 
                :disabled="!tourName.trim()"
                class="save-btn"
              >
                💾 Save Tour
              </BaseButton>
            </div>
          </div>

          <!-- Optimized Stops list -->
          <div class="optimized-route-list">
            <h3>Optimized Stops Sequence</h3>
            <p class="route-desc">Stops have been reordered for the shortest travel loop (returns to start).</p>
            <ul class="tour-timeline">
              <li 
                v-for="(stop, index) in activeTour.route" 
                :key="index" 
                :class="{ 'timeline-hotel': stop.is_hotel }"
                class="timeline-item"
              >
                <!-- Connecting Line -->
                <div v-if="index < activeTour.route.length - 1" class="timeline-line"></div>
                
                <!-- Dot Indicator -->
                <div class="timeline-dot-wrapper">
                  <span class="timeline-number">{{ index + 1 }}</span>
                </div>
                
                <!-- Card content -->
                <div class="timeline-card">
                  <div class="timeline-card-header">
                    <h4>{{ getPlaceName(stop) }}</h4>
                    <div class="badges">
                      <span v-if="stop.is_hotel" class="badge badge-hotel">🏨 Hotel</span>
                      <span v-if="stop.locked" class="badge badge-locked">🔒 Locked</span>
                    </div>
                  </div>
                  <p class="timeline-coords">
                    <span>Lat: {{ stop.latitude.toFixed(4) }}</span>
                    <span class="separator">|</span>
                    <span>Lng: {{ stop.longitude.toFixed(4) }}</span>
                  </p>
                  <p v-if="stop.is_hotel" class="hotel-desc">Round trips will branch from here</p>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'
import { placesApi } from '@/api/placesApi'
import client from '@/api/client'
import TourMap from '@/views/TourMap.vue'
import StopDetails from '@/components/planner/StopDetails.vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseInput from '@/components/BaseInput.vue'

const router = useRouter()
const authStore = useAuthStore()

const availablePlaces = ref([])
const loading = ref(false)
const saving = ref(false)
const error = ref(null)
const saveError = ref(null)

const selectedPlace = ref("")
const selectedPlaceIds = ref([])
const activeTour = ref(null)
const tourName = ref("")
const maxDistance = ref(100)

function getPlaceName(place) {
  return place.name?.split(', ')[0] || place.name || 'Unknown place'
}

// Load public and private places
const loadPlaces = async () => {
  loading.value = true
  error.value = null
  try {
    // 1. Load public places
    const publicReq = await placesApi.getPublicPlaces()
    const publicList = publicReq.data?.places ?? []
    
    // 2. Load private places (if authenticated)
    let privateList = []
    if (authStore.isAuthenticated) {
      try {
        const privateReq = await placesApi.getMyPlaces()
        privateList = privateReq.data?.places ?? []
      } catch (err) {
        console.error("Could not load private places:", err)
      }
    }
    
    // Combine list and make sure IDs are unique
    const merged = [...publicList]
    const seenIds = new Set(publicList.map(p => p.id))
    privateList.forEach(p => {
      if (!seenIds.has(p.id)) {
        merged.push(p)
      }
    })
    
    availablePlaces.value = merged
  } catch (err) {
    error.value = err
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadPlaces()
})

const availableUnselectedPlaces = computed(() => {
  if (!availablePlaces.value) return []
  return availablePlaces.value.filter(
    place => !selectedPlaceIds.value.some(sp => sp.id === place.id)
  )
})

function togglePlace(place) {
  if (!place || place === "") return
  
  const exists = selectedPlaceIds.value.some(p => p.id === place.id)
  if (!exists) {
    selectedPlaceIds.value.push(place)
  }
  
  // Reset selection
  selectedPlace.value = ""
}

function deleteFromTour(index) {
  selectedPlaceIds.value.splice(index, 1)
  // Clear computed tour to force recalculation
  activeTour.value = null
}

const friendlyError = computed(() => {
  if (!error.value) return null
  const messages = {
    NETWORK_ERROR: 'Unable to reach the API. Please check that the backend is running.',
    UNAUTHORIZED: 'Please log in again to manage tours.',
    VALIDATION_ERROR: 'Please select at least 2 distinct valid places.',
    FORBIDDEN: 'You do not have permission to access one or more selected places.',
    UNKNOWN_ERROR: 'Something went wrong. Please try again.'
  }
  return messages[error.value.code] || error.value.message || messages.UNKNOWN_ERROR
})

const friendlySaveError = computed(() => {
  if (!saveError.value) return null
  const messages = {
    NETWORK_ERROR: 'Unable to reach the API. Please check that the backend is running.',
    UNAUTHORIZED: 'Please log in again to save tours.',
    VALIDATION_ERROR: 'Please verify the tour name and selected places.',
    UNKNOWN_ERROR: 'Something went wrong. Please try again.'
  }
  return messages[saveError.value.code] || saveError.value.message || messages.UNKNOWN_ERROR
})

const handleGenerateTour = async () => {
  if (selectedPlaceIds.value.length < 2) return
  loading.value = true
  error.value = null
  activeTour.value = null

  try {
    const payload = {
      place_ids: selectedPlaceIds.value.map(p => p.id),
      max_distance: maxDistance.value
    }
    const response = await client.post('/tours/preview', payload)
    const tourData = response.data?.tour
    if (tourData) {
      activeTour.value = {
        totalDistance: tourData.total_distance,
        route: tourData.places
      }
      
      // Auto-suggest a default tour name based on number of stops
      const count = selectedPlaceIds.value.length
      tourName.value = `Tour of Himeji - ${count} Stops`
    }
  } catch (err) {
    error.value = err
  } finally {
    loading.value = false
  }
}

const handleSaveTour = async () => {
  if (selectedPlaceIds.value.length < 2 || !tourName.value.trim()) return
  saving.value = true
  saveError.value = null

  try {
    const payload = {
      name: tourName.value.trim(),
      place_ids: selectedPlaceIds.value.map(p => p.id),
      visibility: 'private',
      max_distance: maxDistance.value
    }
    await client.post('/tours', payload)
    
    // Redirect to Tours view
    router.push({ name: 'tours' })
  } catch (err) {
    saveError.value = err
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.planner-container {
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Header styling */
.planner-header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
}

.header-badge {
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.2);
  color: #4f46e5;
  padding: 0.4rem 0.8rem;
  border-radius: 2rem;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.planner-header h1 {
  font-size: 2.25rem;
  color: #111827;
  font-weight: 800;
  background: linear-gradient(135deg, #4f46e5, #2563eb);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: #6b7280;
  font-size: 1.05rem;
  max-width: 700px;
}

/* Main workspace layout */
.planner-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

@media (min-width: 1024px) {
  .planner-content {
    grid-template-columns: 1.1fr 0.9fr;
    align-items: start;
  }
}

.planner-section {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.section-title-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.section-num {
  background: #111827;
  color: white;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.9rem;
}

.section-title-wrapper h2 {
  font-size: 1.35rem;
  color: #111827;
  font-weight: 700;
}

/* Selection Card */
.selection-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 1.25rem;
  padding: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.input-group label {
  font-size: 0.9rem;
  font-weight: 600;
  color: #374151;
}

.select-wrapper {
  position: relative;
  width: 100%;
}

.select-wrapper select {
  width: 100%;
  padding: 0.8rem 1rem;
  border-radius: 0.75rem;
  border: 1.5px solid #e5e7eb;
  background: #f9fafb;
  color: #1f2937;
  font-size: 0.95rem;
  font-weight: 500;
  appearance: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.select-wrapper select:focus {
  outline: none;
  border-color: #4f46e5;
  background: #ffffff;
  box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.12);
}

.select-chevron {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #9ca3af;
  font-size: 0.75rem;
  pointer-events: none;
}

/* Stops container */
.stops-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  border-top: 1px solid #f3f4f6;
  padding-top: 1.5rem;
}

.stops-container h3 {
  font-size: 1rem;
  color: #111827;
  font-weight: 700;
}

.empty-stops-text {
  color: #9ca3af;
  font-size: 0.9rem;
  text-align: center;
  padding: 2.5rem 1.5rem;
  background: #f9fafb;
  border: 1.5px dashed #e5e7eb;
  border-radius: 1rem;
  line-height: 1.5;
}

.stops-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  max-height: 500px;
  overflow-y: auto;
  padding-right: 0.25rem;
}

@media (min-width: 640px) {
  .stops-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* Results section placeholder / cards */
.result-placeholder {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 1.25rem;
  padding: 3.5rem 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 1rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
  min-height: 350px;
}

.empty-result-card .placeholder-icon {
  font-size: 3.5rem;
  animation: float 4s ease-in-out infinite;
}

.empty-result-card p {
  color: #6b7280;
  font-size: 0.95rem;
  max-width: 300px;
  line-height: 1.5;
}

.loading-card p {
  color: #4b5563;
  font-size: 0.95rem;
  font-weight: 600;
}

.spinner-large {
  width: 48px;
  height: 48px;
  border: 4px solid rgba(99, 102, 241, 0.1);
  border-radius: 50%;
  border-top-color: #4f46e5;
  animation: spin 1s linear infinite;
}

/* Results Card */
.result-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 1.25rem;
  padding: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02);
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

.tour-summary-badge {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(37, 99, 235, 0.08));
  border: 1px solid rgba(99, 102, 241, 0.15);
  border-radius: 1rem;
  padding: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.badge-icon {
  font-size: 1.75rem;
  background: white;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.badge-text {
  display: flex;
  flex-direction: column;
}

.badge-text .label {
  font-size: 0.75rem;
  color: #6b7280;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge-text .value {
  font-size: 1.35rem;
  color: #4f46e5;
  font-weight: 800;
}

.map-wrapper-container {
  overflow: hidden;
  border-radius: 1rem;
}

/* Save Tour Form styling */
.save-tour-form {
  border-top: 1px solid #f3f4f6;
  border-bottom: 1px solid #f3f4f6;
  padding: 1.5rem 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.save-tour-form h3 {
  font-size: 1rem;
  color: #111827;
  font-weight: 700;
}

.form-desc {
  font-size: 0.85rem;
  color: #6b7280;
}

.save-inputs {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  align-items: stretch;
}

@media (min-width: 640px) {
  .save-inputs {
    flex-direction: row;
    align-items: flex-end;
  }
  
  .save-inputs :deep(.form-group) {
    flex: 1;
  }
}

.save-btn {
  flex-shrink: 0;
}

/* Optimized Route sequence */
.optimized-route-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.optimized-route-list h3 {
  font-size: 1rem;
  color: #111827;
  font-weight: 700;
}

.route-desc {
  font-size: 0.85rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.tour-route {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  max-height: 450px;
  overflow-y: auto;
}

/* Max distance slider */
.max-distance-group {
  border-top: 1px solid #f3f4f6;
  padding-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.label-wrapper {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.max-distance-val {
  font-size: 0.95rem;
  font-weight: 800;
  color: #4f46e5;
  background: rgba(99, 102, 241, 0.08);
  padding: 0.2rem 0.6rem;
  border-radius: 0.5rem;
}

.input-desc {
  font-size: 0.8rem;
  color: #6b7280;
  line-height: 1.4;
}

.slider {
  width: 100%;
  height: 6px;
  background: #e5e7eb;
  border-radius: 3px;
  outline: none;
  appearance: none;
  cursor: pointer;
  transition: all 0.2s;
}

.slider:focus {
  background: #cbd5e1;
}

.slider::-webkit-slider-thumb {
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #4f46e5;
  border: 2px solid white;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  transition: transform 0.1s;
}

.slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
}

/* Custom Timeline for optimized stops */
.tour-timeline {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.timeline-item {
  display: flex;
  gap: 1.25rem;
  position: relative;
  align-items: flex-start;
}

.timeline-line {
  position: absolute;
  left: 17px;
  top: 36px;
  bottom: -24px;
  width: 2px;
  background-color: #cbd5e1;
  z-index: 1;
}

.timeline-dot-wrapper {
  position: relative;
  z-index: 2;
}

.timeline-number {
  background-color: #111827;
  color: white;
  width: 2.25rem;
  height: 2.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-weight: 700;
  font-size: 0.9rem;
  border: 3px solid white;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  transition: all 0.3s;
}

.timeline-hotel .timeline-number {
  background: linear-gradient(135deg, #4f46e5, #2563eb);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
}

.timeline-card {
  flex: 1;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  transition: all 0.2s ease;
}

.timeline-card:hover {
  border-color: #cbd5e1;
  background: #f3f4f6;
}

.timeline-hotel .timeline-card {
  background: rgba(99, 102, 241, 0.02);
  border-color: rgba(99, 102, 241, 0.15);
}

.timeline-hotel .timeline-card:hover {
  background: rgba(99, 102, 241, 0.04);
  border-color: rgba(99, 102, 241, 0.3);
}

.timeline-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  flex-wrap: wrap;
}

.timeline-card h4 {
  margin: 0;
  font-size: 1rem;
  color: #1f2937;
  font-weight: 700;
}

.badges {
  display: flex;
  gap: 0.35rem;
}

.badge {
  font-size: 0.7rem;
  font-weight: 800;
  padding: 0.15rem 0.45rem;
  border-radius: 999px;
  text-transform: uppercase;
}

.badge-hotel {
  background-color: #e0e7ff;
  color: #4338ca;
}

.badge-locked {
  background-color: #fef3c7;
  color: #92400e;
}

.timeline-coords {
  margin: 0;
  font-size: 0.8rem;
  color: #6b7280;
  display: flex;
  gap: 0.5rem;
}

.separator {
  color: #d1d5db;
}

.hotel-desc {
  margin: 0.25rem 0 0 0;
  font-size: 0.75rem;
  color: #4f46e5;
  font-weight: 600;
}

/* Alerts styling */
.alert-banner {
  padding: 1rem 1.25rem;
  border-radius: 0.75rem;
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  box-sizing: border-box;
}

.error-alert {
  border: 1px solid #fecaca;
  background: #fef2f2;
  color: #b91c1c;
}

.error-alert h3 {
  font-size: 0.95rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.error-alert p {
  font-size: 0.875rem;
  line-height: 1.4;
}

.error-alert-inline {
  border: 1px solid #fecaca;
  background: #fef2f2;
  color: #b91c1c;
  padding: 0.6rem 0.8rem;
  border-radius: 0.5rem;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.w-full {
  width: 100%;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>