<template>
  <div v-show="showPopup" ref="popupElement"
    class="absolute z-20 bg-white rounded-xl shadow-xl p-4 border min-w-[300px] space-y-4">
    <!-- Close button -->
    <span @click="closePopup"
      class="absolute top-2 right-2 text-gray-500 hover:text-gray-800 cursor-pointer text-xl font-bold">
      ×
    </span>

    <!-- Default Information -->
    <div v-if="selectedFeature">
      <h4 class="text-sm font-semibold mb-2 text-gray-700">Default Information</h4>
      <div class="space-y-2 text-sm">
        <div>
          <strong class="text-gray-600">Feature Name:</strong> {{ selectedFeature.name || 'Unnamed Feature' }}
        </div>
        <div>
          <strong class="text-gray-600">Country:</strong> {{ selectedFeature.properties?.COUNTRY || selectedFeature.properties?.name || 'N/A' }}
        </div>
        <div>
          <strong class="text-gray-600">Layer ID:</strong> {{ selectedFeature.layer_id || 'N/A' }}
        </div>
      </div>
    </div>

    <!-- Additional Information -->
    <div>
      <h4 class="text-sm font-semibold mb-2 text-gray-700">Additional Information</h4>
      <div v-if="featureInforms.length" class="space-y-2 text-sm">
        <div v-for="inform in featureInforms" :key="inform.informs_id" class="flex items-center justify-between">
          <div v-if="editingInformId !== inform.informs_id" class="flex-1">
            <strong class="text-gray-600">{{ inform.title }}:</strong> {{ inform.content }}
          </div>
          <div v-else class="flex-1 space-y-2">
            <div>
              <div>
              <Label for="edit-title" class="text-sm font-medium text-gray-600">Title</Label>
              <Input id="edit-title" v-model="editForm.title" placeholder="Enter title" class="w-full" />
            </div>
            <div>
              <Label for="edit-content" class="text-sm font-medium text-gray-600">Content</Label>
              <Input id="edit-content" v-model="editForm.content" placeholder="Enter content" class="w-full" />
            </div>
          </div>
            </div>
          <div class="flex gap-2 ml-4">
            <Button
              :disabled="isEditing || editingInformId !== null"
              variant="ghost"
              class="cursor-pointer"
              size="sm"
              @click="startEditing(inform)"
              v-if="editingInformId !== inform.informs_id"
            >
              <Pencil class="w-4 h-4" />
            </Button>
            <Button
              :disabled="isEditing || editingInformId !== null"
              variant="ghost"
              class="cursor-pointer"
              size="sm"
              @click="deleteInform(inform.informs_id)"
              v-if="editingInformId !== inform.informs_id"
            >
              <Trash2 class="w-4 h-4 text-red-500" />
            </Button>
            <Button
              v-if="editingInformId == inform.informs_id"
              :disabled="!editForm.title || !editForm.content"
              class="cursor-pointer bg-sky-400 hover:bg-sky-500 text-white text-center"
              size="sm"
              @click="saveEditedInform(inform.informs_id)"
            >
              <Save class="w-4 h-4"/>
            </Button>
            <Button
              v-if="editingInformId == inform.informs_id"
              variant="ghost"
              class="cursor-pointer"
              size="sm"
              @click="resetEditing"
            >
              <RotateCcw class="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
      <div v-else class="text-sm text-gray-500">
        No information available.
      </div>
    </div>

    <!-- Add New Inform Section -->
    <div v-if="isAdding" class="space-y-2">
      <div>
        <Label for="add-title" class="text-sm font-medium text-gray-600">Title</Label>
        <Input id="add-title" v-model="addForm.title" placeholder="Enter title" class="w-full" />
      </div>
      <div>
        <Label for="add-content" class="text-sm font-medium text-gray-600">Content</Label>
        <Input id="add-content" v-model="addForm.content" placeholder="Enter content" class="w-full" />
      </div>
    </div>

    <!-- Add/Save Button -->
    <Button
      :disabled="isEditing || editingInformId !== null"
      class="cursor-pointer bg-sky-400 hover:bg-sky-500 text-white text-center w-full"
      :variant="isAdding ? 'default' : 'outline'"

      @click="isAdding ? saveNewInform() : isAdding = true"
    >
      {{ isAdding ? 'Save' : 'Add' }}
      <Plus v-if="!isAdding" class="w-4 h-4 ml-1" />
      <Save v-if="isAdding" class="w-4 h-4 ml-1" :disabled="!addForm.title || !addForm.content" />
    </Button>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { Overlay } from 'ol'
import axios from 'axios'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Pencil, Trash2, Save, Plus, RotateCcw } from 'lucide-vue-next'
import Swal from 'sweetalert2'

const props = defineProps({
  map: { type: Object, required: true },
  featureData: { type: Array, required: true },
  isDrawing: { type: Boolean, required: true }
})

const emit = defineEmits(['update:UpdateFeatureInforms'])
const popupElement = ref(null)
const popupOverlay = ref(null)
const showPopup = ref(false)
const selectedFeature = ref(null)
const featureInforms = ref([])
const currentCoordinate = ref(null)
const isAdding = ref(false)
const addForm = ref({ title: '', content: '' })
const editingInformId = ref(null)
const editForm = ref({ title: '', content: '' })
const isEditing = ref(false)

const closePopup = () => {
  showPopup.value = false
  selectedFeature.value = null
  featureInforms.value = []
  isAdding.value = false
  addForm.value = { title: '', content: '' }
  editingInformId.value = null
  editForm.value = { title: '', content: '' }
  isEditing.value = false
  if (popupOverlay.value) {
    popupOverlay.value.setPosition(undefined)
  }
}

const getFeatureAtPixel = (pixel) => {
  return props.map.forEachFeatureAtPixel(pixel, (feature) => feature)
}

const fetchFeatureInforms = async (featureId) => {
  try {
    const response = await axios.get(`http://localhost:8000/feature_informs/${featureId}`)
    console.log(response.data)
    return response.data
  } catch (error) {
    console.error('Error fetching feature informs:', error)
    return []
  }
}

const saveNewInform = async () => {
  if (!selectedFeature.value) return
  else if(!addForm.value.title || !addForm.value.content){
    Swal.fire({
      icon: 'warning',
      title: 'warning',
      text: 'Popup title and content must be not null!!!',
    })
    return
  }
  try {
    isEditing.value = true
    const response = await axios.post(`http://localhost:8000/feature_informs`, {
      feature_id: selectedFeature.value.feature_id,
      title: addForm.value.title,
      content: addForm.value.content
    })
    featureInforms.value.push(response.data)
    isAdding.value = false
    addForm.value = { title: '', content: '' }
    emit('update:UpdateFeatureInforms',true)
    Swal.fire({
      icon: 'success',
      title: 'Success',
      text: 'Feature inform added successfully!',
      timer: 1500,
      showConfirmButton: false
    })
  } catch (error) {
    console.error('Error adding feature inform:', error)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'Failed to add feature inform.',
    })
  } finally {
    isEditing.value = false
  }
}

const startEditing = (inform) => {
  editingInformId.value = inform.informs_id
  editForm.value = { title: inform.title, content: inform.content }
  isEditing.value = true
}

const saveEditedInform = async (informsId) => {
  if(!editForm.value.title || !editForm.value.content){
    Swal.fire({
      icon: 'warning',
      title: 'warning',
      text: 'Popup title and content must be not null!!!',
    })
    return
  }
  try {
    isEditing.value = true
    const response = await axios.put(`http://localhost:8000/feature_informs/${informsId}`, {
      title: editForm.value.title,
      content: editForm.value.content
    })
    const index = featureInforms.value.findIndex(inform => inform.informs_id == informsId)
    if (index !== -1) {
      featureInforms.value[index] = response.data
    }
    editingInformId.value = null
    editForm.value = { title: '', content: '' }
    emit('update:UpdateFeatureInforms',true)
    Swal.fire({
      icon: 'success',
      title: 'Success',
      text: 'Feature inform updated successfully!',
      timer: 1500,
      showConfirmButton: false
    })
  } catch (error) {
    console.error('Error updating feature inform:', error)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'Failed to update feature inform.',
    })
  } finally {
    isEditing.value = false
  }
}

const resetEditing = () => {
  const inform = featureInforms.value.find(inform => inform.informs_id == editingInformId.value)
  if (inform) {
    editForm.value = { title: inform.title, content: inform.content }
  }
  editingInformId.value = null
  isEditing.value = false
}

const deleteInform = async (informsId) => {
  try {
    isEditing.value = true
    await axios.delete(`http://localhost:8000/feature_informs/${informsId}`)
    featureInforms.value = featureInforms.value.filter(inform => inform.informs_id != informsId)
    emit('update:UpdateFeatureInforms',true)
    Swal.fire({
      icon: 'success',
      title: 'Success',
      text: 'Feature inform deleted successfully!',
      timer: 1500,
      showConfirmButton: false
    })
  } catch (error) {
    console.error('Error deleting feature inform:', error)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: 'Failed to delete feature inform.',
    })
  } finally {
    isEditing.value = false
  }
}

const handleMapClick = async (event) => {
  if (props.isDrawing) return

  const pixel = props.map.getEventPixel(event.originalEvent)
  const coordinate = event.coordinate
  const feature = getFeatureAtPixel(pixel)
  if (feature) {
    const featureId = feature.getProperties().id
    console.log(featureId)
    if (featureId) {
      selectedFeature.value = props.featureData.find(f => f.feature_id == featureId) || null
      featureInforms.value = await fetchFeatureInforms(featureId)
      showPopup.value = true
      currentCoordinate.value = coordinate
      console.log(selectedFeature.value)
      if(selectedFeature.value == null){
        popupOverlay.value.setPosition(undefined)
        return;
      } 
      console.log(selectedFeature.value)
      if (popupOverlay.value) {
        popupOverlay.value.setPosition(coordinate)
      }
    } else {
      closePopup()
    }
  } else {
    closePopup()
  }
}

onMounted(async () => {
  await nextTick()
  if (props.map && popupElement.value) {
    const canvas = props.map.getViewport().querySelector('canvas')
    if (canvas) {
      const context = canvas.getContext('2d', { willReadFrequently: true })
      props.map.set('context', context)
    }

    popupOverlay.value = new Overlay({
      element: popupElement.value,
      positioning: 'bottom-center',
      stopEvent: true,
      offset: [0, -15]
    })
    props.map.addOverlay(popupOverlay.value)
    if (!props.isDrawing) {
      props.map.on('click', handleMapClick)
    }
  }
})

onUnmounted(() => {
  if (props.map) {
    props.map.un('click', handleMapClick)
    if (popupOverlay.value) {
      props.map.removeOverlay(popupOverlay.value)
    }
  }
})

watch(() => props.isDrawing, (newVal) => {
  if (props.map) {
    if (!newVal) {
      props.map.on('click', handleMapClick)
    } else {
      props.map.un('click', handleMapClick)
      closePopup()
    }
  }
}, { immediate: true })
</script>