<template>
  <div class="auth-container">
    <BaseCard class="auth-card">
      <div class="auth-header">
        <h2>Welcome to Himeji Planner</h2>
        <p>Login to start planning your travel!</p>
      </div>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <BaseInput
          id="email"
          v-model="email"
          type="email"
          label="Email Address"
          placeholder="e.g. traveler@example.com"
          :disabled="loading"
          required
        />

        <BaseInput
          id="password"
          v-model="password"
          type="password"
          label="Password"
          placeholder="••••••••"
          :disabled="loading"
          required
        />

        <div class="test-user-info">
          ⚙️ <strong>Production Mode</strong>: Connect using your registered account credentials.
        </div>

        <div v-if="error" class="error-message">
          {{ getFriendlyErrorMessage(error.code) }}
        </div>

        <BaseButton type="submit" :loading="loading">
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
import { useAuth } from '@/composables/useAuth'
import BaseCard from '@/components/BaseCard.vue'
import BaseInput from '@/components/BaseInput.vue'
import BaseButton from '@/components/BaseButton.vue'

const { loading, error, loginUser } = useAuth()

const email = ref('')
const password = ref('')

const handleSubmit = async () => {
  await loginUser({
    email: email.value,
    password: password.value
  })
}

const getFriendlyErrorMessage = (code) => {
  const errorMessages = {
    'UNAUTHORIZED': 'Invalid email or password. Please verify your credentials.',
    'VALIDATION_ERROR': 'Please ensure all fields are correctly formatted.',
    'INVALID_AUTH_RESPONSE': 'The server response is incomplete. Please try again later.',
    'UNKNOWN_ERROR': 'Unable to connect to the server. Please check your network connection.'
  }
  return errorMessages[code] || errorMessages['UNKNOWN_ERROR']
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
  background-clip: text;
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
