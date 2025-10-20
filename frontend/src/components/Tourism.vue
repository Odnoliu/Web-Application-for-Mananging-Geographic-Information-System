<template>
  <div class="h-full w-full relative overflow-hidden">
    <!-- Map Container -->
    <div class="h-full w-full" ref="mapContainer"></div>

    <!-- Toggle Button -->
    <button
      class="absolute top-4 z-40 bg-white opacity-80 cursor-pointer rounded-full p-2 shadow hover:bg-gray-100 transition-all duration-300 ease-in-out"
      :class="isSidebarOpen ? 'right-[21%]' : 'right-4'" @click="toggleSidebar">
      <component :is="isSidebarOpen ? ChevronRight : ChevronLeft" class="w-6 h-6" />
    </button>

    <!-- Sidebar -->
    <transition name="slide">
      <div v-if="isSidebarOpen"
        class="fixed top-16.25 right-0 z-30 h-[700px] w-1/5 bg-white shadow-xl border-l p-4 flex flex-col">
        <!-- Tabs -->
        <Tabs default-value="favourites" class="w-full">
          <TabsList class="grid grid-cols-2 gap-2 mb-4 w-full">
            <TabsTrigger value="favourites">
              <Heart class="w-4 h-4 mr-1" /> Favourites
            </TabsTrigger>
            <TabsTrigger value="checkin">
              <MapPin class="w-4 h-4 mr-1" /> Check-ins
            </TabsTrigger>
          </TabsList>

          <!-- FAVOURITES TAB -->
          <TabsContent value="favourites">
            <ScrollArea class="h-full w-full pr-2">
              <ul class="space-y-1">
                <li v-for="favor in display_favourite" :key="favor.properties['@id']" @click="flyToPlace(favor)"
                  class="block px-3 py-2 rounded-md text-sm cursor-pointer text-gray-800 hover:bg-gray-100 transition">
                  <span class="font-medium">{{ favor.properties.name }}</span>
                  <span v-if="favor.properties['name:en']" class="text-gray-500 ml-1">
                    ({{ favor.properties['name:en'] }})
                  </span>
                </li>
              </ul>
            </ScrollArea>
          </TabsContent>

          <!-- CHECK-INS TAB -->
          <TabsContent value="checkin">
            <ScrollArea class="h-full w-full">
              <div class="space-y-3 p-1">
                <div v-if="!checkIns.length"
                  class="flex flex-col items-center justify-center rounded-lg border border-dashed p-8 text-center min-h-[200px]">
                  <h3 class="mt-4 text-sm font-semibold text-gray-800 dark:text-gray-200">No registrations yet</h3>
                  <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">Click on the map to add your first check-in!
                  </p>
                </div>

                <div v-for="ci in checkIns" :key="ci.check_in_id"
                  class="group relative flex gap-4 rounded-lg border bg-white p-3 transition-all hover:border-gray-300 hover:shadow-sm dark:bg-zinc-800/50 dark:border-zinc-700 dark:hover:border-zinc-600">
                  <img v-if="ci.check_in_image" :src="toDataUrl(ci.check_in_image)"
                    class="h-16 w-16 rounded-md object-cover" alt="checkin" />
                  <div v-else
                    class="flex h-16 w-16 items-center justify-center rounded-md bg-gray-100 dark:bg-zinc-700">
                  </div>

                  <div class="flex-1 min-w-0">
                    <div class="flex items-start justify-between">
                      <p class="flex-shrink-0 text-xs text-gray-500 dark:text-gray-400">{{
                        formatTime(ci.created_at) }}</p>
                    </div>

                    <p class="mt-2 text-sm text-gray-700 break-words dark:text-gray-300">{{ ci.check_in_description ||
                      'No description' }}</p>

                    <p class="mt-2 text-xs font-mono text-gray-500 dark:text-gray-400"
                      v-if="ci.longitude && ci.latitude">
                      ({{ ci.latitude.toFixed(5) }}, {{ ci.longitude.toFixed(5) }})
                    </p>

                    <div class="mt-4 flex items-center space-x-2">
                      <button v-tooltip.bottom="'View on Map'" title="View on Map"
                        class="p-1.5 border rounded cursor-pointer bg-white hover:bg-gray-100 dark:bg-zinc-700 dark:border-zinc-600 dark:hover:bg-zinc-600"
                        @click="flyToCheckIn(ci)">
                        <MapPin class="h-4 w-4 text-gray-600 dark:text-gray-300" />
                      </button>
                      <button v-tooltip.bottom="'Edit'" title="Update Check-in"
                        class="p-1.5 border rounded cursor-pointer bg-white hover:bg-gray-100 dark:bg-zinc-700 dark:border-zinc-600 dark:hover:bg-zinc-600"
                        @click="openEditCheckIn(ci)">
                        <Pencil class="h-4 w-4 text-gray-600 dark:text-gray-300" />
                      </button>
                      <button v-tooltip.bottom="'Delete'" title="Delete Check-in"
                        class="p-1.5 border rounded text-red-600 border-red-300 cursor-pointer hover:bg-red-50 hover:text-red-700 dark:bg-red-900/20 dark:border-red-800/50 dark:text-red-400 dark:hover:bg-red-900/50"
                        @click="deleteCheckIn(ci)">
                        <Trash2 class="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </ScrollArea>
          </TabsContent>
        </Tabs>
      </div>
    </transition>

    <!-- AlertDialog for Check-in (Create / Edit reuse) -->
    <AlertDialog v-model:open="showCheckInDialog">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{{ editMode ? 'Update check in' : 'Check-in here!' }}</AlertDialogTitle>
          <AlertDialogDescription>
            {{ editMode ? 'Update your checkin destination.' : 'Enter your check in description' }}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <div class="space-y-4">
          <div>
            <Label for="image" class="mb-2">Image</Label>
            <Input id="image" :required="!editMode" type="file" accept="image/*" @change="handleImageUpload" />
            <img v-if="formData.check_in_image" :src="formData.check_in_image"
              class="mt-2 w-28 h-28 object-cover rounded" />
          </div>
          <div>
            <Label for="description" class="mb-2">Description</Label>
            <Textarea id="description" required v-model="formData.check_in_description"
              placeholder="Enter your description" />
          </div>
        </div>
        <AlertDialogFooter>
          <AlertDialogCancel @click="cancelDialog">Cancel</AlertDialogCancel>
          <AlertDialogAction @click="editMode ? submitUpdateCheckIn() : submitCheckIn()"
            class="bg-sky-400 text-white hover:bg-sky-500 cursor-pointer">
            {{ editMode ? 'Update' : 'Submit' }}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue';
import { createMap, addUserPosition } from '@/modules/mapbox';
import mapboxgl from 'mapbox-gl';
import axios from 'axios';
import { ScrollArea } from '@/components/ui/scroll-area'
import { AlertDialog, AlertDialogContent, AlertDialogHeader, AlertDialogTitle, AlertDialogDescription, AlertDialogFooter, AlertDialogCancel, AlertDialogAction } from '@/components/ui/alert-dialog';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { ChevronLeft, ChevronRight, Heart, MapPin } from 'lucide-vue-next'
import { Pencil, Trash2 } from 'lucide-vue-next';
import { Chart, LineController, LineElement, PointElement, LinearScale, Title, CategoryScale } from 'chart.js';
import Swal from 'sweetalert2';
Chart.register(LineController, LineElement, PointElement, LinearScale, Title, CategoryScale);

// -------------------- STATE --------------------
const isSidebarOpen = ref(false)
const mapContainer = ref<HTMLDivElement | null>(null);
const showCheckInDialog = ref(false);
const checkInCoords = ref<[number, number] | null>(null); // [lng, lat]
const favorites = ref<any[]>([]);
const favoriteMarkers = ref<{ [key: string]: boolean }>({});
const geojson = ref<any>({});
const selectedFeatureId = ref<string | null>(null);
const map = ref<any>(null)
const formData = ref<{ check_in_description: string; check_in_image: string | null }>({ check_in_description: '', check_in_image: null })
const favoritePlaceIds = ref<string[]>([]);

// Check-ins
interface CheckInItem {
  check_in_id: number
  check_in_description?: string | null
  check_in_image?: string | null // base64 (no prefix)
  created_at: string
  updated_at: string
  longitude?: number | null
  latitude?: number | null
  place_id?: string | null
}
const checkIns = ref<CheckInItem[]>([])
const editMode = ref(false)
const editingId = ref<number | null>(null)

// Stats
const statsCanvas = ref<HTMLCanvasElement | null>(null)
let statsChart: Chart | null = null

function toggleSidebar() { isSidebarOpen.value = !isSidebarOpen.value }
const display_favourite = computed(() => favorites.value)

// -------------------- UTILS --------------------
const getPosition = (): Promise<GeolocationPosition> => new Promise((resolve, reject) => {
  if (!navigator.geolocation) reject(new Error('Trình duyệt không hỗ trợ định vị.'));
  else navigator.geolocation.getCurrentPosition(resolve, reject, { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 });
});

const toDataUrl = (base64: string | null | undefined) => base64 ? `data:image/*;base64,${base64}` : ''
const formatTime = (isoStr: string) => new Date(isoStr).toLocaleString()

// Ensure image is loaded before add to map
function loadImageOnce(name: string, url: string): Promise<void> {
  return new Promise((resolve, reject) => {
    if (!map.value) return reject('Map not ready');
    if (map.value.hasImage && map.value.hasImage(name)) return resolve();
    map.value.loadImage(url, (err: any, image: any) => {
      if (err || !image) return reject(err || 'Image missing')
      if (!map.value.hasImage(name)) map.value.addImage(name, image)
      resolve()
    })
  })
}

// Highlight pulse around a point
function pulseAt(lng: number, lat: number) {
  const id = `pulse-${Date.now()}`
  if (!map.value) return
  map.value.addSource(id, { type: 'geojson', data: { type: 'FeatureCollection', features: [{ type: 'Feature', geometry: { type: 'Point', coordinates: [lng, lat] }, properties: {} }] } })
  map.value.addLayer({ id, type: 'circle', source: id, paint: { 'circle-radius': 0, 'circle-color': '#3b82f6', 'circle-opacity': 0.5 } })
  let r = 0
  const intv = setInterval(() => {
    r += 2
    map.value.setPaintProperty(id, 'circle-radius', r)
    map.value.setPaintProperty(id, 'circle-opacity', Math.max(0, 0.5 - r / 50))
    if (r > 50) { clearInterval(intv); if (map.value.getLayer(id)) map.value.removeLayer(id); if (map.value.getSource(id)) map.value.removeSource(id) }
  }, 30)
}

// -------------------- MAP INIT --------------------
onMounted(async () => {
  if (!mapContainer.value) return;
  map.value = createMap(mapContainer.value, { center: [105.769154, 10.031100], zoom: 10, attributionControl: false });

  // Load base icons before any layer uses them
  await Promise.all([
    loadImageOnce('landscape', '/icons/landscape.png'),
    loadImageOnce('checkin', '/icons/checkin.png')
  ]).catch(console.error)

  // Fetch data
  try {
    const geojson_response = await axios.get('http://localhost:8000/service_map/tourism');
    geojson.value = geojson_response.data

    const favRes = await axios.get('http://localhost:8000/favourite-places/by-user', { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } });
    favoritePlaceIds.value = favRes.data.map((item: any) => item.place_id);
    favorites.value = geojson.value.features.filter((f: any) => favoritePlaceIds.value.includes(f.properties['@id']))
    favoritePlaceIds.value.forEach((pid: string) => { favoriteMarkers.value[pid] = true })
  } catch (e) {
    console.error('Lỗi khi tải favorites/geojson:', e)
  }
  await addUserPosition(map.value, 105.769154, 10.031100)

  // Build low/high zoom features for POIs
  try {
    const featuresLowZoom: any[] = []
    const featuresHighZoom: any[] = []
    geojson.value.features.forEach((feature: any) => {
      const { geometry, properties } = feature
      if (!properties.name && !properties['name:en']) return
      let lng: number, lat: number
      if (geometry.type == 'Point') [lng, lat] = geometry.coordinates
      else if (geometry.type == 'Polygon' || geometry.type == 'MultiPolygon') {
        const coords = geometry.type == 'Polygon' ? geometry.coordinates[0][0] : geometry.coordinates[0][0][0]
        ;[lng, lat] = coords
      } else return

      const featureId = properties['@id'] || `${lng}-${lat}`
      const isFavorited = favoriteMarkers.value[featureId] || false
      const baseFeature = { type: 'Feature', geometry: { type: 'Point', coordinates: [lng, lat] }, properties: { ...properties, id: featureId, isFavorited, icon: 'landscape' } }
      if (properties.name && properties['name:en']) featuresLowZoom.push(baseFeature)
      if (properties.name || properties['name:en']) featuresHighZoom.push(baseFeature)
    })

    map.value.on('load', async () => {
      // POI sources
      map.value.addSource('low-zoom-markers', { type: 'geojson', data: { type: 'FeatureCollection', features: featuresLowZoom } })
      map.value.addSource('high-zoom-markers', { type: 'geojson', data: { type: 'FeatureCollection', features: featuresHighZoom } })
      map.value.addLayer({ id: 'low-zoom-layer', type: 'symbol', source: 'low-zoom-markers', layout: { 'icon-image': 'landscape', 'icon-size': 0.05, 'icon-allow-overlap': true, visibility: 'visible' } })
      map.value.addLayer({ id: 'high-zoom-layer', type: 'symbol', source: 'high-zoom-markers', layout: { 'icon-image': 'landscape', 'icon-size': 0.05, 'icon-allow-overlap': true, visibility: 'none' } })

      // Check-in source/layer
      initCheckInLayer()
      await fetchCheckIns() // load user's check-ins and plot

      // Toggle visibility by zoom
      const updateLayerVisibility = () => {
        const z = map.value.getZoom()
        map.value.setLayoutProperty('low-zoom-layer', 'visibility', z < 8 ? 'visible' : 'none')
        map.value.setLayoutProperty('high-zoom-layer', 'visibility', z >= 8 ? 'visible' : 'none')
      }
      updateLayerVisibility()
      map.value.on('zoomend', updateLayerVisibility)

      // Click on POI => popup
      map.value.on('click', ['low-zoom-layer', 'high-zoom-layer'], (e: any) => {
        const feature = e.features?.[0]; if (!feature) return
        const props = feature.properties
        const lngLat = e.lngLat
        const favActive = favoriteMarkers.value[props['@id']] ? 'bg-blue-500 text-white' : 'bg-white border-blue-500 text-blue-500'
        const popupHTML = `
          <div class="popup-custom">
            <p class="font-semibold text-blue-600">Tên (VN): ${props.name || ''}</p>
            ${props['name:en'] ? `<p class="text-green-600">Name (EN): ${props['name:en']}</p>` : ''}
            <div class="flex gap-2 mt-2">
              <button id="favorite-${props['@id']}" class="px-2 py-1 cursor-pointer rounded border ${favActive}" onclick="window.toggleFavorite('${props.name || props['name:en']}', ${lngLat.lng}, ${lngLat.lat}, '${props['@id']}')">
                <span class="mr-1">★</span> Favourite
              </button>
              <button id="checkin-${props['@id']}" class="px-2 py-1 cursor-pointer rounded border bg-white border-yellow-500 text-yellow-500" onclick="window.checkIn(${lngLat.lng}, ${lngLat.lat}, '${props['@id']}')">
                Check in here!
              </button>
            </div>
          </div>`
        new mapboxgl.Popup({ closeButton: true }).setLngLat([lngLat.lng, lngLat.lat]).setHTML(popupHTML).addTo(map.value)
      })

      // Empty click => quick check-in
      map.value.on('click', (e: any) => {
        const feats = map.value.queryRenderedFeatures(e.point, { layers: ['low-zoom-layer', 'high-zoom-layer', 'checkin-layer'] })
        if (feats.length) return
        const { lng, lat } = e.lngLat
        new mapboxgl.Popup({ closeButton: true })
          .setLngLat([lng, lat])
          .setHTML(`<div class="popup-custom"><button class="px-2 py-1 cursor-pointer mt-2 rounded border bg-white border-yellow-500 text-yellow-500" onclick="window.checkIn(${lng}, ${lat}, 'custom')">Check in here!</button></div>`)
          .addTo(map.value)
      })

      // Click on check-in marker => show details popup
      map.value.on('click', 'checkin-layer', (e: any) => {
        const feat = e.features?.[0]; if (!feat) return
        const p = feat.properties
        const id = Number(p.id)
        const ci = checkIns.value.find(x => x.check_in_id === id)
        const img = ci?.check_in_image ? `<img src="${toDataUrl(ci!.check_in_image!)}" class=\"w-40 h-28 object-cover rounded mt-2\"/>` : ''
        const html = `<div class=\"popup-custom\"><div class=\"text-sm\">${ci?.check_in_description || ''}</div>${img}
          <div class=\"flex gap-2 mt-2\"> 
            <button class=\"px-2 py-1 text-xs border rounded\" onclick=\"window.flyToCheckIn(${p.longitude}, ${p.latitude})\">View</button>
            <button class=\"px-2 py-1 text-xs border rounded\" onclick=\"window.openEditCheckIn(${id})\">Update</button>
            <button class=\"px-2 py-1 text-xs border rounded text-red-600 border-red-300\" onclick=\"window.deleteCheckIn(${id})\">Delete</button>
          </div></div>`
        new mapboxgl.Popup({ closeButton: true }).setLngLat(e.lngLat).setHTML(html).addTo(map.value)
      })

    })
  } catch (e) {
    console.error('Lỗi khi tải GeoJSON:', e)
  }
});

// -------------------- CHECK-IN MAP LAYER --------------------
function initCheckInLayer() {
  if (!map.value) return
  if (!map.value.getSource('checkin-source')) {
    map.value.addSource('checkin-source', { type: 'geojson', data: emptyFC() })
  }
  if (!map.value.getLayer('checkin-layer')) {
    map.value.addLayer({ id: 'checkin-layer', type: 'symbol', source: 'checkin-source', layout: { 'icon-image': 'checkin', 'icon-size': 0.07, 'icon-allow-overlap': true } })
  }
}

function emptyFC() { return { type: 'FeatureCollection', features: [] as any[] } }

function updateCheckInSource() {
  if (!map.value || !map.value.getSource('checkin-source')) return
  const feats = checkIns.value.filter(ci => ci.longitude != null && ci.latitude != null).map(ci => ({
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [ci.longitude, ci.latitude] },
    properties: { id: ci.check_in_id, longitude: ci.longitude, latitude: ci.latitude }
  }))
  const src: any = map.value.getSource('checkin-source')
  src.setData({ type: 'FeatureCollection', features: feats })
}

// -------------------- FETCH / CRUD CHECK-IN --------------------
async function fetchCheckIns() {
  try {
    const res = await axios.get('http://localhost:8000/check_in/by-user', { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } })
    // Expecting backend to return optional longitude/latitude/place_id
    console.log(res)
    checkIns.value = (res.data || []).map((x: any) => ({
      check_in_id: x.check_in_id,
      check_in_description: x.check_in_description,
      check_in_image: x.check_in_image ?? null,
      created_at: x.created_at,
      updated_at: x.updated_at,
      longitude: x.longitude ?? null,
      latitude: x.latitude ?? null,
      place_id: x.place_id ?? null,
    }))
    updateCheckInSource()
    await nextTick(); drawStats()
  } catch (e) {
    console.error('Lỗi tải check-ins:', e)
  }
}

// Submit (Create)
async function submitCheckIn() {
  if (!checkInCoords.value) return alert('Thiếu toạ độ check-in!')
  try {
    const payload: any = {
      check_in_description: formData.value.check_in_description,
      check_in_image: formData.value.check_in_image,
      longitude: checkInCoords.value[0],
      latitude: checkInCoords.value[1],
      place_id: selectedFeatureId.value,
    }
    const res = await axios.post('http://localhost:8000/check_in/', payload, { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}`, 'Content-Type': 'application/json' } })
    console.log(res)
    // Merge coords locally (in case backend strips them)
    const created: CheckInItem = {
      check_in_id: res.data.check_in_id,
      check_in_description: res.data.check_in_description,
      check_in_image: res.data.check_in_image,
      created_at: res.data.created_at,
      updated_at: res.data.updated_at,
      longitude: payload.longitude,
      latitude: payload.latitude,
      place_id: payload.place_id
    }
    checkIns.value.unshift(created)
    updateCheckInSource()
    Swal.fire({
      icon: 'success',
      title: 'Success',
      text: 'Check in destination successfully!'
    })
    cancelDialog()
    // Visual pulse
    pulseAt(payload.longitude, payload.latitude)
  } catch (e) {
    console.error('Lỗi khi check-in:', e)
    alert('Check-in thất bại!')
  }
}

function cancelDialog() {
  showCheckInDialog.value = false
  formData.value = { check_in_description: '', check_in_image: null }
  editingId.value = null
  editMode.value = false
}

// Update (Edit)
function openEditCheckIn(ciOrId: CheckInItem | number) {
  const ci = typeof ciOrId === 'number' ? checkIns.value.find(x => x.check_in_id === ciOrId)! : ciOrId
  if (!ci) return
  selectedFeatureId.value = ci.place_id || null
  checkInCoords.value = (ci.longitude != null && ci.latitude != null) ? [ci.longitude, ci.latitude] : null
  formData.value.check_in_description = ci.check_in_description || ''
  formData.value.check_in_image = ci.check_in_image ? toDataUrl(ci.check_in_image) : null
  editingId.value = ci.check_in_id
  editMode.value = true
  showCheckInDialog.value = true
}

async function submitUpdateCheckIn() {
  if (!editingId.value) return
  try {
    const payload: any = { check_in_description: formData.value.check_in_description }
    if (formData.value.check_in_image && formData.value.check_in_image.startsWith('data:image')) {
      payload.check_in_image = formData.value.check_in_image
    }
    // Optional: send updated coords if user re-picked a place (not in this UI)
    if (checkInCoords.value) { payload.longitude = checkInCoords.value[0]; payload.latitude = checkInCoords.value[1] }

    const res = await axios.put(`http://localhost:8000/check_in/${editingId.value}`, payload, { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}`, 'Content-Type': 'application/json' } })
    const idx = checkIns.value.findIndex(x => x.check_in_id === editingId.value)
    if (idx !== -1) {
      checkIns.value[idx] = {
        ...checkIns.value[idx],
        check_in_description: res.data.check_in_description,
        check_in_image: res.data.check_in_image,
        updated_at: res.data.updated_at,
        longitude: payload.longitude ?? checkIns.value[idx].longitude,
        latitude: payload.latitude ?? checkIns.value[idx].latitude,
      }
    }
    updateCheckInSource()
    drawStats()
    Swal.fire({
      icon: 'success',
      title: 'Success',
      text: 'Check in updated successfully!'
    })
    cancelDialog()
  } catch (e) {
    console.error('Lỗi cập nhật check-in:', e)
    alert('Cập nhật thất bại!')
  }
}

// Delete
async function deleteCheckIn(ciOrId: CheckInItem | number) {
  const id = typeof ciOrId === 'number' ? ciOrId : ciOrId.check_in_id
  if (!confirm('Bạn chắc chắn muốn xoá check-in này?')) return
  try {
    await axios.delete(`http://localhost:8000/check_in/${id}`, { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } })
    const idx = checkIns.value.findIndex(x => x.check_in_id === id)
    if (idx !== -1) checkIns.value.splice(idx, 1)
    updateCheckInSource()
    drawStats()
  } catch (e) {
    console.error('Lỗi xoá check-in:', e)
    alert('Xoá thất bại!')
  }
}

// -------------------- IMAGE HANDLING --------------------
const handleImageUpload = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (e) => { formData.value.check_in_image = e.target?.result as string }
  reader.readAsDataURL(file)
}

// -------------------- MAP-FACING GLOBALS --------------------
// Keep using global window callbacks for popup buttons
;(window as any).toggleFavorite = async (name: string, lng: number, lat: number, featureId: string) => {
  const button = document.getElementById(`favorite-${featureId}`)
  if (!button) return
  const isFavorited = favoriteMarkers.value[featureId]
  try {
    if (isFavorited) {
      const encodedId = encodeURIComponent(featureId)
      await axios.delete(`http://localhost:8000/favourite-places/?place_id=${encodedId}`, { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } })
      favoriteMarkers.value[featureId] = false
      favorites.value = favorites.value.filter(f => f.properties['@id'] != featureId)
      favoritePlaceIds.value = favoritePlaceIds.value.filter(f => f != featureId)
      button.className = 'px-2 py-1 rounded border bg-white border-blue-500 text-blue-500'
    } else {
      await axios.post('http://localhost:8000/favourite-places', featureId, { headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` } })
      const found = geojson.value.features.find((f: any) => f.properties['@id'] == featureId)
      if (found && !favoritePlaceIds.value.includes(featureId)) { favorites.value.push(found); favoritePlaceIds.value.push(featureId) }
      favoriteMarkers.value[featureId] = true
      button.className = 'px-2 py-1 rounded border bg-blue-500 text-white'
    }
  } catch (e) {
    console.error('Lỗi cập nhật danh sách yêu thích:', e)
    alert('Cập nhật danh sách yêu thích thất bại!')
  }
}

;(window as any).checkIn = (lng: number, lat: number, featureId: string) => {
  checkInCoords.value = [lng, lat]
  showCheckInDialog.value = true
  selectedFeatureId.value = featureId
  const button = document.getElementById(`checkin-${featureId}`)
  if (button) button.className = 'px-2 py-1 cursor-pointer rounded border bg-yellow-500 text-white'
}

;(window as any).flyToCheckIn = (lng: number, lat: number) => { flyToCheckIn({ longitude: lng, latitude: lat } as any) }
;(window as any).openEditCheckIn = (id: number) => openEditCheckIn(id)
;(window as any).deleteCheckIn = (id: number) => deleteCheckIn(id)

watch(showCheckInDialog, (open) => {
  if (!open) {
    if (selectedFeatureId.value) {
      const btn = document.getElementById(`checkin-${selectedFeatureId.value}`)
      if (btn) btn.className = 'px-2 py-1 cursor-pointer rounded border bg-white border-yellow-500 text-yellow-500'
    }
  }
})

function flyToPlace(favor: any) {
  if (!map.value || !favor.geometry) return
  let coords: any
  if (favor.geometry.type == 'Point') coords = favor.geometry.coordinates
  else {
    const raw = favor.geometry.coordinates
    try { coords = favor.geometry.type === 'Polygon' ? raw[0][0] : raw[0][0][0] } catch { return }
  }
  if (!Array.isArray(coords) || coords.length !== 2) return
  map.value.flyTo({ center: coords, zoom: 14, speed: 1.2, curve: 1.4, essential: true })
  pulseAt(coords[0], coords[1])
}

function flyToCheckIn(ci: Partial<CheckInItem>) {
  if (!map.value || ci.longitude == null || ci.latitude == null) return
  map.value.flyTo({ center: [ci.longitude, ci.latitude], zoom: 15, speed: 1.2, curve: 1.4, essential: true })
  pulseAt(ci.longitude!, ci.latitude!)
}

// -------------------- STATS (Chart.js) --------------------
function drawStats() {
  if (!statsCanvas.value) return
  const last7days: string[] = Array.from({ length: 7 }).map((_, i) => {
    const d = new Date(); d.setDate(d.getDate() - (6 - i)); return d.toISOString().slice(0, 10)
  })
  const counts = last7days.map(day => checkIns.value.filter(ci => (ci.created_at || '').startsWith(day)).length)
  if (statsChart) { statsChart.data.labels = last7days; (statsChart.data.datasets[0].data as number[]) = counts; statsChart.update(); return }
  statsChart = new Chart(statsCanvas.value.getContext('2d')!, { type: 'line', data: { labels: last7days, datasets: [{ label: 'Check-ins', data: counts }] }, options: { responsive: true, maintainAspectRatio: false, plugins: { title: { display: false } }, scales: { x: { display: true }, y: { beginAtZero: true } } } })
}
</script>

<style>
.mapboxgl-popup-content .popup-custom { font-size: 14px; line-height: 1.4; margin-top: 5px; }
.mapboxgl-popup-close-button { font-size: 20px; color: #333; margin-right: 5px; }
.mapboxgl-popup-close-button:hover { color: #ef4444; }
.slide-enter-active, .slide-leave-active { transition: transform 0.3s ease; }
.slide-enter-from { transform: translateX(100%); }
.slide-leave-to { transform: translateX(100%); }
</style>
