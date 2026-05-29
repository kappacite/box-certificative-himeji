<template>
  <div class="dashboard-container">
    <!-- Header banner -->
    <header class="dashboard-header">
      <div class="welcome-section">
        <h1>Hello, {{ authStore.user?.username || 'Traveler' }}! 👋</h1>
        <p class="subtitle">Welcome to your personal travel workspace. Ready to plan your next journey?</p>
      </div>
      
      <div class="quick-status">
        <div class="avatar-badge">{{ authStore.user?.avatarInitials || 'T' }}</div>
        <div class="user-details">
          <span class="user-name">{{ authStore.user?.username }}</span>
          <span class="user-email">{{ authStore.user?.email }}</span>
        </div>
      </div>
    </header>

    <!-- Stats row -->
    <div class="stats-row">
      <BaseCard class="stat-card">
        <div class="stat-icon">🗺️</div>
        <div class="stat-content">
          <span class="stat-number">{{ myTours.length }}</span>
          <span class="stat-label">Itineraries published</span>
        </div>
      </BaseCard>
      
      <BaseCard highlight class="stat-card">
        <div class="stat-icon">🚀</div>
        <div class="stat-content">
          <span class="stat-number">{{ totalOptimizedKm }} km</span>
          <span class="stat-label">Total optimized km</span>
        </div>
      </BaseCard>
      
      <BaseCard class="stat-card">
        <div class="stat-icon">🔒</div>
        <div class="stat-content">
          <span class="stat-number">{{ privateTours.length }}</span>
          <span class="stat-label">Private itineraries</span>
        </div>
      </BaseCard>
    </div>

    <!-- Main Section: Active Modules -->
    <div class="dashboard-content">
      <div class="section-header">
        <h2>📋 My Saved Travel Itineraries</h2>
      </div>

      <div class="dashboard-grid">
        <BaseCard highlight hoverable class="dashboard-card">
          <div class="card-icon">🌸</div>
          <h3>Explore Popular Sights</h3>
          <p>Browse top-rated cultural highlights, historical castle keeps, and beautiful gardens to map out your dream destinations.</p>
          <RouterLink :to="{ name: 'places' }" class="card-action">
            Discover Places →
          </RouterLink>
        </BaseCard>

        <!-- Card 2: Travel Essentials Checklist -->
        <BaseCard hoverable class="dashboard-card">
          <div class="card-icon">🎒</div>
          <h3>Travel Checklist</h3>
          <p>Prepare your baggage optimally: follow our curated list of essentials for an enjoyable stay abroad.</p>
          <BaseButton @click="handleManageChecklist">
            Manage My Checklist
          </BaseButton>
        </BaseCard>

        <!-- Card 3: Saved Travel Guides -->
        <BaseCard hoverable class="dashboard-card">
          <div class="card-icon">🗺️</div>
          <h3>My Saved Itineraries</h3>
          <p>Your saved routes, itineraries, and custom offline guides will be listed here. Explore destinations to compile a guide.</p>
          <BaseButton variant="secondary" @click="handleBrowseGuides">
            Browse Guides
          </BaseButton>
        </BaseCard>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useTours } from '@/composables/useTours'
import BaseCard from '@/components/BaseCard.vue'
import BaseButton from '@/components/BaseButton.vue'

const authStore = useAuthStore()
const { myTours, privateTours, loadMyTours } = useTours()

const totalOptimizedKm = computed(() => {
  const sum = myTours.value.reduce((acc, tour) => {
    const dist = Number(tour.total_distance)
    return acc + (Number.isFinite(dist) ? dist : 0)
  }, 0)
  return sum.toFixed(1)
})

onMounted(async () => {
  if (authStore.isAuthenticated) {
    await loadMyTours()
  }
})

const handleManageChecklist = () => {
  alert('Travel luggage checklist feature coming soon!')
}

const handleBrowseGuides = () => {
  alert('Itinerary guides and offline maps feature coming soon!')
}
</script>

<style scoped>
.dashboard-container {
  padding: 1rem 0;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
  padding-bottom: 2rem;
  border-bottom: 1px solid rgba(229, 231, 235, 0.6);
}

.welcome-section h1 {
  font-size: 2.25rem;
  color: #111827;
  font-weight: 800;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #1e40af, #3b82f6);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.welcome-section .subtitle {
  color: #6b7280;
  font-size: 1.05rem;
}

.quick-status {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: rgba(243, 244, 246, 0.7);
  padding: 0.75rem 1.25rem;
  border-radius: 1rem;
  border: 1px solid rgba(229, 231, 235, 0.8);
}

.avatar-badge {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.1rem;
  box-shadow: 0 4px 10px rgba(59, 130, 246, 0.2);
}

.user-details {
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 700;
  color: #1f2937;
  font-size: 0.95rem;
}

.user-email {
  color: #6b7280;
  font-size: 0.8rem;
}

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
}

.stat-card {
  padding: 1.5rem !important;
  flex-direction: row !important;
  align-items: center;
  gap: 1.25rem;
}

.stat-icon {
  font-size: 2.25rem;
  background: #f3f4f6;
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 1rem;
}

.stat-card.card-highlight .stat-icon {
  background: rgba(59, 130, 246, 0.1);
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 1.75rem;
  font-weight: 800;
  color: #111827;
  line-height: 1.2;
}

.stat-card.card-highlight .stat-number {
  color: #2563eb;
}

.stat-label {
  font-size: 0.8rem;
  color: #6b7280;
  font-weight: 600;
}

/* Dashboard Content & Section Header */
.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
}

.section-header h2 {
  font-size: 1.35rem;
  color: #111827;
  font-weight: 700;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.dashboard-card {
  padding: 2rem !important;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02) !important;
}

.card-icon {
  font-size: 2.5rem;
}

.dashboard-card h3 {
  font-size: 1.25rem;
  color: #111827;
  font-weight: 700;
}

.dashboard-card p {
  color: #4b5563;
  font-size: 0.95rem;
  line-height: 1.6;
  flex: 1;
}

.card-action {
  color: #2563eb;
  font-weight: 600;
  text-decoration: none;
  font-size: 0.95rem;
  transition: transform 0.2s ease;
  align-self: flex-start;
  margin-top: 0.5rem;
}

.card-action:hover {
  transform: translateX(3px);
  color: #1d4ed8;
}

@media (max-width: 640px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
