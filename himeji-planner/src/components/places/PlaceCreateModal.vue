<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="open" class="modal-backdrop" @click.self="$emit('close')">
        <section class="modal-panel" role="dialog" aria-modal="true" aria-labelledby="create-place-title">
          <header class="modal-header">
            <div>
              <p class="eyebrow">New place</p>
              <h2 id="create-place-title">Add a place</h2>
            </div>
            <button class="icon-button" type="button" aria-label="Close form" @click="$emit('close')">
              x
            </button>
          </header>

          <form class="place-form" @submit.prevent="handleSubmit">
            <BaseInput
              id="place-name"
              v-model="form.name"
              label="Place name"
              placeholder="e.g. Himeji Castle"
              :disabled="loading"
              required
            />

            <BaseInput
              id="place-city"
              v-model="form.city"
              label="City"
              placeholder="e.g. Himeji"
              :disabled="loading"
              required
            />

            <div class="field-row">
              <BaseInput
                id="place-latitude"
                v-model="form.latitude"
                type="number"
                label="Latitude"
                placeholder="Optional"
                :disabled="loading"
                step="any"
              />
              <BaseInput
                id="place-longitude"
                v-model="form.longitude"
                type="number"
                label="Longitude"
                placeholder="Optional"
                :disabled="loading"
                step="any"
              />
            </div>

            <p v-if="localError" class="error-message">
              {{ localError }}
            </p>

            <p v-else-if="error" class="error-message">
              {{ friendlyErrorMessage }}
            </p>

            <footer class="modal-actions">
              <BaseButton variant="secondary" type="button" :disabled="loading" @click="$emit('close')">
                Cancel
              </BaseButton>
              <BaseButton type="submit" :loading="loading">
                Add place
              </BaseButton>
            </footer>
          </form>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import BaseButton from '@/components/BaseButton.vue'
import BaseInput from '@/components/BaseInput.vue'

const props = defineProps({
  open: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'create'])

const form = reactive({
  name: '',
  city: '',
  latitude: '',
  longitude: ''
})

const localError = ref('')

const friendlyErrorMessage = computed(() => {
  const messages = {
    BAD_REQUEST: 'Please check the place information.',
    VALIDATION_ERROR: 'Please check the place information.',
    FORBIDDEN: 'You do not have permission to create this place.',
    UNAUTHORIZED: 'Please log in again before adding a place.',
    NETWORK_ERROR: 'Unable to reach the API. Please check that the backend is running.',
    INTERNAL_SERVER_ERROR: 'The server could not create this place. Please check the backend logs.',
    UNKNOWN_ERROR: 'Unable to add this place. Please try again.'
  }

  return props.error?.message || messages[props.error?.code] || messages.UNKNOWN_ERROR
})

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      resetForm()
    }
  }
)

function handleSubmit() {
  localError.value = ''

  if (!form.name.trim()) {
    localError.value = 'Please enter a place name.'
    return
  }

  if (!form.city.trim()) {
    localError.value = 'Please enter a city.'
    return
  }

  if (!hasValidCoordinates()) {
    localError.value = 'Latitude and longitude must both be valid numbers when provided.'
    return
  }

  emit('create', buildPayload())
}

function buildPayload() {
  const payload = {
    name: `${form.name.trim()}, ${form.city.trim()}`
  }

  if (form.latitude !== '') {
    payload.latitude = Number(form.latitude)
  }

  if (form.longitude !== '') {
    payload.longitude = Number(form.longitude)
  }

  return payload
}

function hasValidCoordinates() {
  if (form.latitude === '' && form.longitude === '') {
    return true
  }

  if (form.latitude === '' || form.longitude === '') {
    return false
  }

  return Number.isFinite(Number(form.latitude)) && Number.isFinite(Number(form.longitude))
}

function resetForm() {
  form.name = ''
  form.city = ''
  form.latitude = ''
  form.longitude = ''
  localError.value = ''
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: rgba(17, 24, 39, 0.45);
  backdrop-filter: blur(8px);
}

.modal-panel {
  width: min(560px, 100%);
  background: #ffffff;
  border: 1px solid rgba(229, 231, 235, 0.9);
  border-radius: 1rem;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.2);
  padding: 1.5rem;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.eyebrow {
  margin-bottom: 0.35rem;
  color: #047857;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.modal-header h2 {
  color: #111827;
  font-size: 1.4rem;
  line-height: 1.25;
}

.icon-button {
  width: 36px;
  height: 36px;
  border: 1px solid #e5e7eb;
  border-radius: 50%;
  background: #ffffff;
  color: #4b5563;
  font-size: 1.1rem;
  font-weight: 700;
  cursor: pointer;
}

.icon-button:hover {
  background: #f9fafb;
  color: #111827;
}

.place-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.error-message {
  padding: 0.75rem 1rem;
  border: 1px solid #fecaca;
  border-radius: 0.75rem;
  background: #fef2f2;
  color: #b91c1c;
  font-size: 0.875rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

@media (max-width: 520px) {
  .field-row {
    grid-template-columns: 1fr;
  }

  .modal-actions {
    flex-direction: column-reverse;
  }
}
</style>
