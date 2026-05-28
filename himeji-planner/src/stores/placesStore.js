// src/stores/placesStore.js
import { ref } from 'vue'
import { defineStore } from 'pinia'

export const usePlacesStore = defineStore('places', () => {
  const places = ref([
    {
      id: 1,
      name: 'Himeji Castle (Himeji-jo)',
      description: 'Nicknamed the "White Heron Castle" due to its brilliant white exterior walls. It is one of Japan\'s twelve original surviving castles and is recognized as a registered UNESCO World Heritage site.',
      visitTime: '2-3h',
      rating: '4.9/5',
      tag: 'Must-See',
      cssClass: 'castle-img',
      latitude: 34.839449,
      longitude: 134.693905
    },
    {
      id: 2,
      name: 'Koko-en Garden',
      description: 'A compact complex of nine beautiful traditional Japanese gardens adjoining the castle grounds. Recreating authentic Edo-period landscape styles, they feature gorgeous waterfalls and tea ceremony houses.',
      visitTime: '1-2h',
      rating: '4.7/5',
      tag: 'Nature',
      cssClass: 'garden-img',
      latitude: 34.837372,
      longitude: 134.688849
    },
    {
      id: 3,
      name: 'Mount Shosha & Engyo-ji Temple',
      description: 'Located atop Mount Shosha, this sprawling Buddhist temple complex founded over 1,000 years ago offers a spiritual and peaceful atmosphere, made famous internationally as a filming location for "The Last Samurai".',
      visitTime: 'Half day',
      rating: '4.8/5',
      tag: 'Culture',
      cssClass: 'temple-img',
      latitude: 34.891243,
      longitude: 134.655848
    },
    {
      id: 4,
      name: 'Savigny le temple ',
      description: 'Located atop Mount Shosha, this sprawling Buddhist temple complex founded over 1,000 years ago offers a spiritual and peaceful atmosphere, made famous internationally as a filming location for "The Last Samurai".',
      visitTime: 'Half day',
      rating: '4.8/5',
      tag: 'Culture',
      cssClass: 'temple-img',
      latitude: 34.891243,
      longitude: 134.655848
    },
    {
      id: 5,
      name: 'Soulac sur mer',
      description: 'Located atop Mount Shosha, this sprawling Buddhist temple complex founded over 1,000 years ago offers a spiritual and peaceful atmosphere, made famous internationally as a filming location for "The Last Samurai".',
      visitTime: 'Half day',
      rating: '4.8/5',
      tag: 'Culture',
      cssClass: 'temple-img',
      latitude: 34.891243,
      longitude: 134.655848
    }
  ])

  const loading = ref(false)
  const error = ref(null)

  function setError(err) {
    error.value = err ?? null
  }

  function clearError() {
    error.value = null
  }

  return { places, loading, error, setError, clearError }
})