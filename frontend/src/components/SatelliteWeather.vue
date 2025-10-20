<template>
  <div class="relative h-screen w-screen">
    <!-- Map container -->
    <div ref="mapContainer" class="h-full w-full"></div>

    <!-- Loading spinner -->
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-white/70 z-20">
      <div class="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600"></div>
    </div>

    <!-- Control panel (dính theo map, nằm trong map container) -->
    <div class="absolute top-4 left-4 bg-white shadow-lg rounded-xl p-3 z-10 flex items-center gap-2">
      <button @click="exportGeoJSON" class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">
        Export GeoJSON
      </button>

      <!-- Nút mở biểu đồ bằng AlertDialog -->
      <AlertDialog>
        <AlertDialogTrigger as-child>
          <button
            class="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-gray-200 hover:bg-gray-50 transition"
            aria-label="Open charts" title="Open charts">
            <BarChart3 class="w-5 h-5" />
            Charts
          </button>
        </AlertDialogTrigger>

        <AlertDialogContent class="!w-[1200px] !h-[700px] !max-w-none">
          <!-- Header -->
          <AlertDialogHeader class="mb-2">
            <AlertDialogTitle class="text-xl">Disaster Statistics</AlertDialogTitle>
            <AlertDialogDescription>
              Summary of disasters grouped by country.
            </AlertDialogDescription>
          </AlertDialogHeader>

          <!-- Toolbar chọn loại biểu đồ -->
          <div class="flex items-center gap-3 mb-4">
            <label class="text-sm text-gray-600">Chart type</label>
            <select v-model="selectedChart" class="border rounded-lg px-3 py-2">
              <option value="bar">Bar Chart</option>
              <option value="area">Area Chart</option>
              <option value="pie">Pie Chart</option>
            </select>
          </div>

          <!-- Khu vực biểu đồ: rộng và cao hơn -->
          <div class="w-full min-w-0">
            <div class="w-full h-[520px]">
              <component :is="currentChartComponent" :data="chartData" />
            </div>
          </div>

          <!-- Button Close ở góc trên phải -->
          <AlertDialogCancel as-child>
            <button class="absolute top-3 right-3 text-gray-500 hover:text-gray-800">
              ✕
            </button>
          </AlertDialogCancel>
        </AlertDialogContent>

      </AlertDialog>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from "vue";
import axios from "axios";
import mapboxgl from "mapbox-gl";

/* shadcn-vue */
import {
  AlertDialog,
  AlertDialogTrigger,
  AlertDialogContent,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogCancel,
} from "@/components/ui/alert-dialog";

/* lucide icon (Vue) */
import { BarChart3 } from "lucide-vue-next";

/* Charts */
import BarChart from "../components/Charts/BarChart.vue";
import AreaChart from "../components/Charts/AreaChart.vue";
import PieChart from "../components/Charts/PieChart.vue";

const mapContainer = ref(null);
const map = ref(null);
const geojsonData = ref(null);
const loading = ref(true);

/* state cho dialog chart */
const selectedChart = ref("bar"); // mặc định BarChart
const currentChartComponent = computed(() => {
  return selectedChart.value === "area"
    ? AreaChart
    : selectedChart.value === "pie"
    ? PieChart
    : BarChart;
});

onMounted(async () => {
  await nextTick(); // đảm bảo mapContainer là HTMLElement

  mapboxgl.accessToken =
    "pk.eyJ1IjoicHBodWNqcyIsImEiOiJjbTV5emdvNWUwbjhhMmpweXAybThmbmVhIn0.4PA9RDEf2HFu7jMuicJ1OQ";

  // Tạo map
  map.value = new mapboxgl.Map({
    container: mapContainer.value,
    style: "mapbox://styles/mapbox/light-v11",
    center: [0, 0],
    zoom: 2,
  });

  // Chờ map load xong
  await new Promise((resolve) => map.value.on("load", resolve));

  // Fetch dữ liệu từ API
  const res = await axios.get(
    "https://www.gdacs.org/gdacsapi/api/events/geteventlist/EVENTS4APP"
  );

  // Lưu dữ liệu
  geojsonData.value = {
    type: "FeatureCollection",
    features: res.data.features || [],
  };

  // Add source
  map.value.addSource("disasters", {
    type: "geojson",
    data: geojsonData.value,
  });

  // Layer Point
  map.value.addLayer({
    id: "disasters-points",
    type: "circle",
    source: "disasters",
    filter: ["==", ["geometry-type"], "Point"],
    paint: {
      "circle-radius": 6,
      "circle-color": [
        "match",
        ["get", "alertlevel"],
        "Red",
        "#e11d48",
        "Orange",
        "#f97316",
        "Green",
        "#10b981",
        /* default */ "#3b82f6",
      ],
      "circle-stroke-width": 1,
      "circle-stroke-color": "#fff",
    },
  });

  // Layer LineString
  map.value.addLayer({
    id: "disasters-lines",
    type: "line",
    source: "disasters",
    filter: ["==", ["geometry-type"], "LineString"],
    paint: {
      "line-width": 2,
      "line-color": "#f59e0b",
    },
  });

  // Layer Polygon
  map.value.addLayer({
    id: "disasters-polygons",
    type: "fill",
    source: "disasters",
    filter: ["==", ["geometry-type"], "Polygon"],
    paint: {
      "fill-color": "#3b82f6",
      "fill-opacity": 0.3,
    },
  });

  // Popup khi click
  map.value.on("click", "disasters-points", (e) => showPopup(e));
  map.value.on("click", "disasters-lines", (e) => showPopup(e));
  map.value.on("click", "disasters-polygons", (e) => showPopup(e));

  // Cursor pointer khi hover
  ["disasters-points", "disasters-lines", "disasters-polygons"].forEach(
    (layer) => {
      map.value.on("mouseenter", layer, () => {
        map.value.getCanvas().style.cursor = "pointer";
      });
      map.value.on("mouseleave", layer, () => {
        map.value.getCanvas().style.cursor = "";
      });
    }
  );

  loading.value = false; // tắt spinner
});

// Popup
const showPopup = (e) => {
  const feature = e.features[0];
  const p = feature.properties || {};
  let reportUrl = "";
  try {
    const parsed = typeof p.url === "string" ? JSON.parse(p.url) : p.url;
    reportUrl = parsed?.report || "";
  } catch (err) {
    reportUrl = "";
  }

  const html = `
    <div class="p-3 rounded-lg max-w-xs space-y-2">
      <h3 class="text-lg font-bold text-gray-900">${p.name || "Unknown Event"}</h3>
      <p class="text-base text-gray-700">${p.htmldescription || ""}</p>
      <p class="text-base text-gray-800">
        <span class="font-semibold">Severity:</span> ${
          p.severitydata?.severitytext || "N/A"
        }
      </p>
      ${
        reportUrl
          ? `<a href="${reportUrl}" target="_blank" class="text-blue-600 hover:underline text-base">📄 View Report</a>`
          : ""
      }
    </div>
  `;

  new mapboxgl.Popup({ offset: 25 })
    .setLngLat(e.lngLat)
    .setHTML(html)
    .addTo(map.value);
};

// Export dữ liệu
const exportGeoJSON = () => {
  if (!geojsonData.value) return;
  const blob = new Blob([JSON.stringify(geojsonData.value)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "Aug_disasters.geojson";
  a.click();
};

/* Dữ liệu cho biểu đồ: thống kê số thiên tai theo quốc gia */
const chartData = computed(() => {
  if (!geojsonData.value) return [];
  const counts = {};
  for (const f of geojsonData.value.features) {
    const c = f.properties?.country?.trim() || "Unknown";
    counts[c] = (counts[c] || 0) + 1;
  }
  // chuyển về [{ year: country, count }]
  return Object.entries(counts)
    .map(([country, count]) => ({ year: country, count }))
    .sort((a, b) => b.count - a.count);
});

onUnmounted(() => {
  if (map.value) map.value.remove();
});
</script>
