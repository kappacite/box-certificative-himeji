<template>
  <div 
    class="base-card" 
    :class="{ 
      'card-highlight': highlight, 
      'card-hoverable': hoverable 
    }"
  >
    <slot />
  </div>
</template>

<script setup>
defineProps({
  highlight: {
    type: Boolean,
    default: false
  },
  hoverable: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.base-card {
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 1.25rem;
  padding: 2rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.01);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card-highlight {
  background: linear-gradient(135deg, #ffeffe, #ffffff);
  border-color: rgba(254, 191, 251, 0.8);
}

.card-hoverable:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -4px rgba(0, 0, 0, 0.06), 0 4px 12px -2px rgba(0, 0, 0, 0.03);
  border-color: rgba(59, 130, 246, 0.2);
}
</style>
