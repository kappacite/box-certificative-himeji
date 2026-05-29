<template>
  <div class="places-container">
    <header class="places-header">
      <div>
        <h1>Explore Popular Landmarks</h1>
        <p class="subtitle">A curated selection of must-see attractions to include in your customized travel itineraries.</p>
      </div>

      <BaseButton v-if="isAuthenticated" type="button" @click="openCreatePlace">
        Add place
      </BaseButton>
    </header>

    <div v-if="error && !selectedPlace && !isCreatePlaceOpen" class="error-message">
      {{ friendlyErrorMessage }}
    </div>

    <div v-if="loading && places.length === 0" class="loading-state">
      Loading places...
    </div>

    <p v-else-if="places.length === 0" class="empty-state">
      No places are available yet.
    </p>

    <section v-if="isAuthenticated && myPlaces.length > 0" class="places-section">
      <div class="section-header">
        <h2>My Places</h2>
        <span class="section-count">{{ myPlaces.length }}</span>
      </div>

      <div class="places-grid">
        <PlaceCard
          v-for="place in myPlaces"
          :key="place.id"
          :name="getPlaceName(place)"
          :latitude="place.latitude"
          :longitude="place.longitude"
          :city="getPlaceCity(place)"
          @select="openPlaceDetails(place)"
        />
      </div>
    </section>

    <section v-if="otherPublicPlaces.length > 0" class="places-section">
      <div class="section-header">
        <h2>Public Places</h2>
        <span class="section-count">{{ otherPublicPlaces.length }}</span>
      </div>

      <div class="places-grid">
        <PlaceCard
          v-for="place in otherPublicPlaces"
          :key="place.id"
          :name="getPlaceName(place)"
          :latitude="place.latitude"
          :longitude="place.longitude"
          :city="getPlaceCity(place)"
          @select="openPlaceDetails(place)"
        />
      </div>
    </section>

    <PlaceDetailsModal
      :place="selectedPlace"
      :can-edit="canManagePlace"
      :can-delete="canManagePlace"
      :loading="loading"
      :error="error"
      @close="closePlaceDetails"
      @edit="handleOpenEditPlace"
      @delete="handleDeletePlace"
    />

    <PlaceCreateModal
      :open="isCreatePlaceOpen"
      :loading="loading"
      :error="error"
      @close="closeCreatePlace"
      @create="handleCreatePlace"
    />

    <PlaceEditModal
      :open="isEditPlaceOpen"
      :place="placeToEdit"
      :loading="loading"
      :error="error"
      @close="handleCloseEditPlace"
      @update="handleUpdatePlace"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { usePlaces } from '@/composables/usePlaces'
import BaseButton from '@/components/BaseButton.vue'
import PlaceCard from '@/components/places/PlaceCard.vue'
import PlaceCreateModal from '@/components/places/PlaceCreateModal.vue'
import PlaceDetailsModal from '@/components/places/PlaceDetailsModal.vue'
import PlaceEditModal from '@/components/places/PlaceEditModal.vue'

const authStore = useAuthStore()
const { places, loading, error, loadVisiblePlaces, createPlace, updatePlace, deletePlace } = usePlaces()

const selectedPlace = ref(null)
const isCreatePlaceOpen = ref(false)
const isEditPlaceOpen = ref(false)
const placeToEdit = ref(null)

const isAuthenticated = computed(() => authStore.isAuthenticated)
const currentUserId = computed(() => authStore.user?.id ?? null)
const myPlaces = computed(() => places.value.filter((place) => place.owner_id === currentUserId.value))
const otherPublicPlaces = computed(() => places.value.filter((place) => place.visibility === 'public' && place.owner_id !== currentUserId.value))
const friendlyErrorMessage = computed(() => getFriendlyErrorMessage(error.value?.code))

const canManagePlace = computed(() => {
  if (!isAuthenticated.value || !selectedPlace.value) return false
  return selectedPlace.value.owner_id === authStore.user?.id
})

function getPlaceName(place) {
  return place.name?.split(', ')[0] || 'Unknown place'
}

function getPlaceCity(place) {
  return place.name?.split(', ')[1] || 'Not specified'
}

function openPlaceDetails(place) {
  selectedPlace.value = place
}

function closePlaceDetails() {
  selectedPlace.value = null
}

function openCreatePlace() {
  isCreatePlaceOpen.value = true
}

function closeCreatePlace() {
  isCreatePlaceOpen.value = false
}

async function handleCreatePlace(placeData) {
  const createdPlace = await createPlace(placeData)

  if (createdPlace) {
    closeCreatePlace()
  }
}

async function handleDeletePlace(placeId) {
  const deleted = await deletePlace(placeId)

  if (deleted) {
    closePlaceDetails()
  }
}

function handleOpenEditPlace(place) {
  placeToEdit.value = place
  isEditPlaceOpen.value = true
  closePlaceDetails()
}

function handleCloseEditPlace() {
  isEditPlaceOpen.value = false
  placeToEdit.value = null
}

async function handleUpdatePlace(placeId, placeData) {
  const updated = await updatePlace(placeId, placeData)

  if (updated) {
    handleCloseEditPlace()
  }
}

function getFriendlyErrorMessage(code) {
  const messages = {
    FORBIDDEN: 'You do not have permission to manage this place.',
    NOT_FOUND: 'This place no longer exists.',
    UNAUTHORIZED: 'Please log in again before managing this place.',
    VALIDATION_ERROR: 'Please check the place information.',
    UNKNOWN_ERROR: 'Unable to load places. Please try again.'
  }

  return messages[code] || messages.UNKNOWN_ERROR
}

onMounted(async () => {
  await loadVisiblePlaces(authStore.isAuthenticated)
})
</script>

<style scoped>
.places-container {
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.places-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
}

.places-header > div {
  flex: 1;
  min-width: 0;
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

.places-header :deep(.base-btn) {
  flex-shrink: 0;
  margin-left: auto;
}

@media (max-width: 640px) {
  .places-header {
    flex-direction: column;
  }

  .places-header :deep(.base-btn) {
    align-self: flex-end;
  }
}

.places-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 1.5rem;
}

.places-section {
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
  font-size: 1.3rem;
}

.section-count {
  min-width: 2rem;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  background: #dcfce7;
  color: #047857;
  font-size: 0.8rem;
  font-weight: 800;
  text-align: center;
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

.place-card {
  overflow: hidden;
  gap: 0 !important;
}

.place-card:hover {
  border-color: rgba(16, 185, 129, 0.3) !important;
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
