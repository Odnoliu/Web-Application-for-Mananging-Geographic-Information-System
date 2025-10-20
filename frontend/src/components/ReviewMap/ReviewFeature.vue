<script setup>
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger, DialogClose } from '@/components/ui/dialog'
import { createMap, addFeaturetoUserLayer, zoom_to_Feature } from '@/modules/openlayer';
import { ref, watch, onMounted } from 'vue';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import Feature from 'ol/Feature';
import { Style, Fill, Stroke } from 'ol/style';
import TileLayer from "ol/layer/Tile";
import XYZ from "ol/source/XYZ";
import OSM from "ol/source/OSM";
import axios from 'axios';
const props = defineProps({
    feature_id: {
        type: Number,
    },
    openDialog: {
        type: Boolean,
    }
});
const map = ref(null)
const user_feature = ref({});
const list_user_feature_id = ref([]);
const user_feature_data = ref({});
const isLoading = ref(true);
const fetchData = async () => {
    try {
        const feature_response = await axios.get(
            `http://localhost:8000/features/${props.feature_id}`,
            {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('access_token')}`,
                },
            }
        );
        user_feature_data.value = feature_response.data
    } catch (error) {
        console.error('Error fetching feature data:', error);
    }
};

// Fetch features data
const initMap = async () => {
    map.value = createMap('map', {
        zoom: 8,
    });
    const vectorSource = new VectorSource({
      features: [],
    });
    const layerStyle = new Style({
        fill: new Fill({
            color: '#8B4513',
        }),
        stroke: new Stroke({
            color: '#000000',
            width: 1,
        }),
    })
    const vectorLayer = new VectorLayer({
      source: vectorSource,
      style: layerStyle,
      visible: true,
      properties: {
        id: props.feature_id,
      },
    });
    vectorLayer.setZIndex(100)
    map.value.addLayer(vectorLayer)
    addFeaturetoUserLayer(map.value, props.feature_id, [user_feature_data.value])
    const layers = map.value.getLayers().getArray()
    layers.forEach(layer =>{
        const vectorSource = layer.getSource()
        const features = vectorSource.getFeatures()
        features.forEach(feat =>{
             zoom_to_Feature(map.value, feat)
        })
    })
    const osmLayer = new TileLayer({
        source: new OSM(),
    });
    map.value.addLayer(osmLayer)
    isLoading.value = false
}

// Watch for feature_id or openDialog changes
watch(() => [props.feature_id, props.openDialog], async () => {
    if (props.openDialog) {
        await fetchData();
    }
}, { immediate: true });

// onMounted hook
onMounted(async () => {
    await fetchData();
    await initMap();
});
</script>
<template>
    <Dialog v-model:open="props.openDialog" class="h-full w-500">
        <DialogContent class="!w-[1000px] !h-[700px] !max-w-none [&>button.absolute.top-4.right-4]:hidden">
            <DialogHeader class="h-13 w-full">
                <DialogTitle class="text-center">FEATURE REVIEW</DialogTitle>
                <DialogDescription class="flex gap-2 items-center px-2 justify-center">
                    <p v-if="user_feature_data" class="font-medium">Name: {{ user_feature_data.feature_name }}</p>
                </DialogDescription>
            </DialogHeader>
            <div id="map" ref="mapContainer" class="inset-0 z-10 h-130 w-full bg-white" />
            <DialogFooter class="h-12 w-full">
                <button @click="$emit('update:openFeatureDialog', false)"
                    class="bg-gray-500 text-white px-4 py-2 rounded cursor-pointer">Close</button>
            </DialogFooter>
        </DialogContent>
    </Dialog>

</template>