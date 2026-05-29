// src/stores/placesStore.js
import { ref } from 'vue'
import { defineStore } from 'pinia'

export const usePlacesStore = defineStore('places', () => {
  const places = ref([])
  const loading = ref(false)
  const error = ref(null)

  function setPlaces(newPlaces) {
    places.value = newPlaces ?? []
  }

  function mergePlaces(newPlaces) {
    const placeById = new Map()

    for (const place of [...places.value, ...(newPlaces ?? [])]) {
      if (place?.id) {
        placeById.set(place.id, place)
      }
    }

    places.value = Array.from(placeById.values())
  }

  function addPlace(place) {
    if (place) {
      places.value = [place, ...places.value]
    }
  }

  function removePlace(placeId) {
    places.value = places.value.filter((place) => place.id !== placeId)
  }

  function updatePlace(updatedPlace) {
    if (updatedPlace?.id) {
      const index = places.value.findIndex((p) => p.id === updatedPlace.id)
      if (index !== -1) {
        places.value[index] = updatedPlace
      }
    }
  }

  function setError(err) {
    error.value = err ?? null
  }

  function clearError() {
    error.value = null
  }

  return { places, loading, error, setPlaces, mergePlaces, addPlace, updatePlace, removePlace, setError, clearError }
})
