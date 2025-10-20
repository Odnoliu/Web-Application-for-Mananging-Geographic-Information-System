<template>
  <div class="h-full w-full" ref="mapContainer"></div>
</template>

<script setup lang="ts">
import { onMounted, ref, h } from 'vue';
import { createMap, addMarker, getIconClass } from '@/modules/mapbox';
import axios from 'axios';
const mapContainer = ref<HTMLDivElement | null>(null);
import mapboxgl from 'mapbox-gl';

onMounted(async () => {
  if (!mapContainer.value) return;

  const map = createMap(mapContainer.value, {
    center: [108.2772, 16.083],
    zoom: 5,
    attributionControl: false,
  });

  const markersLowZoom: mapboxgl.Marker[] = [];
  const markersHighZoom: mapboxgl.Marker[] = [];

  try {
    const response = await axios.get('http://localhost:8000/service_map/market');
    const geojson = response.data;

    geojson.features.forEach((feature: any) => {
      const { geometry, properties } = feature;
      if (!properties.name) return;

      let lng: number, lat: number;
      if (geometry.type == 'Point') {
        [lng, lat] = geometry.coordinates;
      } else if (geometry.type == 'Polygon' || geometry.type == 'MultiPolygon') {
        const coords = geometry.type == 'Polygon'
          ? geometry.coordinates[0][0]
          : geometry.coordinates[0][0][0];
        [lng, lat] = coords;
      } else {
        return;
      }

      // Popup HTML
      const popupHTML = `
        <div class="popup-custom">
          <p class="font-semibold text-blue-600">Tên (VN): ${properties.name}</p>
          ${properties['name:en'] ? `<p class="text-green-600">Name (EN): ${properties['name:en']}</p>` : ''}
        </div>
      `;

      // Tạo DOM marker
      const el = document.createElement('div');
      el.className = 'marker-image';
      el.style.backgroundImage = "url('/icons/market.png')";
      el.style.width = '24px';
      el.style.height = '24px';
      el.style.backgroundSize = 'cover';
      el.style.borderRadius = '30%';

      const marker = new mapboxgl.Marker({ element: el })
        .setLngLat([lng, lat])
        .setPopup(new mapboxgl.Popup({ closeButton: true }).setHTML(popupHTML));

      // Phân loại marker
      if (properties['name:en']) {
        markersLowZoom.push(marker);
      } else {
        markersHighZoom.push(marker);
      }
    });

    // Hàm cập nhật hiển thị marker theo zoom
    const updateMarkers = () => {
      const zoom = map.getZoom();

      if (zoom < 8) {
        markersLowZoom.forEach(marker => marker.addTo(map));
        markersHighZoom.forEach(marker => marker.remove());
      } else {
        markersHighZoom.forEach(marker => marker.addTo(map));
        markersLowZoom.forEach(marker => marker.remove());
      }
    };

    // Gọi ban đầu
    updateMarkers();

    // Lắng nghe sự kiện zoom
    map.on('zoomend', updateMarkers);

  } catch (error) {
    console.error('Lỗi khi tải GeoJSON:', error);
  }
});
</script>

<style>
.marker {
  display: flex;
  align-items: center;
  justify-content: center;
}
.mapboxgl-popup-content .popup-custom {
  font-size: 14px;
  line-height: 1.4;
  margin-top: 5px;
}
.mapboxgl-popup-close-button {
  font-size: 20px;
  color: #333;
  margin-right: 5px;
}
.mapboxgl-popup-close-button:hover {
  color: #ef4444;
}
</style>