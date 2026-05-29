<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="place" class="modal-backdrop" @click.self="$emit('close')">
        <section class="modal-panel" role="dialog" aria-modal="true" aria-labelledby="place-modal-title">
          <header class="modal-header">
            <div>
              <p class="eyebrow">Place details</p>
              <h2 id="place-modal-title">{{ displayName }}</h2>
            </div>
            <button class="icon-button" type="button" aria-label="Close details" @click="$emit('close')">
              x
            </button>
          </header>

          <div class="details-grid">
            <div class="detail-item">
              <span class="detail-label">City</span>
              <span class="detail-value">{{ city }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Latitude</span>
              <span class="detail-value">{{ formattedLatitude }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Longitude</span>
              <span class="detail-value">{{ formattedLongitude }}</span>
            </div>
          </div>

          <p v-if="place.description" class="description">
            {{ place.description }}
          </p>

          <p v-if="error" class="error-message">
            {{ friendlyErrorMessage }}
          </p>

          <footer class="modal-actions">
            <BaseButton variant="secondary" type="button" @click="$emit('close')">
              Close
            </BaseButton>
            <BaseButton
              v-if="canEdit"
              variant="secondary"
              type="button"
              @click="$emit('edit', place)"
            >
              Edit place
            </BaseButton>
            <BaseButton
              v-if="canDelete"
              type="button"
              :loading="loading"
              @click="$emit('delete', place.id)"
            >
              Delete place
            </BaseButton>
          </footer>
        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed } from 'vue'
import BaseButton from '@/components/BaseButton.vue'

const props = defineProps({
  place: {
    type: Object,
    default: null
  },
  canEdit: {
    type: Boolean,
    default: false
  },
  canDelete: {
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

defineEmits(['close', 'edit', 'delete'])

const nameParts = computed(() => props.place?.name?.split(', ') ?? [])
const displayName = computed(() => nameParts.value[0] || props.place?.name || 'Unknown place')
const city = computed(() => nameParts.value[1] || 'Not specified')
const formattedLatitude = computed(() => formatCoordinate(props.place?.latitude))
const formattedLongitude = computed(() => formatCoordinate(props.place?.longitude))

const friendlyErrorMessage = computed(() => {
  const messages = {
    FORBIDDEN: 'You do not have permission to delete this place.',
    NOT_FOUND: 'This place no longer exists.',
    UNAUTHORIZED: 'Please log in again before deleting this place.',
    UNKNOWN_ERROR: 'Unable to delete this place. Please try again.'
  }

  return messages[props.error?.code] || messages.UNKNOWN_ERROR
})

function formatCoordinate(value) {
  const coordinate = Number(value)
  return Number.isFinite(coordinate) ? coordinate.toFixed(6) : 'Not available'
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

.details-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.9rem;
}

.detail-item {
  padding: 0.85rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.75rem;
  background: #f9fafb;
}

.detail-label,
.detail-value {
  display: block;
}

.detail-label {
  margin-bottom: 0.35rem;
  color: #6b7280;
  font-size: 0.75rem;
  font-weight: 700;
}

.detail-value {
  color: #111827;
  font-size: 0.95rem;
  font-weight: 700;
  word-break: break-word;
}

.description {
  margin-top: 1rem;
  color: #4b5563;
  line-height: 1.6;
}

.error-message {
  margin-top: 1rem;
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
  margin-top: 1.5rem;
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
  .details-grid {
    grid-template-columns: 1fr;
  }

  .modal-actions {
    flex-direction: column-reverse;
  }
}
</style>
