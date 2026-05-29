<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="tour" class="modal-backdrop" @click.self="$emit('close')">
        <section class="modal-panel" role="dialog" aria-modal="true" aria-labelledby="tour-modal-title">
          <header class="modal-header">
            <div>
              <div class="header-badge-row">
                <span class="eyebrow">Itinerary Details</span>
                <span :class="['visibility-badge', tour.visibility]">
                  {{ tour.visibility }}
                </span>
              </div>
              <h2 id="tour-modal-title">{{ tour.name }}</h2>
            </div>
            <button class="icon-button" type="button" aria-label="Close details" @click="$emit('close')">
              x
            </button>
          </header>

          <div class="details-content">
            <div class="map-container-section">
              <TourMap :route="tour.places || []" />
            </div>

            <div class="sidebar-section">
              <div class="stat-box">
                <span class="stat-label">Total Distance</span>
                <span class="stat-value">{{ formatDistance(tour.total_distance) }}</span>
              </div>

              <div class="timeline-container">
                <h3 class="timeline-title">Route Stops</h3>
                <div class="timeline-scroll">
                  <div v-for="(place, index) in tour.places" :key="index" class="timeline-item">
                    <div class="timeline-marker">
                      <span class="marker-index">{{ index + 1 }}</span>
                    </div>
                    <div class="timeline-details">
                      <h4 class="place-name">{{ getPlaceName(place) }}</h4>
                      <p class="place-coords">
                        {{ place.latitude.toFixed(4) }}°, {{ place.longitude.toFixed(4) }}°
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <footer class="modal-actions">
            <BaseButton variant="secondary" type="button" @click="$emit('close')">
              Close
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
import TourMap from '@/views/TourMap.vue'

const props = defineProps({
  tour: {
    type: Object,
    default: null
  }
})

defineEmits(['close'])

function formatDistance(distance) {
  const value = Number(distance)
  return Number.isFinite(value) ? `${value.toFixed(2)} km` : 'Distance unavailable'
}

function getPlaceName(place) {
  return place.name?.split(', ')[0] || place.name || 'Unknown place'
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
  width: min(920px, 100%);
  background: #ffffff;
  border: 1px solid rgba(229, 231, 235, 0.9);
  border-radius: 1.25rem;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.2);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  max-height: 90vh;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-shrink: 0;
}

.header-badge-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.35rem;
}

.eyebrow {
  color: #2563eb;
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.visibility-badge {
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.visibility-badge.public {
  background: #ecfdf5;
  color: #047857;
}

.visibility-badge.private {
  background: #fef3c7;
  color: #92400e;
}

.modal-header h2 {
  color: #111827;
  font-size: 1.5rem;
  font-weight: 800;
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
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.icon-button:hover {
  background: #f9fafb;
  color: #111827;
  transform: scale(1.05);
}

.details-content {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 1.75rem;
  overflow: hidden;
  margin-bottom: 1.5rem;
  flex-grow: 1;
}

.map-container-section {
  width: 100%;
  height: 100%;
  min-height: 320px;
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
}

.sidebar-section {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  overflow: hidden;
}

.stat-box {
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.04), rgba(59, 130, 246, 0.08));
  border: 1px solid rgba(59, 130, 246, 0.15);
  padding: 1rem;
  border-radius: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #4b5563;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 1.6rem;
  font-weight: 900;
  color: #1d4ed8;
}

.timeline-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  overflow: hidden;
  flex-grow: 1;
}

.timeline-title {
  font-size: 0.9rem;
  font-weight: 800;
  color: #111827;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.timeline-scroll {
  overflow-y: auto;
  padding-right: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.timeline-item {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  position: relative;
}

.timeline-item:not(:last-child)::after {
  content: '';
  position: absolute;
  left: 13px;
  top: 26px;
  bottom: -12px;
  width: 2px;
  background-color: #e5e7eb;
}

.timeline-marker {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #eff6ff;
  border: 2px solid #3b82f6;
  color: #1d4ed8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 800;
  flex-shrink: 0;
  z-index: 2;
}

.timeline-details {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.place-name {
  font-size: 0.9rem;
  font-weight: 700;
  color: #1f2937;
}

.place-coords {
  font-size: 0.75rem;
  color: #6b7280;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  flex-shrink: 0;
}

.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .modal-panel {
    max-height: 95vh;
    padding: 1.25rem;
  }

  .details-content {
    grid-template-columns: 1fr;
    overflow-y: auto;
  }

  .map-container-section {
    height: 240px;
    min-height: 240px;
  }
}
</style>
