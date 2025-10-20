<script setup>
import { ref, computed, watch, onMounted, nextTick } from 'vue';
import { Pencil, X, Dot, Spline, Hexagon, Circle, Save, Trash2 } from 'lucide-vue-next';

// OpenLayers imports
import Draw from 'ol/interaction/Draw';
import VectorSource from 'ol/source/Vector';
import VectorLayer from 'ol/layer/Vector';
import GeoJSON from 'ol/format/GeoJSON';
import Overlay from 'ol/Overlay';
import { fromCircle } from 'ol/geom/Polygon';
import { addFeaturetoUserLayer } from '@/modules/openlayer';
// Shadcn-vue AlertDialog for delete confirmation
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import Button from '../ui/button/Button.vue';
import axios from 'axios';
import { toLonLat } from 'ol/proj'
import { transform } from 'ol/proj';
import Swal from 'sweetalert2'
// Import hàm mới từ openlayer.ts
// import { addFeatureToLayer } from '@/path/to/your/openlayer.ts'; // <-- THAY ĐỔI ĐƯỜNG DẪN

const props = defineProps({
  map: Object,
  userData: { 
    type: Array,
    default: () => [],
  },
});

const emit = defineEmits(['update:drawing', 'update:savingFeature']);

// --- State cũ ---
const isOpen = ref(false);
const drawInteraction = ref(null);
const drawing = ref(false);
const vectorSource = ref(new VectorSource()); // Đây là layer tạm để vẽ
const vectorLayer = ref(new VectorLayer({ source: vectorSource.value}));
props.map.addLayer(vectorLayer.value)
vectorLayer.value.setZIndex(999)
let dragPanInteraction = null;
const type = ref('')
// --- State mới ---
const saving_feature = ref(false); // 2. State cho việc lưu trữ
const showLayerPopup = ref(false);
const popupCoordinates = ref([0, 0]);
const popupOverlay = ref(null);
const popupElement = ref(null);
let currentFeature = null; // Lưu trữ feature đang vẽ
const showDeleteConfirm = ref(false); // State cho AlertDialog
const positionClass = computed(() => 'top-full mt-2')

const layoutClass = computed(() => 'flex flex-col items-center w-fit h-fit')

const animationClass = computed(() => 'slide-y')
const control_draw_layer_state = ref(false)
const selectedLayers = ref([])
// --- Watchers ---

watch(saving_feature, (newValue) => {
    if (newValue == true) {
        emit('update:savingFeature', true);
    }
});

// --- Hàm xử lý chính ---

const setMapDraggable = (enabled) => {
  if (dragPanInteraction) dragPanInteraction.setActive(enabled);
};

const toggle = () => {
  isOpen.value = !isOpen.value;
  if (!isOpen.value) cancelDrawing();
};

const removeDrawInteraction = () => {
  if (props.map && drawInteraction.value) {
    props.map.removeInteraction(drawInteraction.value);
    drawInteraction.value = null;
  }
};

// Bắt đầu quá trình vẽ
const startDraw = (typeDraw) => {
  cancelDrawing();
  emit('update:drawing', true);
  if(!control_draw_layer_state.value){
    props.map.on('click', handleClick)
  } else{
    cancelDrawing;
    props.map.un('click', handleClick)
    drawing.value = true; 
    setMapDraggable(false);
    drawInteraction.value = new Draw({
      source: vectorSource.value,
      type: typeDraw,
    });

    // Lắng nghe sự kiện bắt đầu vẽ
    drawInteraction.value.on('drawstart', (event) => {
      currentFeature = event.feature;
    });

    // Lắng nghe sự kiện kết thúc vẽ
    drawInteraction.value.on('drawend', (event) => {
      // Feature đã được gán trong 'drawstart'
      console.log("Draw ended, but waiting for layer selection to finalize.");
      selectedLayers.value.forEach(layerID => {
        selectLayerForDrawing(layerID)
      })
      control_draw_layer_state.value = true
      cancelDrawing()
  });

  props.map.addInteraction(drawInteraction.value);
    showLayerPopup.value = false;
  }
  type.value = typeDraw
};

// Được gọi khi người dùng chọn một layer từ popup
const selectLayerForDrawing = (layerId) => {
  console.log(currentFeature)
  if (!currentFeature) return;

  // Xử lý hình tròn đặc biệt
  const geometry = currentFeature.getGeometry();
  if (geometry.getType() == 'Circle') {
    // Chuyển Circle thành Polygon để lưu trữ GeoJSON hợp lệ
    const polygonGeom = fromCircle(geometry);
    currentFeature.setGeometry(polygonGeom);
  }
  
  const format = new GeoJSON();
  const featureGeoJSON = format.writeFeatureObject(currentFeature);

  // Lưu vào localStorage
  const drawings = JSON.parse(localStorage.getItem('drawings') || '[]');
  drawings.push({
    layer_id: layerId,
    feature: featureGeoJSON,
  });
  localStorage.setItem('drawings', JSON.stringify(drawings));

};

const cancelDrawing = () => {
  removeDrawInteraction();
  drawing.value = false;
  type.value = ''
  emit('update:drawing', false);
  setMapDraggable(true);
  showLayerPopup.value = false;
  if (popupOverlay.value) {
  popupOverlay.value.setPosition(undefined);
  }
  currentFeature = null;
};

// Lưu tất cả các hình đã vẽ lên server
const saveDraw = async () => {
  const drawingsToSave = JSON.parse(localStorage.getItem('drawings') || '[]');
  console.log(drawingsToSave)
  console.log(drawingsToSave.length)
  if (drawingsToSave.length == 0) {
      Swal.fire({
      icon: 'question',
      title: 'No Information',
      text: `There is no feature to save`,
    })
    return;
  }

  saving_feature.value = true;
  
  try {
    console.log("Calling API to save features:", drawingsToSave);
    // TODO: Gọi API của bạn ở đây
    const rawdrawings = JSON.parse(localStorage.getItem('drawings') || '[]');
    const drawings = rawdrawings.map(item => ({
      ...item,
      feature: {
        ...item.feature,
        geometry: transformGeometryTo4326(item.feature.geometry)
      }
    }));
    const insert_draw_features_response = await axios.post('http://localhost:8000/features/draw-features',
      drawings,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      }
    );
    vectorSource.value.clear();
    const drawingsByLayer = {};
    const featureIdMap = new Map(insert_draw_features_response.data.map(item => [item.layer_id, item.feature_id]));
    console.log(drawings)
    for (const [index, item] of drawings.entries()) {
      const lid = item.layer_id;
      if (!drawingsByLayer[lid]) drawingsByLayer[lid] = [];
      drawingsByLayer[lid].push({
        feature_id: featureIdMap.get(lid) || null, // Use feature_id from response
        layer_id: lid,
        name: item.feature?.properties?.name || 'Unnamed',
        properties: item.feature?.properties || {},
        geom: item.feature?.geometry
      });
    }
    console.log(drawingsByLayer)
    for (const [layer_id, featuresData] of Object.entries(drawingsByLayer)) {
      addFeaturetoUserLayer(props.map, layer_id, featuresData);
    }
    Swal.fire({
      icon: 'success',
      title: 'Success',
      text: `Features saved successfully!`,
    })
    localStorage.removeItem('drawings'); // Clear after successful save
    // Không cần xóa feature trên các layer đã vẽ
  } catch (error) {
    console.error("Failed to save features:", error);
    Swal.fire({
      icon: 'error',
      title: 'Erro',
      text: `Error in save features. Plese try again later!`,
    })
  } finally {
    saving_feature.value = false; // Reset trạng thái
    cancelDrawing();
    control_draw_layer_state.value = false
    localStorage.removeItem('drawings');
  }
};
const Always = () => {
  cancelDrawing;
  props.map.un('click',handleClick)
  drawing.value = true;
  emit('update:drawing', true); // Gửi tín hiệu đang vẽ
  setMapDraggable(false);
  drawInteraction.value = new Draw({
    source: vectorSource.value,
    type: type.value,
  });

  // Lắng nghe sự kiện bắt đầu vẽ
  drawInteraction.value.on('drawstart', (event) => {
    currentFeature = event.feature;
  });

  // Lắng nghe sự kiện kết thúc vẽ
  drawInteraction.value.on('drawend', (event) => {
    // Feature đã được gán trong 'drawstart'
    console.log("Draw ended, but waiting for layer selection to finalize.");
    selectedLayers.value.forEach(layerID => {
      selectLayerForDrawing(layerID)
    })
    control_draw_layer_state.value = true
    cancelDrawing()
  });

  props.map.addInteraction(drawInteraction.value);
  showLayerPopup.value = false;
  console.log('Always selected with:', selectedLayers.value)
}

const JustOnce = () => {
  cancelDrawing;
  
  props.map.un('click',handleClick)
  drawing.value = true;
  emit('update:drawing', true); // Gửi tín hiệu đang vẽ
  setMapDraggable(false);
  drawInteraction.value = new Draw({
    source: vectorSource.value,
    type: type.value,
  });

  // Lắng nghe sự kiện bắt đầu vẽ
  drawInteraction.value.on('drawstart', (event) => {
    currentFeature = event.feature;
  });
  // Lắng nghe sự kiện kết thúc vẽ
  drawInteraction.value.on('drawend', (event) => {
    control_draw_layer_state.value = false
    // Feature đã được gán trong 'drawstart'
    selectedLayers.value.forEach(layerID => {
      selectLayerForDrawing(layerID)
    })
    selectedLayers.value = []
    cancelDrawing()
  });

  props.map.addInteraction(drawInteraction.value);
  showLayerPopup.value = false;
  // Gọi xử lý khác tùy bạn
}
// Xóa các hình đã vẽ
const deleteDraw = () => {
  const drawings = JSON.parse(localStorage.getItem('drawings') || '[]');
  if (drawings.length == 0) {
      // Không có gì để xóa
      return;
  }
  showDeleteConfirm.value = true;
};

const confirmDelete = () => {
    const drawings = JSON.parse(localStorage.getItem('drawings') || '[]');
    console.log("Data to be deleted:", drawings); // Dữ liệu được lấy ra
    localStorage.removeItem('drawings'); // Xóa khỏi localStorage

    // TODO: Bạn cần có logic để xóa các feature đã được thêm vào các layer tương ứng trên bản đồ
    // Cách đơn giản là reload lại các layer từ đầu.
    vectorSource.value.clear();
    Swal.fire({
      icon: 'success',
      title: 'Success',
      text: `All features has been deleted`,
    })
    cancelDrawing();
    control_draw_layer_state.value = false
};
const closePopup = () =>{
  showLayerPopup.value = false
  drawing.value = false
  emit('update:drawing', false);
  control_draw_layer_state.value = false
  selectedLayers.value = []
  type.value = ''
  props.map.un('click', handleClick)
}
const handleClick = (evt) =>{
  const coordinate = evt.coordinate
  popupCoordinates.value = coordinate
  if (popupOverlay.value) {
    popupOverlay.value.setPosition(coordinate);
  }
  showLayerPopup.value = true;
}
function transformGeometryTo4326(geometry) {
  const type = geometry.type;

  if (type === 'Point') {
    return {
      type: 'Point',
      coordinates: transform(geometry.coordinates, 'EPSG:3857', 'EPSG:4326')
    };
  }

  if (type === 'LineString' || type === 'MultiPoint') {
    return {
      type,
      coordinates: geometry.coordinates.map(coord =>
        transform(coord, 'EPSG:3857', 'EPSG:4326')
      )
    };
  }

  if (type === 'Polygon' || type === 'MultiLineString') {
    return {
      type,
      coordinates: geometry.coordinates.map(ring =>
        ring.map(coord =>
          transform(coord, 'EPSG:3857', 'EPSG:4326')
        )
      )
    };
  }

  if (type === 'MultiPolygon') {
    return {
      type,
      coordinates: geometry.coordinates.map(polygon =>
        polygon.map(ring =>
          ring.map(coord =>
            transform(coord, 'EPSG:3857', 'EPSG:4326')
          )
        )
      )
    };
  }

  console.warn('Unsupported geometry type:', type);
  return geometry; // fallback nếu không xử lý được
}

onMounted(async () => {
  await nextTick(); // Đảm bảo DOM đã render
  console.log(props.userData)
  if (props.map && popupElement.value) {
    dragPanInteraction = props.map.getInteractions().getArray().find(
      (i) => i?.constructor?.name == 'DragPan'
    );

    popupOverlay.value = new Overlay({
      element: popupElement.value, // <-- Dùng element từ Vue
      positioning: 'bottom-center',
      stopEvent: true,
      offset: [0, -15],
    });

    props.map.addOverlay(popupOverlay.value);
  }
});
</script>

<template>
  <div class="relative inline-flex items-center justify-center">
    <div class="relative inline-flex flex-col items-center justify-center">
      <!-- Main Button -->
      <button v-tooltip.right="'Draw tool'" @click="toggle"
        class="w-10 h-10 rounded-md bg-gray-400 hover:bg-gray-500 hover:cursor-pointer text-white flex items-center justify-center transition-transform duration-400 hover:cursor-pointer">
        <component :is="isOpen ? X : Pencil" class="w-6 h-6" />
      </button>

      <!-- Action Buttons -->
      <transition-group tag="div" :name="animationClass" class="absolute z-10" :class="[positionClass, layoutClass]">
        <button v-tooltip.right="'Point'" v-if="isOpen" key="draw-point" @click="startDraw('Point')"
          class="w-10 h-10 m-1 rounded-md bg-neutral-400 hover:bg-neutral-500 hover:cursor-pointer text-white flex items-center justify-center shadow">
          <Dot class="w-6 h-6" />
        </button>

        <button v-tooltip.right="'Line'" v-if="isOpen" key="draw-line" @click="startDraw('LineString')"
          class="w-10 h-10 m-1 rounded-md bg-neutral-400 hover:bg-neutral-500 hover:cursor-pointer text-white flex items-center justify-center shadow">
          <Spline class="w-6 h-6" />
        </button>

        <button v-tooltip.right="'Polygon'" v-if="isOpen" key="draw-polygon" @click="startDraw('Polygon')"
          class="w-10 h-10 m-1 rounded-md bg-neutral-400 hover:bg-neutral-500 hover:cursor-pointer text-white flex items-center justify-center shadow">
          <Hexagon class="w-6 h-6" />
        </button>

        <button v-tooltip.right="'Circle'" v-if="isOpen" key="draw-circle" @click="startDraw('Circle')"
          class="w-10 h-10 m-1 rounded-md bg-neutral-400 hover:bg-neutral-500 hover:cursor-pointer text-white flex items-center justify-center shadow">
          <Circle class="w-6 h-6" />
        </button>

        <button v-tooltip.right="'Save'" v-if="isOpen" key="save" @click="saveDraw"
          class="w-10 h-10 m-1 rounded-md bg-neutral-400 hover:bg-neutral-500 hover:cursor-pointer text-white flex items-center justify-center shadow">
          <Save class="w-6 h-6" />
        </button>

        <button v-tooltip.right="'Delete'" v-if="isOpen" key="delete" @click="deleteDraw"
          class="w-10 h-10 m-1 rounded-md bg-neutral-400 hover:bg-neutral-500 hover:cursor-pointer text-white flex items-center justify-center shadow">
          <Trash2 class="w-6 h-6" />
        </button>
      </transition-group>
    </div>
    <!-- Popup container -->
    <div v-show="showLayerPopup" ref="popupElement"
      class="absolute mt-3 z-20 bg-white rounded-xl shadow-xl p-4 border min-w-[300px] space-y-4">

      <!-- Close button -->
      <span @click="closePopup"
        class="absolute top-2 right-2 text-gray-500 hover:text-gray-800 cursor-pointer text-xl font-bold">
        &times;
      </span>

      <h4 class="text-sm font-semibold mb-2">Please select these layers to draw on:</h4>

      <!-- Table -->
      <div class="max-h-40 overflow-y-auto">
        <table class="w-full text-sm text-center">
          <thead>
            <tr>
              <th class="font-semibold text-gray-600 pb-1">Select</th>
              <th class="font-semibold text-gray-600 pb-1 text-left">Layer Name</th>
              <th class="font-semibold text-gray-600 pb-1">Fill</th>
              <th class="font-semibold text-gray-600 pb-1">Stroke</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="layer in props.userData" :key="layer.layer_id" class="hover:bg-gray-50 transition">
              <td class="py-1">
                <input type="checkbox" :id="`layer-${layer.layer_id}`" :value="layer.layer_id" v-model="selectedLayers"
                  class="shadcn-checkbox" />
              </td>
              <td class="py-1 text-gray-700 text-left">
                <label :for="`layer-${layer.layer_id}`" class="cursor-pointer">
                  {{ layer.layer_name }}
                </label>
              </td>
              <td class="py-1">
                <div class="w-4 h-4 rounded-full border border-gray-300" :style="{ backgroundColor: layer.fill }"></div>
              </td>
              <td class="py-1">
                <div class="w-4 h-4 rounded-full border border-gray-300" :style="{ backgroundColor: layer.stroke }">
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Action Buttons -->
      <div v-if="selectedLayers.length > 0" class="flex justify-center gap-4 pt-4 border-t pt-4">
        <Button variant="outline" @click="JustOnce"
          class="px-4 py-2 text-sm text-blue-600 border-blue-600 hover:bg-blue-100 transition">
          Just once
        </Button>
        <Button @click="Always" class="px-4 py-2 text-sm text-white bg-green-600 hover:bg-green-700 transition">
          Always
        </Button>
      </div>
    </div>

    <AlertDialog :open="showDeleteConfirm" @update:open="showDeleteConfirm = $event">
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
          <AlertDialogDescription>
            This action will permanently delete all unsaved drawings. This data cannot be recovered.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel @click="showDeleteConfirm = false">Cancel</AlertDialogCancel>
          <AlertDialogAction @click="confirmDelete">Continue</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  </div>
</template>

<style scoped>
.slide-y-enter-active,
.slide-y-leave-active {
  transition: all 0.4s ease;
}
.slide-y-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.slide-y-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
