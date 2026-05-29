<template>
  <button 
    :type="type" 
    class="base-btn" 
    :class="`btn-${variant}`"
    :disabled="disabled || loading"
  >
    <span v-if="loading" class="spinner"></span>
    <span v-else><slot /></span>
  </button>
</template>

<script setup>
defineProps({
  type: {
    type: String,
    default: 'button'
  },
  variant: {
    type: String,
    default: 'primary' // 'primary' or 'secondary'
  },
  loading: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  }
})
</script>

<style scoped>
.base-btn {
  padding: 0.8rem 1.5rem;
  border-radius: 0.75rem;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-primary {
  background: linear-gradient(135deg, #a15aa3, #f77acd);
  color: #ffffff;
  border: none;
  box-shadow: 0 4px 12px rgba(219, 37, 235, 0.2);
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #a15aa3, #f77acd);
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(235, 37, 219, 0.3);
}

.btn-secondary {
  background: #ffffff;
  color: #374151;
  border: 1.5px solid #d1d5db;
}

.btn-secondary:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #9ca3af;
  color: #111827;
  transform: translateY(-1px);
}

.base-btn:active:not(:disabled) {
  transform: translateY(0);
}

.base-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

/* Loading Spinner */
.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: currentColor;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
