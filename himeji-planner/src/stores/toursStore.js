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
    const idx = myTours.value.findIndex((t) => t.id === updatedTour.id)
    if (idx !== -1) myTours.value[idx] = updatedTour

    const pidx = publicTours.value.findIndex((t) => t.id === updatedTour.id)
    if (updatedTour.visibility === 'public') {
      if (pidx !== -1) publicTours.value[pidx] = updatedTour
      else publicTours.value = [updatedTour, ...publicTours.value]
    } else if (pidx !== -1) {
      publicTours.value.splice(pidx, 1)
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

