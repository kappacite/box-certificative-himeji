import axios from 'axios'
import { useAuthStore } from '@/stores/authStore'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5000/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

client.interceptors.request.use((config) => {
  const authStore = useAuthStore()

  if (authStore.token) {
    config.headers.Authorization = `Bearer ${authStore.token}`
  }

  return config
})

client.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status
    const responseData = error.response?.data

    if (status === 401) {
      useAuthStore().logout()
    }

    return Promise.reject({
      status,
      message: responseData?.message ?? 'Unexpected error',
      code: responseData?.code ?? 'UNKNOWN_ERROR'
    })
  }
)

export default client
