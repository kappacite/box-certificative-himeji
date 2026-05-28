import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute, useRouter } from 'vue-router'
import { authApi } from '@/api/authApi'
import { useAuthStore } from '@/stores/authStore'

export function useAuth() {
  const authStore = useAuthStore()
  const router = useRouter()
  const route = useRoute()
  const { token, user, isAuthenticated } = storeToRefs(authStore)

  const loading = ref(false)
  const error = ref(null)

  function clearError() {
    error.value = null
  }

  async function loginUser(credentials) {
    clearError()
    loading.value = true

    try {
      const response = await authApi.login(credentials)
      const loggedIn = authStore.login(response.data)

      if (!loggedIn) {
        error.value = {
          code: 'INVALID_AUTH_RESPONSE',
          message: 'The authentication response is incomplete.'
        }
        return false
      }

      const redirectPath = route.query.redirect?.toString()
      await router.push(redirectPath || { name: 'dashboard' })
      return true
    } catch (err) {
      error.value = err
      return false
    } finally {
      loading.value = false
    }
  }

  async function registerUser(userData) {
    clearError()
    loading.value = true

    try {
      await authApi.register(userData)
      await router.push({ name: 'login' })
      return true
    } catch (err) {
      error.value = err
      return false
    } finally {
      loading.value = false
    }
  }

  async function logoutUser() {
    clearError()
    loading.value = true

    try {
      if (authStore.token) {
        await authApi.logout()
      }
    } catch {
      // The local session must still be cleared if the server logout fails.
    } finally {
      authStore.logout()
      loading.value = false
      await router.push({ name: 'login' })
    }
  }

  return {
    token,
    user,
    isAuthenticated,
    loading,
    error,
    clearError,
    loginUser,
    registerUser,
    logoutUser
  }
}
