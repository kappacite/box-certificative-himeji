import { ref } from 'vue'
import { geocodingApi } from '@/api/geocodingApi'

export function usePlaceSearch() {
  const results = ref([])
  const searchLoading = ref(false)
  const searchError = ref(null)

  async function searchPlaces(city, query) {
    searchError.value = null
    results.value = []

    if (!city?.trim()) {
      searchError.value = { message: 'Please enter a city before searching.' }
      return []
    }

    searchLoading.value = true

    try {
      const response = await geocodingApi.searchPlaces({
        city: city.trim(),
        query: query?.trim()
      })

      results.value = response.data.map((result) => normalizeResult(result, city))
      return results.value
    } catch {
      searchError.value = { message: 'Unable to search places. Please try again.' }
      return []
    } finally {
      searchLoading.value = false
    }
  }

  function clearResults() {
    results.value = []
    searchError.value = null
  }

  return {
    results,
    searchLoading,
    searchError,
    searchPlaces,
    clearResults
  }
}

function normalizeResult(result, fallbackCity) {
  const address = result.address ?? {}
  const city = address.city || address.town || address.village || address.municipality || fallbackCity
  const name = result.name || result.display_name?.split(',')[0] || 'Selected place'

  return {
    id: result.place_id,
    name,
    city,
    latitude: Number(result.lat),
    longitude: Number(result.lon),
    label: result.display_name
  }
}
