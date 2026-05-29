import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { toursApi } from '@/api/toursApi'
import { useToursStore } from '@/stores/toursStore'

export function useTours() {
  const toursStore = useToursStore()
  const { publicTours, myTours, loading, error } = storeToRefs(toursStore)

  const privateTours = computed(() => myTours.value.filter((tour) => tour.visibility === 'private'))

  async function loadPublicTours() {
    toursStore.clearError()
    toursStore.loading = true

    try {
      const response = await toursApi.getPublicTours()
      toursStore.setPublicTours(response.data?.tours ?? [])
    } catch (err) {
      toursStore.setError(err)
    } finally {
      toursStore.loading = false
    }
  }

  async function loadMyTours() {
    toursStore.clearError()
    toursStore.loading = true

    try {
      const response = await toursApi.getMyTours()
      toursStore.setMyTours(response.data?.tours ?? [])
    } catch (err) {
      toursStore.setError(err)
    } finally {
      toursStore.loading = false
    }
  }

  async function createTour(tourData) {
    toursStore.clearError()
    toursStore.loading = true

    try {
      const response = await toursApi.generateTour(tourData)
      const tour = response.data?.tour
      toursStore.addTour(tour)
      return tour
    } catch (err) {
      toursStore.setError(err)
      return null
    } finally {
      toursStore.loading = false
    }
  }

  async function patchTour(tourId, data) {
    toursStore.clearError()
    toursStore.loading = true

    try {
      const response = await toursApi.updateTour(tourId, data)
      const tour = response.data?.tour
      toursStore.updateTour(tour)
      return tour
    } catch (err) {
      toursStore.setError(err)
      return null
    } finally {
      toursStore.loading = false
    }
  }

  async function optimizeTour(data) {
    toursStore.clearError()
    toursStore.loading = true

    try {
      const response = await toursApi.optimizeTour(data)
      return response.data
    } catch (err) {
      toursStore.setError(err)
      return null
    } finally {
      toursStore.loading = false
    }
  }

  async function deleteTour(tourId) {
    toursStore.clearError()
    toursStore.loading = true

    try {
      await toursApi.deleteTour(tourId)
      toursStore.removeTour(tourId)
      return true
    } catch (err) {
      toursStore.setError(err)
      return false
    } finally {
      toursStore.loading = false
    }
  }

  return {
    publicTours,
    myTours,
    privateTours,
    loading,
    error,
    loadPublicTours,
    loadMyTours,
    createTour,
    patchTour,
    optimizeTour,
    deleteTour
  }
}
