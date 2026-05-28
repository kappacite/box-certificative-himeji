<template>
  <div class="map-wrapper">
    <div id="tour-map" class="map-container"></div>
  </div>
</template>

<script setup>
import { onMounted, watch, onUnmounted } from 'vue'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'

const props = defineProps({
  route: {
    type: Array,
    required: true,
    default: () => []
  }
})

let map = null
let routeLayer = null

// Fix for missing default marker icons in Leaflet with Vite
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: new URL('leaflet/dist/images/marker-icon-2x.png', import.meta.url).href,
  iconUrl: new URL('leaflet/dist/images/marker-icon.png', import.meta.url).href,
  shadowUrl: new URL('leaflet/dist/images/marker-shadow.png', import.meta.url).href,
})

const renderMap = () => {
  if (!map) {
    map = L.map('tour-map').setView([0, 0], 2)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map)
  }

  // Clear previous layers if any
  if (routeLayer) {
    map.removeLayer(routeLayer)
  }

  if (props.route && props.route.length > 0) {
    const latlngs = props.route.map(stop => [stop.latitude, stop.longitude])
    
    // Group markers and polyline into one layer
    const layers = latlngs.map((latlng, index) => {
      return L.marker(latlng).bindPopup(`<b>Stop ${index + 1}</b><br>${props.route[index].name}`)
    })
    
    // Draw line between markers
    const polyline = L.polyline(latlngs, { color: '#2563eb', weight: 4 })
    layers.push(polyline)

    routeLayer = L.featureGroup(layers).addTo(map)
    
    // Adjust map zoom and position to fit the route
    map.fitBounds(routeLayer.getBounds(), { padding: [50, 50] })
  }
}

onMounted(() => {
  renderMap()
})

// Reactively update map when the route changes
watch(() => props.route, () => {
  renderMap()
}, { deep: true })

onUnmounted(() => {
  if (map) {
    map.remove()
  }
})
</script>

<style scoped>
.map-wrapper {
  width: 100%;
  height: 400px;
  border-radius: 0.5rem;
  overflow: hidden;
  border: 1px solid #e5e7eb;
  z-index: 1; /* Keep leaflet controls below custom overlays if any */
}

.map-container {
  width: 100%;
  height: 100%;
}
</style>