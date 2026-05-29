
    
<template>
    <button class="place-card-button" type="button" @click="$emit('select')">
      <BaseCard hoverable class="place-card">
        <div class="place-content">
          <h3>{{ name }}</h3>
          <div class="place-meta">
            <span class="meta-item">{{ city }}</span>
            <span class="meta-item">{{ latitude }} | {{ longitude }}</span>
          </div>
        </div>
      </BaseCard>
    </button>
</template>

<script setup>
import BaseCard from '../BaseCard.vue';

defineProps({
  name: String,
  city: String,
  latitude: Number,
  longitude: Number
})

defineEmits(['select'])
</script>

<style scoped>
.place-card-button {
  width: 100%;
  padding: 0;
  border: 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
}

.base-card {
  background: #ffffff;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.01);
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  width:100%;

  background: linear-gradient(white, white) padding-box,
              linear-gradient(135deg, #047857, #10b981) border-box;
  border-radius: 1rem;
  border: 1px solid transparent;
}

.card-highlight {
  background: linear-gradient(135deg, #eff6ff, #ffffff);
  border-color: rgba(191, 219, 254, 0.8);
}

.card-hoverable:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px -4px rgba(0, 0, 0, 0.06), 0 4px 12px -2px rgba(0, 0, 0, 0.03);
  border-color: rgba(59, 130, 246, 0.2);
}

.place-content .meta-item {
    color: lightgray;
}
.place-content .meta-item:last-child {
    float :right;
}
</style>
