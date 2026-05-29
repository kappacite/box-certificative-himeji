import { storeToRefs } from 'pinia'
import { placesApi } from '@/api/placesApi'
import { usePlacesStore } from '@/stores/placesStore'

export function usePlaces() {
  const placesStore = usePlacesStore()
  const { places, loading, error } = storeToRefs(placesStore)

  async function loadPublicPlaces() {
    placesStore.clearError()
    placesStore.loading = true

    try {
      const response = await placesApi.getPublicPlaces()
      placesStore.setPlaces(response.data?.places ?? [])
    } catch (err) {
      placesStore.setError(err)
    } finally {
      placesStore.loading = false
    }
  }

  async function loadVisiblePlaces(isAuthenticated) {
    placesStore.clearError()
    placesStore.loading = true

    try {
      const publicResponse = await placesApi.getPublicPlaces()
      placesStore.setPlaces(publicResponse.data?.places ?? [])

      if (isAuthenticated) {
        const privateResponse = await placesApi.getMyPlaces()
        placesStore.mergePlaces(privateResponse.data?.places ?? [])
      }
    } catch (err) {
      placesStore.setError(err)
    } finally {
      placesStore.loading = false
    }
  }

  async function deletePlace(placeId) {
    placesStore.clearError()
    placesStore.loading = true

    try {
      await placesApi.deletePlace(placeId)
      placesStore.removePlace(placeId)
      return true
    } catch (err) {
      placesStore.setError(err)
      return false
    } finally {
      placesStore.loading = false
    }
  }

  async function createPlace(placeData) {
    placesStore.clearError()
    placesStore.loading = true

    try {
      const response = await placesApi.createPlace(placeData)
      const place = response.data?.place
      placesStore.addPlace(place)
      return place
    } catch (err) {
      placesStore.setError(err)
      return null
    } finally {
      placesStore.loading = false
    }
  }

  async function updatePlace(placeId, placeData) {
    placesStore.clearError()
    placesStore.loading = true

    try {
      const response = await placesApi.updatePlace(placeId, placeData)
      const updatedPlace = response.data?.place
      placesStore.updatePlace(updatedPlace)
      return updatedPlace
    } catch (err) {
      placesStore.setError(err)
      return null
    } finally {
      placesStore.loading = false
    }
  }

  return {
    places,
    loading,
    error,
    loadPublicPlaces,
    loadVisiblePlaces,
    createPlace,
    updatePlace,
    deletePlace
  }
}
