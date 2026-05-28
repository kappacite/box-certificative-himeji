<template>
  <div class="notfound-container">
    <BaseCard class="notfound-card">
      <span class="notfound-icon">🧭</span>
      <h1>404</h1>
      <h2>Page Not Found</h2>
      <p>The travel path you are looking for does not exist or has been relocated. Let's get you back on track!</p>
      
      <BaseButton @click="router.push({ name: 'Home' })">
        Go Back Home
      </BaseButton>
    </BaseCard>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import BaseCard from '@/components/BaseCard.vue'
import BaseButton from '@/components/BaseButton.vue'

const router = useRouter()
</script>

<style scoped>
.notfound-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 160px);
  padding: 1rem;
}

.notfound-card {
  width: 100%;
  max-width: 460px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.25rem;
  animation: scaleUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.notfound-icon {
  font-size: 3.5rem;
  animation: spinSlow 8s linear infinite;
}

.notfound-card h1 {
  font-size: 4rem;
  font-weight: 800;
  line-height: 1;
  background: linear-gradient(135deg, #ef4444, #db2777);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0;
}

.notfound-card h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.notfound-card p {
  color: #6b7280;
  font-size: 0.95rem;
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

@keyframes scaleUp {
  from {
    opacity: 0;
    transform: scale(0.96);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes spinSlow {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>