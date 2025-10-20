<script setup>
import { ref, computed, watch } from 'vue'
import TileLayer from 'ol/layer/Tile'

const props = defineProps({
  map: Object,
  layerIds: {
    type: Array,
    default: () => []
  }
})

// Danh sách layer nền mặc định
const baseLayers = [
 {
    id: 1, layer_name: "Google Maps"
  },
  {
    id: 2, layer_name: "Mapbox"
  },
  {
    id: 3, layer_name: "CartoDB"
  },
  {
    id: 4, layer_name: "ESRI ArcGIS Online"
  },
]

// Lọc ra danh sách layer cho phép điều khiển (dựa trên props.layerIds)
const filteredLayers = computed(() =>
  baseLayers.filter(layer => props.layerIds.includes(layer.id))
)

// ID của layer đang active
const activeId = ref(filteredLayers.value[0].id || null)

// Hàm kiểm tra và set visible cho các TileLayer có layer_id
const updateTileLayerVisibility = () => {
  if (!props.map) return
  props.map.getLayers().forEach(layer => {
    // Kiểm tra có phải là TileLayer không
    if (layer instanceof TileLayer) {
      const layer_id  = layer.getProperties().layer_id
      if (props.layerIds.includes(layer_id)) {
        layer.setVisible(layer_id == activeId.value)
      }
    }
  })
}

// Gọi khi activeId thay đổi hoặc khi map đã mount
watch(
  () => activeId.value,
  () => updateTileLayerVisibility(),
  { immediate: true }
)
</script>

<template>
  <div class="flex gap-2 p-2 bg-white/80 rounded-md shadow">
    <button
      v-for="layer in filteredLayers"
      :key="layer.id"
      @click="activeId = layer.id"
      :class="[
        'px-3 py-1 rounded text-sm font-medium hover:cursor-pointer',
        activeId == layer.id
          ? 'bg-blue-600 text-white'
          : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
      ]"
    >
      {{ layer.layer_name }}
    </button>
    <button @click="activeId = 0"
      :class="[
        'px-3 py-1 rounded text-sm font-medium hover:cursor-pointer',
        activeId == 0
          ? 'bg-blue-600 text-white'
          : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
      ]">
    None
    </button>
  </div>
</template>
