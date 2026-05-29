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
          <select id="placeSelector" name="placeSelector" @change="togglePlace(selectedPlace)" v-model="selectedPlace">
            <option value="0" selected disabled>-- Choose a place to add --</option>
            <option v-for="place in availableUnselectedPlaces" :key="place.id" class="place-info" :value="place" v-if="!(place in selectedPlaceIds)">
              <strong>{{ place.name }}</strong>
            </option>
          </select>
        </div>
        <div id="trip-log">
          <StopDetails 
            v-for="(place, index) in selectedPlaceIds" 
            :key="place.id" 
            :index="index" 
            :hasIndex="true" 
            :stop="place" 
            @delete="deleteFromTour(index)"/>
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
          <StopDetails v-for="(stop, index) in activeTour.route" :key="index" :id="'tourStop'+index" hasIndex="true" :index="index" :stop="stop"/>
        </ul>

        <button>Save my travel</button>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import TourMap from '@/views/TourMap.vue'
import { placesApi } from '../api/placesApi'
import StopDetails from '@/components/planner/StopDetails.vue'

const availablePlaces = ref()
async function placesFunction() {
  const placesReq = await placesApi.getPublicPlaces()
  availablePlaces.value = placesReq.data.places
}

onMounted(async () => {
        await placesFunction();
})

const loading = ref(false)
const error = ref(null)
const selectedPlaceIds = ref([])
const activeTour = ref(null)

const availableUnselectedPlaces = computed(() => {
  if (!availablePlaces.value) return []
  return availablePlaces.value.filter(
    place => !selectedPlaceIds.value.some(sp => sp.id === place.id)
  )
})

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

function togglePlace(placeInfos) {
  if(placeInfos["id"] in selectedPlaceIds.value) {
    selectedPlaceIds.value = selectedPlaceIds.value.filter((value) => value["id"] != placeInfos["id"])
  } else {
    selectedPlaceIds.value.push(placeInfos)
  }
  document.getElementById("placeSelector").selectedIndex = 1;
}

function deleteFromTour(id) {
  selectedPlaceIds.value.splice(id, 1)
}
</script>

<style scoped>
#trip-log {
  display:grid;
  grid-template-columns: repeat(3, 1fr);
}

#placeSelector {
  margin-bottom:20px;
  padding: 5px 10px;
  border-radius: 25px;
  border: 1px lightgray solid;
}

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
</style>