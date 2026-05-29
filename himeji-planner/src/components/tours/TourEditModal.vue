<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div v-if="tour" class="modal-backdrop" @click.self="handleClose">
        <section class="modal-panel" role="dialog" aria-modal="true" aria-labelledby="edit-modal-title">

          <!-- Header -->
          <header class="modal-header">
            <div>
              <span class="eyebrow">Edit Tour</span>
              <h2 id="edit-modal-title">{{ localName }}</h2>
            </div>
            <button class="icon-button" type="button" aria-label="Close" @click="handleClose">✕</button>
          </header>

          <!-- Error banner -->
          <div v-if="errorMessage" class="error-banner" role="alert">
            ⚠️ {{ errorMessage }}
          </div>

          <!-- Controls row -->
          <div class="controls-row">
            <!-- Tour name -->
            <div class="control-group">
              <label class="control-label" for="tour-name-input">Tour name</label>
              <input
                id="tour-name-input"
                v-model="localName"
                class="name-input"
                type="text"
                placeholder="Tour name…"
              />
            </div>

            <!-- Visibility toggle -->
            <div class="control-group">
              <label class="control-label">Visibility</label>
              <button
                class="visibility-toggle"
                :class="localVisibility"
                type="button"
                @click="toggleVisibility"
              >
                <span class="toggle-icon">{{ localVisibility === 'public' ? '🌍' : '🔒' }}</span>
                {{ localVisibility === 'public' ? 'Public' : 'Private' }}
              </button>
            </div>

            <!-- Optimize checkbox -->
            <div class="control-group">
              <label class="control-label" for="optimize-check">Re-optimize</label>
              <label class="switch-label" for="optimize-check">
                <input id="optimize-check" v-model="shouldOptimize" type="checkbox" class="sr-only" />
                <span class="switch" :class="{ active: shouldOptimize }"></span>
                <span class="switch-text">{{ shouldOptimize ? 'On – respects locks' : 'Off – keep order' }}</span>
              </label>
            </div>
          </div>

          <!-- Drag-and-drop stop list -->
          <div class="stops-section">
            <div class="stops-header">
              <h3 class="stops-title">Stop order</h3>
              <p class="stops-hint">Drag to reorder · 🔒 to lock · × to remove</p>
            </div>

            <div class="stops-list" ref="listEl">
              <div
                v-for="(stop, idx) in editableStops"
                :key="stop._uid"
                class="stop-row"
                :class="{
                  locked: stop.locked,
                  dragging: dragIndex === idx,
                  'drag-over': dragOverIndex === idx,
                  'broken-hotel': stop.is_hotel && brokenHotels.has(stop._uid)
                }"
                draggable="true"
                @dragstart="onDragStart(idx, $event)"
                @dragover.prevent="onDragOver(idx)"
                @drop.prevent="onDrop(idx)"
                @dragend="onDragEnd"
              >
                <span class="drag-handle" aria-hidden="true">⠿</span>

                <span
                  class="stop-badge"
                  :class="stop.is_hotel ? (brokenHotels.has(stop._uid) ? 'hotel-broken' : 'hotel') : 'regular'"
                >
                  {{ stop.is_hotel ? '🏨' : idx + 1 }}
                </span>

                <span class="stop-name">{{ shortName(stop.name) }}</span>

                <span
                  v-if="stop.is_hotel && brokenHotels.has(stop._uid)"
                  class="broken-warning"
                  title="This hotel return is no longer linked to its original stop"
                >⚠️ link broken</span>

                <span v-if="stop.locked" class="lock-indicator" title="Locked">🔒</span>

                <button
                  class="lock-btn"
                  :class="{ active: stop.locked }"
                  type="button"
                  :aria-label="stop.locked ? 'Unlock stop' : 'Lock stop position'"
                  @click="toggleLock(idx)"
                >
                  {{ stop.locked ? '🔓' : '🔒' }}
                </button>

                <button
                  class="delete-btn"
                  type="button"
                  aria-label="Remove stop"
                  @click="removeStop(idx)"
                >×</button>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <footer class="modal-actions">
            <button class="btn-secondary" type="button" @click="handleClose">Cancel</button>
            <button
              class="btn-primary"
              type="button"
              :disabled="saving"
              @click="handleSave"
            >
              <span v-if="saving" class="spinner"></span>
              {{ saving ? 'Saving…' : 'Save changes' }}
            </button>
          </footer>

        </section>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { useTours } from '@/composables/useTours'

const props = defineProps({
  tour: { type: Object, default: null }
})

const emit = defineEmits(['close', 'saved'])

const { patchTour, optimizeTour } = useTours()

// ── Local state ──────────────────────────────────────────────────────────────
const localName = ref('')
const localVisibility = ref('private')
const shouldOptimize = ref(false)
const editableStops = ref([])
const saving = ref(false)
const errorMessage = ref(null)

// drag state
const dragIndex = ref(null)
const dragOverIndex = ref(null)

// originalPredecessors: hotel _uid → predecessor _uid at init time
// Used to detect when a hotel's upstream stop has been moved/removed
const originalPredecessors = ref({})

// ── Init when tour changes ───────────────────────────────────────────────────
watch(
  () => props.tour,
  (newTour) => {
    if (!newTour) return
    localName.value = newTour.name ?? ''
    localVisibility.value = newTour.visibility ?? 'private'
    shouldOptimize.value = false
    errorMessage.value = null
    const stops = (newTour.places ?? []).map((p, i) => ({
      ...p,
      _uid: `${p.id ?? i}-${i}`,
      locked: p.locked ?? false
    }))
    editableStops.value = stops
    // Record each hotel's original predecessor
    const preds = {}
    stops.forEach((stop, idx) => {
      if (stop.is_hotel && idx > 0) {
        preds[stop._uid] = stops[idx - 1]._uid
      }
    })
    originalPredecessors.value = preds
  },
  { immediate: true }
)

// ── Broken-hotel detection ───────────────────────────────────────────────────
// A hotel is "broken" when its current predecessor differs from the original one
const brokenHotels = computed(() => {
  const broken = new Set()
  const currentUids = editableStops.value.map((s) => s._uid)
  editableStops.value.forEach((stop, idx) => {
    if (!stop.is_hotel) return
    const origPred = originalPredecessors.value[stop._uid]
    if (origPred == null) return          // hotel had no predecessor originally
    const currentPred = idx > 0 ? editableStops.value[idx - 1]._uid : null
    // Also broken if original predecessor was removed entirely
    const origStillPresent = currentUids.includes(origPred)
    if (currentPred !== origPred || !origStillPresent) {
      broken.add(stop._uid)
    }
  })
  return broken
})

// ── Helpers ──────────────────────────────────────────────────────────────────
function shortName(name) {
  return name?.split(', ')[0] ?? name ?? 'Unknown'
}

function toggleVisibility() {
  localVisibility.value = localVisibility.value === 'public' ? 'private' : 'public'
}

function toggleLock(idx) {
  editableStops.value[idx].locked = !editableStops.value[idx].locked
}

function removeStop(idx) {
  editableStops.value.splice(idx, 1)
}

// ── Drag & drop ──────────────────────────────────────────────────────────────
function onDragStart(idx, event) {
  dragIndex.value = idx
  event.dataTransfer.effectAllowed = 'move'
}

function onDragOver(idx) {
  dragOverIndex.value = idx
}

function onDrop(targetIdx) {
  const from = dragIndex.value
  if (from === null || from === targetIdx) return

  const items = [...editableStops.value]
  const [moved] = items.splice(from, 1)
  // When manually moved, lock this stop automatically
  moved.locked = true
  items.splice(targetIdx, 0, moved)
  editableStops.value = items
  dragIndex.value = null
  dragOverIndex.value = null
}

function onDragEnd() {
  dragIndex.value = null
  dragOverIndex.value = null
}

// ── Locked positions map — format: { place_id: position_index } ─────────────
// The backend _parse_place_inputs_and_locks expects:
//   locked_positions = { "<place_id>": <target_position>, ... }
const lockedPositions = computed(() => {
  const result = {}
  editableStops.value.forEach((stop, idx) => {
    if (stop.locked && stop.id != null) {
      result[String(stop.id)] = idx
    }
  })
  return result
})

// ── Save ─────────────────────────────────────────────────────────────────────
async function handleSave() {
  saving.value = true
  errorMessage.value = null

  try {
    const placeIds = editableStops.value.map((s) => s.id).filter(Boolean)

    let saved

    if (shouldOptimize.value) {
      // Optimize mode: only user-locked stops are fixed, backend routes the rest
      const lockedPos = Object.keys(lockedPositions.value).length > 0 ? lockedPositions.value : null

      const optimized = await optimizeTour({
        place_ids: placeIds,
        locked_positions: lockedPos
      })
      if (!optimized) {
        errorMessage.value = 'Optimization failed. Please try again.'
        return
      }
      saved = await patchTour(props.tour.id, {
        name: localName.value,
        visibility: localVisibility.value,
        place_ids: optimized.ordered_ids ?? placeIds,
        locked_positions: lockedPos
      })
    } else {
      // Manual order: lock EVERY stop at its current position so the
      // backend algorithm cannot reorder anything.
      // Format: { "<place_id>": <position_index> }
      const allLocked = {}
      placeIds.forEach((id, idx) => {
        if (id != null) allLocked[String(id)] = idx
      })

      saved = await patchTour(props.tour.id, {
        name: localName.value,
        visibility: localVisibility.value,
        place_ids: placeIds,
        locked_positions: allLocked
      })
    }

    if (saved) {
      emit('saved', saved)
      emit('close')
    } else {
      errorMessage.value = 'Could not save. Please try again.'
    }
  } finally {
    saving.value = false
  }
}

function handleClose() {
  if (!saving.value) emit('close')
}
</script>

<style scoped>
/* ── Backdrop & panel ─────────────────────────────────────────────────────── */
.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: rgba(17, 24, 39, 0.5);
  backdrop-filter: blur(10px);
}

.modal-panel {
  width: min(700px, 100%);
  background: #ffffff;
  border: 1px solid rgba(229, 231, 235, 0.9);
  border-radius: 1.25rem;
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.22);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  max-height: 90vh;
  overflow: hidden;
}

/* ── Header ──────────────────────────────────────────────────────────────── */
.modal-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.eyebrow {
  display: block;
  color: #2563eb;
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 0.2rem;
}

.modal-header h2 {
  font-size: 1.35rem;
  font-weight: 800;
  color: #111827;
}

.icon-button {
  width: 36px;
  height: 36px;
  border: 1px solid #e5e7eb;
  border-radius: 50%;
  background: #fff;
  color: #4b5563;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  flex-shrink: 0;
}
.icon-button:hover { background: #f9fafb; color: #111827; transform: scale(1.05); }

/* ── Error ──────────────────────────────────────────────────────────────── */
.error-banner {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  border-radius: 0.6rem;
  padding: 0.75rem 1rem;
  font-size: 0.9rem;
  font-weight: 600;
}

/* ── Controls row ────────────────────────────────────────────────────────── */
.controls-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1.25rem;
  align-items: flex-end;
}

.control-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.control-label {
  font-size: 0.72rem;
  font-weight: 800;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.name-input {
  padding: 0.5rem 0.75rem;
  border: 1.5px solid #e5e7eb;
  border-radius: 0.5rem;
  font-size: 0.95rem;
  font-family: inherit;
  transition: border-color 0.2s;
  min-width: 200px;
}
.name-input:focus { outline: none; border-color: #3b82f6; }

/* Visibility toggle button */
.visibility-toggle {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 1rem;
  border-radius: 999px;
  border: 2px solid transparent;
  font-size: 0.85rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s;
}
.visibility-toggle.public  { background: #ecfdf5; color: #047857; border-color: #6ee7b7; }
.visibility-toggle.private { background: #fef3c7; color: #92400e; border-color: #fcd34d; }
.visibility-toggle:hover { filter: brightness(0.96); transform: scale(1.02); }
.toggle-icon { font-size: 1rem; }

/* Switch */
.switch-label {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  cursor: pointer;
}
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); }
.switch {
  width: 40px;
  height: 22px;
  border-radius: 999px;
  background: #d1d5db;
  position: relative;
  transition: background 0.25s;
  flex-shrink: 0;
}
.switch::after {
  content: '';
  position: absolute;
  left: 3px;
  top: 3px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #fff;
  transition: transform 0.25s;
}
.switch.active { background: #2563eb; }
.switch.active::after { transform: translateX(18px); }
.switch-text { font-size: 0.82rem; font-weight: 600; color: #4b5563; }

/* ── Stops list ──────────────────────────────────────────────────────────── */
.stops-section {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  overflow: hidden;
  flex: 1;
}

.stops-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.stops-title {
  font-size: 0.85rem;
  font-weight: 800;
  color: #111827;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stops-hint {
  font-size: 0.75rem;
  color: #9ca3af;
}

.stops-list {
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  padding-right: 0.25rem;
}

.stop-row {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.75rem;
  background: #f9fafb;
  border: 1.5px solid #e5e7eb;
  border-radius: 0.65rem;
  cursor: grab;
  transition: all 0.18s;
  user-select: none;
}
.stop-row:hover { background: #f0f9ff; border-color: #93c5fd; }
.stop-row.locked { background: #fefce8; border-color: #fcd34d; }
.stop-row.dragging { opacity: 0.45; }
.stop-row.broken-hotel {
  background: #fff1f1;
  border-color: #ef4444;
  animation: pulse-red 1.6s ease-in-out infinite;
}
@keyframes pulse-red {
  0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
  50%       { box-shadow: 0 0 0 4px rgba(239,68,68,0.18); }
}
.stop-row.drag-over { border-color: #2563eb; background: #eff6ff; box-shadow: 0 0 0 2px rgba(37,99,235,0.2); }

.drag-handle {
  color: #d1d5db;
  font-size: 1.1rem;
  cursor: grab;
  flex-shrink: 0;
}
.stop-row.locked .drag-handle { cursor: not-allowed; color: #fbbf24; }

.stop-badge {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.72rem;
  font-weight: 900;
  flex-shrink: 0;
}
.stop-badge.regular      { background: #eff6ff; color: #1d4ed8; border: 2px solid #bfdbfe; }
.stop-badge.hotel        { background: #fef2f2; color: #b91c1c; border: 2px solid #fecaca; font-size: 1rem; }
.stop-badge.hotel-broken { background: #ef4444; color: #fff;    border: 2px solid #dc2626; font-size: 1rem; }

.stop-name {
  flex: 1;
  font-size: 0.88rem;
  font-weight: 600;
  color: #1f2937;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lock-indicator {
  font-size: 0.85rem;
}

.broken-warning {
  font-size: 0.7rem;
  font-weight: 800;
  color: #dc2626;
  white-space: nowrap;
  flex-shrink: 0;
}

.lock-btn {
  background: transparent;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  padding: 0.15rem;
  border-radius: 0.3rem;
  transition: transform 0.15s;
  flex-shrink: 0;
}
.lock-btn:hover { transform: scale(1.2); }

.delete-btn {
  width: 22px;
  height: 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1.5px solid #e5e7eb;
  border-radius: 50%;
  color: #9ca3af;
  font-size: 0.95rem;
  line-height: 1;
  cursor: pointer;
  transition: all 0.18s;
  flex-shrink: 0;
  font-weight: 700;
}
.delete-btn:hover {
  background: #fef2f2;
  border-color: #ef4444;
  color: #ef4444;
  transform: scale(1.15);
}

/* ── Footer ──────────────────────────────────────────────────────────────── */
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  flex-shrink: 0;
}

.btn-secondary {
  padding: 0.55rem 1.25rem;
  border: 1.5px solid #e5e7eb;
  border-radius: 0.65rem;
  background: #fff;
  color: #374151;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-secondary:hover { background: #f9fafb; border-color: #d1d5db; }

.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 1.5rem;
  background: linear-gradient(135deg, #2563eb, #0891b2);
  color: #fff;
  border: none;
  border-radius: 0.65rem;
  font-size: 0.9rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-primary:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 14px rgba(37,99,235,0.35); }
.btn-primary:disabled { opacity: 0.65; cursor: not-allowed; }

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Transition ──────────────────────────────────────────────────────────── */
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.2s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }

@media (max-width: 640px) {
  .modal-panel { padding: 1.25rem; }
  .controls-row { flex-direction: column; }
  .name-input { min-width: 0; width: 100%; }
}
</style>
