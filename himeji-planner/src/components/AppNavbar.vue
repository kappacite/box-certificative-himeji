<template>
  <nav class="navbar">
    <div class="navbar-container">
      <!-- Logo / Brand -->
      <div class="navbar-brand">
        <RouterLink to="/" class="brand-link" @click="closeAllMenus">
          <span class="brand-icon">🌸</span>
          <span class="brand-text">Himeji Planner</span>
        </RouterLink>
      </div>

      <!-- Desktop Navigation Menu -->
      <div class="navbar-menu-desktop">
        <!-- Authenticated Navigation -->
        <template v-if="authStore.isAuthenticated">
          <RouterLink :to="{ name: 'dashboard' }" class="nav-link">
            <span>Dashboard</span>
          </RouterLink>
          <RouterLink :to="{ name: 'places' }" class="nav-link">
            <span>Places to visit</span>
          </RouterLink>
          <RouterLink :to="{ name: 'planner' }" class="nav-link">
            <span>Planify Travel</span>
          </RouterLink>
        </template>

        <!-- Guest Navigation -->
        <template v-else>
          <RouterLink :to="{ name: 'login' }" class="nav-link">
            Log In
          </RouterLink>
          <RouterLink :to="{ name: 'register' }" class="nav-btn-signup">
            Register
          </RouterLink>
        </template>

        <!-- Profile Dropdown (Authenticated) -->
        <div v-if="authStore.isAuthenticated" class="profile-container" v-click-outside="closeProfile">
          <button @click="toggleProfile" class="profile-trigger" aria-label="User menu">
            <div class="avatar">{{ authStore.user?.avatarInitials }}</div>
            <span class="username-text">{{ authStore.user?.username }}</span>
            <span class="chevron" :class="{ 'chevron-rotated': isProfileOpen }">▼</span>
          </button>
          
          <Transition name="dropdown-slide">
            <div v-if="isProfileOpen" class="profile-dropdown">
              <div class="dropdown-header">
                <p class="user-fullname">{{ authStore.user?.username }}</p>
                <p class="user-email">{{ authStore.user?.email }}</p>
              </div>
              <div class="dropdown-divider"></div>
              <button @click="handleLogout" class="dropdown-item logout-item">
                <span class="item-icon">🚪</span>
                <span>Logout</span>
              </button>
            </div>
          </Transition>
        </div>
      </div>

      <!-- Mobile Hamburger Button -->
      <button 
        class="hamburger-btn" 
        @click="toggleMobileMenu" 
        :class="{ 'is-active': isMobileMenuOpen }"
        aria-label="Open menu"
      >
        <span class="hamburger-line"></span>
        <span class="hamburger-line"></span>
        <span class="hamburger-line"></span>
      </button>
    </div>

    <!-- Mobile Navigation Drawer -->
    <Transition name="drawer-slide">
      <div v-if="isMobileMenuOpen" class="navbar-menu-mobile">
        <div class="mobile-links">
          <!-- Authenticated -->
          <template v-if="authStore.isAuthenticated">
            <div class="mobile-user-card">
              <div class="avatar large">{{ authStore.user?.avatarInitials }}</div>
              <div class="mobile-user-info">
                <p class="user-fullname">{{ authStore.user?.username }}</p>
                <p class="user-email">{{ authStore.user?.email }}</p>
              </div>
            </div>
            <div class="dropdown-divider"></div>
            <RouterLink :to="{ name: 'dashboard' }" class="mobile-nav-link" @click="closeAllMenus">
              🇯🇵 Dashboard
            </RouterLink>
            <RouterLink :to="{ name: 'places' }" class="mobile-nav-link" @click="closeAllMenus">
              🌸 Places to visit
            </RouterLink>
            <div class="dropdown-divider"></div>
            <button @click="handleLogout" class="mobile-logout-btn">
              🚪 Logout
            </button>
          </template>

          <!-- Guest -->
          <template v-else>
            <RouterLink :to="{ name: 'login' }" class="mobile-nav-link" @click="closeAllMenus">
              Log In
            </RouterLink>
            <RouterLink :to="{ name: 'register' }" class="mobile-btn-signup" @click="closeAllMenus">
              Register
            </RouterLink>
          </template>
        </div>
      </div>
    </Transition>
  </nav>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const authStore = useAuthStore()

const isProfileOpen = ref(false)
const isMobileMenuOpen = ref(false)

const toggleProfile = () => {
  isProfileOpen.value = !isProfileOpen.value
}

const closeProfile = () => {
  isProfileOpen.value = false
}

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

const closeAllMenus = () => {
  isProfileOpen.value = false
  isMobileMenuOpen.value = false
}

const handleLogout = () => {
  closeAllMenus()
  authStore.logout()
  router.push({ name: 'login' })
}

// Custom click outside directive for dropdown dismissal
const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value(event)
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent)
  }
}
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.75);
  backdrop-filter: blur(16px) saturate(180%);
  border-bottom: 1px solid rgba(229, 231, 235, 0.5);
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.02);
  transition: all 0.3s ease;
}

.navbar-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0.85rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Brand styling */
.navbar-brand .brand-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  font-weight: 800;
  font-size: 1.35rem;
  color: #111827;
  transition: transform 0.2s ease;
}

.navbar-brand .brand-link:hover {
  transform: scale(1.02);
}

.brand-icon {
  font-size: 1.5rem;
  filter: drop-shadow(0 2px 5px rgba(219, 39, 119, 0.2));
  animation: floatIcon 3s ease-in-out infinite;
}

.brand-text {
  background: linear-gradient(135deg, #1f2937 0%, #1e40af 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Desktop Menu */
.navbar-menu-desktop {
  display: flex;
  align-items: center;
  gap: 1.75rem;
}

.nav-link {
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
  color: #4b5563;
  position: relative;
  padding: 0.5rem 0.25rem;
  transition: color 0.25s ease;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  transition: width 0.25s ease;
  border-radius: 2px;
}

.nav-link:hover {
  color: #2563eb;
}

.nav-link:hover::after,
.nav-link.router-link-active::after {
  width: 100%;
}

.nav-link.router-link-active {
  color: #2563eb;
  font-weight: 700;
}

.nav-btn-signup {
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
  padding: 0.6rem 1.25rem;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: white;
  border-radius: 0.75rem;
  box-shadow: 0 4px 10px rgba(37, 99, 235, 0.2);
  transition: all 0.25s ease;
}

.nav-btn-signup:hover {
  background: linear-gradient(135deg, #1d4ed8, #1e40af);
  transform: translateY(-1px);
  box-shadow: 0 6px 14px rgba(37, 99, 235, 0.3);
}

.nav-btn-signup:active {
  transform: translateY(0);
}

/* Profile Dropdown */
.profile-container {
  position: relative;
}

.profile-trigger {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  background: rgba(243, 244, 246, 0.7);
  border: 1px solid rgba(229, 231, 235, 0.8);
  padding: 0.4rem 0.85rem;
  border-radius: 2rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.profile-trigger:hover {
  background: rgba(229, 231, 235, 0.9);
  border-color: rgba(209, 213, 219, 0.8);
}

.avatar {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: white;
  font-weight: 700;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25);
}

.avatar.large {
  width: 50px;
  height: 50px;
  font-size: 1.25rem;
}

.username-text {
  font-size: 0.925rem;
  font-weight: 600;
  color: #374151;
}

.chevron {
  font-size: 0.65rem;
  color: #9ca3af;
  transition: transform 0.2s ease;
}

.chevron-rotated {
  transform: rotate(180deg);
}

.profile-dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 0.75rem);
  width: 240px;
  background: #ffffff;
  border: 1px solid rgba(229, 231, 235, 0.8);
  border-radius: 1rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08), 
              0 8px 10px -6px rgba(0, 0, 0, 0.03);
  overflow: hidden;
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
}

.dropdown-header {
  padding: 0.75rem 1rem;
}

.user-fullname {
  font-weight: 700;
  color: #111827;
  font-size: 0.95rem;
}

.user-email {
  color: #6b7280;
  font-size: 0.775rem;
  word-break: break-all;
}

.dropdown-divider {
  height: 1px;
  background: #f3f4f6;
  margin: 0.4rem 0.5rem;
}

.dropdown-item {
  width: 100%;
  background: transparent;
  border: none;
  border-radius: 0.5rem;
  padding: 0.65rem 0.75rem;
  text-align: left;
  display: flex;
  align-items: center;
  gap: 0.65rem;
  font-size: 0.9rem;
  font-weight: 600;
  color: #4b5563;
  cursor: pointer;
  transition: all 0.15s ease;
}

.dropdown-item:hover {
  background: #f9fafb;
  color: #111827;
}

.logout-item {
  color: #dc2626;
}

.logout-item:hover {
  background: #fef2f2;
  color: #b91c1c;
}

/* Mobile Hamburger Button */
.hamburger-btn {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  width: 22px;
  height: 16px;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0;
  z-index: 101;
}

.hamburger-line {
  width: 100%;
  height: 2px;
  background-color: #374151;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.hamburger-btn.is-active .hamburger-line:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}

.hamburger-btn.is-active .hamburger-line:nth-child(2) {
  opacity: 0;
}

.hamburger-btn.is-active .hamburger-line:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

/* Mobile Menu Mobile Drawer */
.navbar-menu-mobile {
  display: none;
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(229, 231, 235, 0.7);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  padding: 1.5rem 2rem;
}

.mobile-links {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.mobile-user-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem 0;
}

.mobile-user-info {
  display: flex;
  flex-direction: column;
}

.mobile-nav-link {
  text-decoration: none;
  font-size: 1.05rem;
  font-weight: 600;
  color: #374151;
  padding: 0.5rem 0;
  transition: color 0.15s ease;
}

.mobile-nav-link:hover,
.mobile-nav-link.router-link-active {
  color: #2563eb;
}

.mobile-btn-signup {
  text-decoration: none;
  text-align: center;
  font-weight: 600;
  padding: 0.75rem;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  color: white;
  border-radius: 0.75rem;
}

.mobile-logout-btn {
  width: 100%;
  background: transparent;
  border: none;
  text-align: left;
  font-size: 1.05rem;
  font-weight: 600;
  color: #dc2626;
  padding: 0.5rem 0;
  cursor: pointer;
}

/* Animations & Transitions */
@keyframes floatIcon {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-2px);
  }
}

.dropdown-slide-enter-active,
.dropdown-slide-leave-active {
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.dropdown-slide-enter-from {
  opacity: 0;
  transform: translateY(-8px) scale(0.97);
}

.dropdown-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.97);
}

.drawer-slide-enter-active,
.drawer-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}

.drawer-slide-enter-from,
.drawer-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* Media Queries for Responsiveness */
@media (max-width: 768px) {
  .navbar-menu-desktop {
    display: none;
  }
  
  .hamburger-btn {
    display: flex;
  }
  
  .navbar-menu-mobile {
    display: block;
  }
}
</style>
