<template>
  <div class="auth-container">
    <BaseCard class="auth-card">
      <div class="auth-header">
        <h2>Create an Account</h2>
        <p>Join us to start planning your custom itineraries today!</p>
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
          id="email"
          v-model="email"
          type="email"
          label="Email Address"
          placeholder="name@example.com"
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

        <div v-if="error" class="error-message">
          {{ getFriendlyErrorMessage(error.code) }}
        </div>

        <BaseButton type="submit" :loading="loading">
          Register
        </BaseButton>
      </form>

      <div class="auth-footer">
        <p>
          Already registered? 
          <RouterLink :to="{ name: 'login' }" class="auth-link">Sign In</RouterLink>
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

const { loading, error, registerUser } = useAuth()

const username = ref('')
const email = ref('')
const password = ref('')

const handleSubmit = async () => {
  if (!username.value || !email.value || !password.value) {
    error.value = {
      code: 'VALIDATION_ERROR',
      message: 'Please fill in all fields.'
    }
    return
  }

  await registerUser({
    username: username.value,
    email: email.value,
    password: password.value
  })
}

const getFriendlyErrorMessage = (code) => {
  const errorMessages = {
    'CONFLICT_ERROR': 'This username or email is already registered.',
    'VALIDATION_ERROR': 'Please check your username, email, and password.',
    'UNKNOWN_ERROR': 'Unable to connect to the server. Please try again later.'
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
