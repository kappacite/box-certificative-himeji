import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

export const useAuthStore = defineStore('auth', () => {
  // For easy testing without a backend, define a default test user
  const defaultTestUser = {
    username: 'Test Traveler',
    email: 'test.traveler@himeji-planner.com',
    avatarInitials: 'TT'
  }

  // Initialize state from local storage, or default to test user if they haven't explicitly logged out
  const storedUser = localStorage.getItem('himeji_user')
  const hasLoggedOut = localStorage.getItem('himeji_logged_out') === 'true'
  const user = ref(storedUser ? JSON.parse(storedUser) : (!hasLoggedOut ? defaultTestUser : null))

  const isAuthenticated = computed(() => !!user.value)

  function login(username, password) {
    const cleanUsername = username.trim() || 'Traveler'
    const initials = cleanUsername
      .split(' ')
      .map(n => n[0])
      .join('')
      .substring(0, 2)
      .toUpperCase()

    const mockUser = {
      username: cleanUsername,
      email: `${cleanUsername.toLowerCase().replace(/\s+/g, '')}@himeji-planner.com`,
      avatarInitials: initials || 'T'
    }

    user.value = mockUser
    localStorage.setItem('himeji_user', JSON.stringify(mockUser))
    localStorage.removeItem('himeji_logged_out')
    return true
  }

  function register(username, email, password) {
    const cleanUsername = username.trim() || 'Traveler'
    const initials = cleanUsername
      .split(' ')
      .map(n => n[0])
      .join('')
      .substring(0, 2)
      .toUpperCase()

    const mockUser = {
      username: cleanUsername,
      email: email || `${cleanUsername.toLowerCase().replace(/\s+/g, '')}@himeji-planner.com`,
      avatarInitials: initials || 'T'
    }

    user.value = mockUser
    localStorage.setItem('himeji_user', JSON.stringify(mockUser))
    localStorage.removeItem('himeji_logged_out')
    return true
  }

  function logout() {
    user.value = null
    localStorage.removeItem('himeji_user')
    localStorage.setItem('himeji_logged_out', 'true')
  }

  return {
    user,
    isAuthenticated,
    login,
    register,
    logout
  }
})

