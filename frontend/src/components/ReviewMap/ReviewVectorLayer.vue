<script setup>
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger, DialogClose } from '@/components/ui/dialog'
import { createMap, createUserVectorLayer } from '@/modules/openlayer';
import TileLayer from "ol/layer/Tile";
import XYZ from "ol/source/XYZ";
import OSM from "ol/source/OSM";

import { ref, watch, onMounted } from 'vue';
import axios from 'axios';
const props = defineProps({
    layer_id: {
        type: Number,
    },
    openDialog: {
        type: Boolean,
    }
});
const map = ref(null)
const layerData = ref(null);
const features = ref([]);
const user_layer = ref({});
const list_user_layer_id = ref([]);
const user_layer_data = ref([]);
const isLoading = ref(true);
const fetchData = async () => {
    try {
        const response = await axios.get(`http://localhost:8000/layers/${props.layer_id}`, {
            headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` }
        });
        console.log(response.data)
        user_layer.value = response.data
        list_user_layer_id.value = [user_layer.value.layer_id]
        const feature_response = await axios.post(
            'http://localhost:8000/features/by-ids', list_user_layer_id.value,
            {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem('access_token')}`,
                },
            }
        );
        user_layer_data.value = feature_response.data
    } catch (error) {
        console.error('Error fetching layer data:', error);
    }
};

// Fetch features data
const initMap = async () => {
    map.value = createMap('map', {
        center: [105.5056, 17.2625],
        zoom: 5.5,
    });
        // thêm lớp OSM
    const osmLayer = new TileLayer({
        source: new OSM(),
    });
    map.value.addLayer(osmLayer)
    user_layer_data.value.forEach(layer => {
        const temp_vectorLayer = createUserVectorLayer(layer.layer, layer.features)
        temp_vectorLayer.setVisible(true)
        map.value.addLayer(temp_vectorLayer)
    })
    const array = map.value.getLayers().getArray()
    console.log(array)
    isLoading.value = false
}

// Watch for layer_id or openDialog changes
watch(() => [props.layer_id, props.openDialog], async () => {
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
                <DialogTitle class="text-center">LAYER REVIEW</DialogTitle>
                <DialogDescription class="flex gap-2 items-center px-2 justify-center">
                    <p v-if="user_layer" class="font-medium">Name: {{ user_layer.layer_name }}</p>
                    <div class="flex gap-1 items-center justify-center w-20">
                        <label class="text-sm text-muted-foreground">Fill: </label>
                        <div class="rounded border w-10 h-6" :style="{ backgroundColor: user_layer.fill }"></div>
                    </div>
                    <div class="flex gap-1 items-center justify-center w-20">
                        <label class="text-sm text-muted-foreground">Stroke: </label>
                        <div class="rounded border w-10 h-6" :style="{ backgroundColor: user_layer.stroke }"></div>
                    </div>
                </DialogDescription>
            </DialogHeader>
            <div id="map" ref="mapContainer" class="inset-0 z-10 h-130 w-full bg-white" />
            <DialogFooter class="h-12 w-full">
                <button @click="$emit('update:openDialog', false)"
                    class="bg-gray-500 text-white px-4 py-2 rounded cursor-pointer">Close</button>
            </DialogFooter>
        </DialogContent>
    </Dialog>

</template>