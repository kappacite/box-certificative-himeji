import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

function readStoredUser() {
  try {
    return JSON.parse(localStorage.getItem('user') ?? 'null')
  } catch {
    localStorage.removeItem('user')
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') ?? null)
  const user = ref(readStoredUser())

  if (!user.value) {
    token.value = null
    localStorage.removeItem('token')
  }

  const isAuthenticated = computed(() => Boolean(token.value && user.value))

  function login(payload) {
    if (!payload || !payload.token || !payload.user) return false

    token.value = payload.token
    user.value = payload.user

    localStorage.setItem('token', payload.token)
    localStorage.setItem('user', JSON.stringify(payload.user))
    return true
  }

  function logout() {
    token.value = null
    user.value = null

    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  return {
    token,
    user,
    isAuthenticated,
    login,
    logout
  }
})
