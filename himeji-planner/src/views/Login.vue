<template>
  <div class="auth-container">
    <BaseCard class="auth-card">
      <div class="auth-header">
        <h2>Welcome to Himeji Planner</h2>
        <p>Login to start planning your travel!</p>
      </div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <BaseInput
          id="username"
          v-model="username"
          label="Username"
          placeholder="e.g. HimejiTraveler"
          required
        />

        <BaseInput
          id="password"
          v-model="password"
          type="password"
          label="Password"
          placeholder="••••••••"
          required
        />

        <div class="test-user-info">
          ⚙️ <strong>Demo Mode</strong>: The test credentials above are pre-filled for a quick trial.
        </div>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>

        <BaseButton type="submit" :loading="isLoading">
          Log in
        </BaseButton>
      </form>

      <div class="auth-footer">
        <p>
          Don't have an account? 
          <RouterLink :to="{ name: 'register' }" class="auth-link">Register</RouterLink>
        </p>
      </div>
    </BaseCard>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import BaseCard from '@/components/BaseCard.vue'
import BaseInput from '@/components/BaseInput.vue'
import BaseButton from '@/components/BaseButton.vue'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('Test Traveler')
const password = ref('password123')
const error = ref('')
const isLoading = ref(false)

const handleSubmit = async () => {
  if (!username.value || !password.value) {
    error.value = 'Please fill in all fields.'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 800))
    authStore.login(username.value, password.value)
    router.push({ name: 'dashboard' })
  } catch (err) {
    error.value = 'Invalid credentials.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 140px);
  padding: 1rem;
}

.auth-card {
  width: 100%;
  max-width: 440px;
  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(16px) saturate(180%);
}

.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}

.auth-header h2 {
  font-size: 1.75rem;
  color: #111827;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #1e40af, #3b82f6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.auth-header p {
  color: #6b7280;
  font-size: 0.925rem;
  line-height: 1.4;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.error-message {
  padding: 0.75rem 1rem;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  text-align: center;
}

.test-user-info {
  padding: 0.75rem 1rem;
  background-color: rgba(59, 130, 246, 0.04);
  border: 1px dashed rgba(59, 130, 246, 0.3);
  color: #1e40af;
  border-radius: 0.75rem;
  font-size: 0.825rem;
  line-height: 1.4;
  text-align: center;
}

.auth-footer {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.875rem;
  color: #6b7280;
}

.auth-link {
  color: #2563eb;
  text-decoration: none;
  font-weight: 600;
  transition: color 0.15s ease;
}

.auth-link:hover {
  color: #1d4ed8;
  text-decoration: underline;
}
</style>
