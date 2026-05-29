<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="open && place" class="modal-backdrop" @click.self="$emit('close')">
        <section class="modal-panel" role="dialog" aria-modal="true" aria-labelledby="edit-place-title">
          <header class="modal-header">
            <div>
              <p class="eyebrow">Edit place</p>
              <h2 id="edit-place-title">Modify place details</h2>
            </div>
            <button class="icon-button" type="button" aria-label="Close form" @click="$emit('close')">
              x
            </button>
          </header>

          <form class="place-form" @submit.prevent="handleSubmit">
            <BaseInput
              id="edit-place-name"
              v-model="form.name"
              label="Place name"
              placeholder="e.g. Himeji Castle"
              :disabled="loading"
              required
            />

            <BaseInput
              id="edit-place-city"
              v-model="form.city"
              label="City"
              placeholder="e.g. Himeji"
              :disabled="loading"
              required
            />

            <div class="search-panel">
              <BaseInput
                id="edit-place-search"
                v-model="searchQuery"
                label="Search places in this city"
                placeholder="e.g. cathedral, museum, station"
                :disabled="loading || searchLoading"
              />
              <BaseButton
                type="button"
                variant="secondary"
                :loading="searchLoading"
                :disabled="loading"
                @click="handleSearch"
              >
                Search
              </BaseButton>
            </div>

            <p v-if="searchError" class="search-message">
              {{ searchError.message }}
            </p>

            <ul v-if="results.length > 0" class="search-results">
              <li v-for="result in results" :key="result.id">
                <button type="button" class="result-button" @click="selectSearchResult(result)">
                  <strong>{{ result.name }}</strong>
                  <span>{{ result.label }}</span>
                </button>
              </li>
            </ul>

            <div class="field-row">
              <BaseInput
                id="edit-place-latitude"
                v-model="form.latitude"
                type="number"
                label="Latitude"
                placeholder="Optional"
                :disabled="loading"
                step="any"
              />
              <BaseInput
                id="edit-place-longitude"
                v-model="form.longitude"
                type="number"
                label="Longitude"
                placeholder="Optional"
                :disabled="loading"
                step="any"
              />
            </div>

            <label class="checkbox-field">
              <input v-model="form.isPrivate" type="checkbox" :disabled="loading" />
              <span>Make this place private</span>
            </label>

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
                Save Changes
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
import { usePlaceSearch } from '@/composables/usePlaceSearch'
import BaseButton from '@/components/BaseButton.vue'
import BaseInput from '@/components/BaseInput.vue'

const props = defineProps({
  open: {
    type: Boolean,
    default: false
  },
  place: {
    type: Object,
    default: null
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

const emit = defineEmits(['close', 'update'])

const form = reactive({
  name: '',
  city: '',
  latitude: '',
  longitude: '',
  isPrivate: false
})

const localError = ref('')
const searchQuery = ref('')
const { results, searchLoading, searchError, searchPlaces, clearResults } = usePlaceSearch()

const friendlyErrorMessage = computed(() => {
  const messages = {
    BAD_REQUEST: 'Please check the place information.',
    VALIDATION_ERROR: 'Please check the place information.',
    FORBIDDEN: 'You do not have permission to update this place.',
    UNAUTHORIZED: 'Please log in again before updating a place.',
    NETWORK_ERROR: 'Unable to reach the API. Please check that the backend is running.',
    INTERNAL_SERVER_ERROR: 'The server could not update this place. Please check the backend logs.',
    UNKNOWN_ERROR: 'Unable to update this place. Please try again.'
  }

  return props.error?.message || messages[props.error?.code] || messages.UNKNOWN_ERROR
})

watch(
  [() => props.open, () => props.place],
  ([isOpen, currentPlace]) => {
    if (isOpen && currentPlace) {
      const nameParts = currentPlace.name?.split(', ') ?? []
      form.name = nameParts[0] || currentPlace.name || ''
      form.city = nameParts[1] || currentPlace.city || ''
      form.latitude = currentPlace.latitude !== undefined && currentPlace.latitude !== null ? currentPlace.latitude.toString() : ''
      form.longitude = currentPlace.longitude !== undefined && currentPlace.longitude !== null ? currentPlace.longitude.toString() : ''
      form.isPrivate = currentPlace.visibility === 'private'
      searchQuery.value = ''
      localError.value = ''
      clearResults()
    }
  },
  { immediate: true }
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

  emit('update', props.place.id, buildPayload())
}

async function handleSearch() {
  localError.value = ''
  await searchPlaces(form.city, searchQuery.value)
}

function selectSearchResult(result) {
  form.name = result.name
  form.city = result.city
  form.latitude = result.latitude.toString()
  form.longitude = result.longitude.toString()
  clearResults()
}

function buildPayload() {
  const payload = {
    name: `${form.name.trim()}, ${form.city.trim()}`,
    visibility: form.isPrivate ? 'private' : 'public',
    city: form.city.trim()
  }

  if (form.latitude !== '') {
    payload.latitude = Number(form.latitude)
  } else {
    payload.latitude = null
  }

  if (form.longitude !== '') {
    payload.longitude = Number(form.longitude)
  } else {
    payload.longitude = null
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

.search-panel {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: end;
  gap: 0.75rem;
}

.checkbox-field {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  color: #374151;
  font-size: 0.92rem;
  font-weight: 700;
}

.checkbox-field input {
  width: 18px;
  height: 18px;
  accent-color: #047857;
}

.search-message {
  padding: 0.75rem 1rem;
  border: 1px solid #bfdbfe;
  border-radius: 0.75rem;
  background: #eff6ff;
  color: #1d4ed8;
  font-size: 0.875rem;
}

.search-results {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 220px;
  margin: 0;
  padding: 0;
  overflow-y: auto;
  list-style: none;
}

.result-button {
  width: 100%;
  padding: 0.75rem 0.9rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  background: #ffffff;
  text-align: left;
  cursor: pointer;
}

.result-button:hover {
  border-color: #10b981;
  background: #f0fdf4;
}

.result-button strong,
.result-button span {
  display: block;
}

.result-button strong {
  color: #111827;
  font-size: 0.95rem;
}

.result-button span {
  margin-top: 0.25rem;
  color: #6b7280;
  font-size: 0.8rem;
  line-height: 1.4;
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
  .field-row,
  .search-panel {
    grid-template-columns: 1fr;
  }

  .modal-actions {
    flex-direction: column-reverse;
  }
}
</style>
