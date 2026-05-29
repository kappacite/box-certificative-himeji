import axios from 'axios'

const geocodingClient = axios.create({
  baseURL: 'https://nominatim.openstreetmap.org',
  timeout: 10000,
  headers: {
    Accept: 'application/json'
  }
})

export const geocodingApi = {
  searchPlaces: ({ city, query }) => geocodingClient.get('/search', {
    params: {
      q: [query, city].filter(Boolean).join(', '),
      format: 'json',
      addressdetails: 1,
      limit: 8
    }
  })
}
