<template>
  <div class="tours-container">
    <header class="tours-header">
      <div>
        <h1>Published Tours</h1>
        <p class="subtitle">Browse public itineraries shared by travelers and review your private routes when signed in.</p>
      </div>
    </header>

    <div v-if="error" class="error-message">
      {{ friendlyErrorMessage }}
    </div>

    <div v-if="loading && publicTours.length === 0" class="loading-state">
      Loading tours...
    </div>

    <section v-if="isAuthenticated" class="tour-section">
      <div class="section-header">
        <h2>My Private Tours</h2>
        <span class="section-count">{{ privateTours.length }}</span>
      </div>

      <div v-if="privateTours.length > 0" class="tours-grid">
        <BaseCard 
          v-for="tour in privateTours" 
          :key="tour.id" 
          class="tour-card interactive-card"
          hoverable
          @click="selectTour(tour)"
        >
          <div class="tour-card-header">
            <h3>{{ tour.name }}</h3>
            <span class="visibility-badge private">Private</span>
          </div>
          <p class="tour-distance">
            <span>{{ formatDistance(tour.total_distance) }}</span>
            <span v-if="tour.max_distance" class="tour-max-dist-badge">Max Hotel: {{ tour.max_distance }} km</span>
          </p>
          <div class="places-preview-container">
            <ol class="places-preview">
              <li v-for="place in visiblePlaces(tour)" :key="place.id">
                {{ getPlaceName(place) }}
                <span v-if="place.is_hotel" class="badge-hotel-inline">🏨 Hotel</span>
              </li>
            </ol>
            <button 
              v-if="tour.places && tour.places.length > 10" 
              class="expand-button" 
              @click.stop="toggleExpand(tour.id)"
            >
              {{ isExpanded(tour.id) ? 'Show less ▴' : `... View more (${tour.places.length - 10} more) ▾` }}
            </button>
          </div>
          <span class="click-hint">Click to view route map →</span>
        </BaseCard>
      </div>

      <p v-else class="empty-state">
        You do not have private tours yet.
      </p>
    </section>

    <section class="tour-section">
      <div class="section-header">
        <h2>Public Tours</h2>
        <span class="section-count">{{ publicTours.length }}</span>
      </div>

      <div v-if="publicTours.length > 0" class="tours-grid">
        <BaseCard 
          v-for="tour in publicTours" 
          :key="tour.id" 
          class="tour-card interactive-card"
          hoverable
          @click="selectTour(tour)"
        >
          <div class="tour-card-header">
            <h3>{{ tour.name }}</h3>
            <span class="visibility-badge public">Public</span>
          </div>
          <p class="tour-distance">
            <span>{{ formatDistance(tour.total_distance) }}</span>
            <span v-if="tour.max_distance" class="tour-max-dist-badge">Max Hotel: {{ tour.max_distance }} km</span>
          </p>
          <div class="places-preview-container">
            <ol class="places-preview">
              <li v-for="place in visiblePlaces(tour)" :key="place.id">
                {{ getPlaceName(place) }}
                <span v-if="place.is_hotel" class="badge-hotel-inline">🏨 Hotel</span>
              </li>
            </ol>
            <button 
              v-if="tour.places && tour.places.length > 10" 
              class="expand-button" 
              @click.stop="toggleExpand(tour.id)"
            >
              {{ isExpanded(tour.id) ? 'Show less ▴' : `... View more (${tour.places.length - 10} more) ▾` }}
            </button>
          </div>
          <span class="click-hint">Click to view route map →</span>
        </BaseCard>
      </div>

      <p v-else-if="!loading" class="empty-state">
        No public tours have been published yet.
      </p>
    </section>

    <!-- Tour Details Modal -->
    <TourDetailsModal 
      v-if="selectedTour" 
      :tour="selectedTour" 
      @close="selectedTour = null" 
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useTours } from '@/composables/useTours'
import BaseCard from '@/components/BaseCard.vue'
import TourDetailsModal from '@/components/tours/TourDetailsModal.vue'

const authStore = useAuthStore()
const { publicTours, privateTours, loading, error, loadPublicTours, loadMyTours } = useTours()

const selectedTour = ref(null)
const expandedTours = ref({})

const isAuthenticated = computed(() => authStore.isAuthenticated)
const friendlyErrorMessage = computed(() => {
  const messages = {
    NETWORK_ERROR: 'Unable to reach the API. Please check that the backend is running.',
    UNAUTHORIZED: 'Please log in again to see your private tours.',
    UNKNOWN_ERROR: 'Unable to load tours. Please try again.'
  }

  return error.value?.message || messages[error.value?.code] || messages.UNKNOWN_ERROR
})

function selectTour(tour) {
  selectedTour.value = tour
}

function formatDistance(distance) {
  const value = Number(distance)
  return Number.isFinite(value) ? `${value.toFixed(2)} km` : 'Distance unavailable'
}

function getPlaceName(place) {
  return place.name?.split(', ')[0] || place.name || 'Unknown place'
}

function toggleExpand(tourId) {
  expandedTours.value[tourId] = !expandedTours.value[tourId]
}

function isExpanded(tourId) {
  return !!expandedTours.value[tourId]
}

function visiblePlaces(tour) {
  if (!tour.places) return []
  if (tour.places.length <= 10 || isExpanded(tour.id)) {
    return tour.places
  }
  return tour.places.slice(0, 10)
}

onMounted(async () => {
  await loadPublicTours()

  if (authStore.isAuthenticated) {
    await loadMyTours()
  }
})
</script>

<style scoped>
.tours-container {
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.tours-header h1 {
  font-size: 2.25rem;
  color: #111827;
  font-weight: 800;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #1d4ed8, #0891b2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: #6b7280;
  font-size: 1.05rem;
}

.tour-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.section-header h2 {
  color: #111827;
  font-size: 1.35rem;
}

.section-count {
  min-width: 2rem;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  background: #e0f2fe;
  color: #0369a1;
  font-size: 0.8rem;
  font-weight: 800;
  text-align: center;
}

.tours-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}

.tour-card {
  padding: 1.5rem !important;
}

.interactive-card {
  cursor: pointer;
  position: relative;
  padding-bottom: 2.75rem !important;
}

.interactive-card:hover {
  border-color: #3b82f6;
}

.click-hint {
  position: absolute;
  bottom: 1rem;
  right: 1.5rem;
  font-size: 0.8rem;
  font-weight: 700;
  color: #3b82f6;
  opacity: 0;
  transform: translateX(-5px);
  transition: all 0.25s ease;
}

.interactive-card:hover .click-hint {
  opacity: 1;
  transform: translateX(0);
}

.tour-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.tour-card h3 {
  color: #111827;
  font-size: 1.1rem;
  line-height: 1.35;
}

.visibility-badge {
  flex-shrink: 0;
  padding: 0.25rem 0.55rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 800;
}

.visibility-badge.public {
  background: #ecfdf5;
  color: #047857;
}

.visibility-badge.private {
  background: #fef3c7;
  color: #92400e;
}

.tour-distance {
  color: #2563eb;
  font-size: 1rem;
  font-weight: 800;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tour-max-dist-badge {
  font-size: 0.75rem;
  background-color: rgba(99, 102, 241, 0.08);
  color: #4f46e5;
  padding: 0.15rem 0.45rem;
  border-radius: 0.5rem;
  font-weight: 700;
}

.places-preview-container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.places-preview {
  margin: 0;
  padding-left: 1.25rem;
  color: #4b5563;
  line-height: 1.7;
}

.badge-hotel-inline {
  background-color: #e0e7ff;
  color: #4338ca;
  font-size: 0.65rem;
  font-weight: 800;
  padding: 0.05rem 0.35rem;
  border-radius: 999px;
  text-transform: uppercase;
  margin-left: 0.4rem;
  display: inline-block;
  vertical-align: middle;
}

.expand-button {
  background: transparent;
  border: none;
  color: #2563eb;
  font-size: 0.8rem;
  font-weight: 700;
  cursor: pointer;
  align-self: flex-start;
  padding: 0.2rem 0.4rem;
  border-radius: 0.25rem;
  transition: background-color 0.2s, color 0.2s;
  z-index: 2;
}

.expand-button:hover {
  background-color: rgba(37, 99, 235, 0.08);
  color: #1d4ed8;
}

.loading-state,
.empty-state,
.error-message {
  padding: 1rem 1.25rem;
  border-radius: 0.75rem;
  font-size: 0.95rem;
  font-weight: 600;
}

.loading-state,
.empty-state {
  background: rgba(243, 244, 246, 0.8);
  color: #4b5563;
}

.error-message {
  border: 1px solid #fecaca;
  background: #fef2f2;
  color: #b91c1c;
}
</style>
