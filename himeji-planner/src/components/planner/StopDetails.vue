<script setup>
import BaseCard from '../BaseCard.vue';

const infos = defineProps({
    stop: Object,
    hasIndex: Boolean,
    index: Number
})

const emit = defineEmits(['delete'])
</script>

<template>
    <li class="route-stop" :id="'tourStop'+index">
        <BaseCard hoverable class="place-card">
            <div class="stop-indicator" v-if="hasIndex">
                <span class="stop-number">{{ index + 1 }}</span>
            </div>
            <div class="stop-details">
                <h3>{{ stop['name'] }}</h3>
                <p>Lat: {{ stop['latitude'] }} | Lng: {{ stop['longitude'] }}</p>
                <button class="deleteButton" @click="emit('delete')">Supprimer</button>
            </div>
        </BaseCard>
    </li>
</template>

<style scoped>
.route-stop {
  display: flex;
  align-items: flex-start; /* Align top so the line starts exactly at the circle */
  gap: 1rem;
  position: relative;
  padding-bottom: 1.5rem; /* Space between the stops */
}

.deleteButton {
    padding: 5px 10px;
    border-radius: 50px;
    border: 1px solid red;
    color: red;
    transition:.25s;
    margin-top:15px;
}
.deleteButton:hover {
    color:white;
    background-color: red;
}

/* The vertical line connecting the dots */
.route-stop:not(:last-child)::after {
  content: '';
  position: absolute;
  top: 3rem; /* Start just below the number circle */
  left: 15rem; /* Center of the 2rem circle */
  height: 2px;
  width: calc(100% + 1rem); /* Stretch to the bottom of the padding */
  background-color: #cbd5e1; /* Light gray line */
  transform: translateX(-50%);
  z-index: -1;
  overflow-x:visible;
}
.route-stop:not(:last-child):nth-child(3n)::after {
    border-top:2px dotted transparent;
    background: linear-gradient(transparent, transparent) padding-box,
              linear-gradient(to right, #cbd5e1, transparent) border-box;
    height:0px;
}

.route-stop:not(:first-child):nth-child(3n+1)::before {
    content: '';
    position: absolute;
    top: 3rem; /* Start just below the number circle */
    left: 4rem; /* Center of the 2rem circle */
    width: calc(100% - 3rem); /* Stretch to the bottom of the padding */
    background-color: #cbd5e1; /* Light gray line */
    transform: translateX(-50%);
    z-index: -1;
    overflow-x:visible;
    border-top:2px dotted transparent;
    background: linear-gradient(transparent, transparent) padding-box,
                linear-gradient(to left, #cbd5e1, transparent) border-box;
    height:0px;
}

.stop-indicator {
  position: relative;
  z-index: 1; /* Keep the circle above the line */
}

.stop-number {
  background-color: #111827;
  color: white;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-weight: bold;
}

.stop-details {
  padding-top: 0.25rem; /* Vertically align text with the circle */
}

.stop-details h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #1f2937;
  font-weight: 700;
}

.stop-details p {
  margin: 0;
  font-size: 0.85rem;
  color: #6b7280;
}</style>