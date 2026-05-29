import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useToursStore = defineStore('tours', () => {
  const publicTours = ref([])
  const myTours = ref([])
  const loading = ref(false)
  const error = ref(null)

  function setPublicTours(tours) {
    publicTours.value = tours ?? []
  }

  function setMyTours(tours) {
    myTours.value = tours ?? []
  }

  function addTour(tour) {
    if (!tour) return

    myTours.value = [tour, ...myTours.value]

    if (tour.visibility === 'public') {
      publicTours.value = [tour, ...publicTours.value]
    }
  }

  function updateTour(updatedTour) {
    if (!updatedTour) return

    // Replace the whole array so Vue's ref-level reactivity triggers reliably
    myTours.value = myTours.value.map((t) => (t.id === updatedTour.id ? updatedTour : t))

    if (updatedTour.visibility === 'public') {
      const exists = publicTours.value.some((t) => t.id === updatedTour.id)
      if (exists) {
        publicTours.value = publicTours.value.map((t) => (t.id === updatedTour.id ? updatedTour : t))
      } else {
        publicTours.value = [updatedTour, ...publicTours.value]
      }
    } else {
      // Removed from public or was never there
      publicTours.value = publicTours.value.filter((t) => t.id !== updatedTour.id)
    }
  }

  function setError(err) {
    error.value = err ?? null
  }

  function clearError() {
    error.value = null
  }

  return {
    publicTours,
    myTours,
    loading,
    error,
    setPublicTours,
    setMyTours,
    addTour,
    updateTour,
    setError,
    clearError
  }
})

