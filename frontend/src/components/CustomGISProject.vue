<template>
  <div v-if="!isLoading" class="w-full h-full p-4">
    <h3 class="italic opacity-75 flex items-center gap-2 mb-4 text-2xl font-bold mt-6 border-b border-gray-300">
      <img src="@/assets/work.gif" alt="News GIF" class="h-6 w-6 animate-pulse">
      YOUR CUSTOMS GIS STORAGE
    </h3>
    <div v-if="projects.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 p-10">
      <Dialog>
        <DialogTrigger as-child>
          <Button v-tooltip="'Create New Project'"
            class="text-9xl text-center text-neutral-400 bg-zinc-100 hover:cursor-pointer hover:bg-zinc-200 border-2 border-stone-300 border-dashed h-80 w-80 pb-9">
            +
          </Button>
        </DialogTrigger>
        <DialogContent class="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Create new Vector Project</DialogTitle>
            <DialogDescription>
              Make new to your project here. Click save when you're done.
            </DialogDescription>
          </DialogHeader>
          <form @submit.prevent="submitForm">
            <div class="grid gap-4 py-4">
              <!-- Name Field -->
              <div class="grid grid-cols-4 items-center gap-4">
                <Label for="name" class="text-right">Name</Label>
                <Input id="name" placeholder="Example: GeoJSON Map,..." class="col-span-3" v-model="form.project_name"
                  :class="{ 'border-red-500': formErrors.project_name }" required />
                <span v-if="formErrors.project_name" class="text-red-500 text-xs col-span-4">{{ formErrors.project_name
                  }}</span>
              </div>

              <!-- Picture Field -->
              <div class="grid grid-cols-4 items-center gap-4">
                <Label for="picture" class="text-right">Picture</Label>
                <Input id="picture" type="file" class="col-span-3 w-full" ref="project_img"
                  @change="handleImageUpload" />
              </div>

              <!-- Tabs -->
              <Tabs default-value="Vector" class="w-[450px]">
                <TabsList class="w-full">
                  <TabsTrigger value="Vector">
                    Default Vetor Layer
                  </TabsTrigger>
                  <TabsTrigger value="Base">
                    Default Base Layer
                  </TabsTrigger>
                </TabsList>
                <TabsContent value="Vector">
                  <span class="text-sm text-gray-500 italic">Choose default VectorLayer for your project
                    (Optional)</span>
                  <div class="max-h-48 overflow-y-auto border border-gray-200 rounded-md mt-2 p-4">
                    <!-- Checkbox List -->
                    <div v-for="layer in vector_layer" :key="layer.default_layer_id"
                      class="flex items-center space-x-2 mb-2">
                      <Checkbox :id="layer.default_layer_id.toString()"
                        :model-value="Vtags.includes(layer.default_layer_id)"
                        @update:model-value="(checked) => handleVectorLayerChange(checked, layer.default_layer_id)"
                        class="data-[state=checked]:bg-blue-500 data-[state=checked]:border-blue-600 data-[state=checked]:text-white data-[state=checked]:font-bold" />
                      <label :for="layer.default_layer_id.toString()"
                        class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                        {{ layer.default_layer_name }}
                      </label>
                    </div>
                  </div>
                </TabsContent>
                <TabsContent value="Base">
                  <span class="text-sm text-gray-500 italic">Choose default BaseLayer for your project</span>
                  <div class="max-h-48 overflow-y-auto border border-gray-200 rounded-md mt-2 p-4">
                    <!-- Checkbox List -->
                    <div v-for="layer in base_layer" :key="layer.default_base_layer_id"
                      class="flex items-center space-x-2 mb-2">
                      <Checkbox :id="layer.default_base_layer_id.toString()"
                        :model-value="Btags.includes(layer.default_base_layer_id)"
                        @update:model-value="(checked) => handleBaseLayerChange(checked, layer.default_base_layer_id)"
                        class="data-[state=checked]:bg-blue-500 data-[state=checked]:border-blue-600 data-[state=checked]:text-white data-[state=checked]:font-bold" />
                      <label :for="layer.default_base_layer_id.toString()"
                        class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                        {{ layer.default_base_layer_name }}
                      </label>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
            <DialogFooter>
              <Button type="submit" class="bg-blue-500 hover:bg-blue-600 text-white"
                :disabled="isSubmitting">Save</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
      <Card v-for="project in projects" :key="project.project_id"
        class="p-4 w-80 h-80 flex flex-col gap-2 rounded-xl transition duration-200 ease-in-out transform hover:scale-105 hover:shadow-lg relative">
        <div class="h-40 w-full mb-2">
          <img v-if="project.project_img" :src="'data:image/jpeg;base64,' + project.project_img" alt="Project Image"
            class="mt-2 w-full h-full rounded-md" />
        </div>
        <CardTitle>{{ project.project_name }}</CardTitle>
        <div class="text-sm text-gray-600">
          <p>Created Date: {{ formatDate(project.created_at) }}</p>
          <p>Last Update: {{ formatRelativeTime(project.updated_at) }}</p>
        </div>
        <Button class="bg-cyan-500 hover:bg-cyan-600 flex items-center hover:cursor-pointer" @click="navigateToProject(project.project_id)">
          <MapPinned class="w-5 h-5 mr-2" /> View
        </Button>
        <DropdownMenu>
          <DropdownMenuTrigger as-child>
            <Button
              class="absolute top-2 right-2 w-8 h-8 bg-gray-200 hover:bg-gray-300 rounded-full p-1 hover:cursor-pointer">
              <MoreVertical class="w-4 h-4" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent class="w-40 z-[1001]">
            <DropdownMenuItem @click="openEditDialog(project)">
              <EditIcon class="w-4 h-4 mr-2" />
              <span>Edit project</span>
            </DropdownMenuItem>
            <DropdownMenuItem @click="openDeleteDialog(project.project_id)">
              <TrashIcon class="w-4 h-4 mr-2" />
              <span>Delete project</span>
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </Card>
      <!-- Edit Project Dialog -->
      <Dialog v-model:open="editDialogOpen">
        <DialogContent class="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Edit Project</DialogTitle>
            <DialogDescription>
              Update your project details here. Click save when you're done.
            </DialogDescription>
          </DialogHeader>
          <form @submit.prevent="updateProject">
            <div class="grid gap-4 py-4">
              <div class="grid grid-cols-4 items-center gap-4">
                <Label for="edit-name" class="text-right">Name</Label>
                <Input id="edit-name" class="col-span-3" v-model="editForm.project_name"
                  :class="{ 'border-red-500': editFormErrors.project_name }" required />
                <span v-if="editFormErrors.project_name" class="text-red-500 text-xs col-span-4">{{
                  editFormErrors.project_name }}</span>
              </div>
              <div class="grid grid-cols-4 items-center gap-4">
                <Label for="edit-picture" class="text-right">Picture</Label>
                <Input id="edit-picture" type="file" class="col-span-3 w-full" ref="edit_project_img"
                  @change="handleEditImageUpload" accept="image/*" />
              </div>
              <Tabs default-value="Vector" class="w-[450px]">
                <TabsList class="w-full">
                  <TabsTrigger value="Vector">Default Vector Layer</TabsTrigger>
                  <TabsTrigger value="Base">Default Base Layer</TabsTrigger>
                </TabsList>
                <TabsContent value="Vector">
                  <span class="text-sm text-gray-500 italic">Add more default VectorLayer for your project
                    (Optional)</span>
                  <div class="max-h-48 overflow-y-auto border border-gray-200 rounded-md mt-2 p-4">
                    <div v-for="layer in more_vector_layer" :key="layer.default_layer_id"
                      class="flex items-center space-x-2 mb-2">
                      <Checkbox :id="layer.default_layer_id.toString()"
                        :model-value="editVtags.includes(layer.default_layer_id)"
                        @update:model-value="handleEditVectorLayerChange($event, layer.default_layer_id)"
                        class="data-[state=checked]:bg-blue-500 data-[state=checked]:border-blue-600 data-[state=checked]:text-white data-[state=checked]:font-bold" />
                      <label :for="layer.default_layer_id.toString()" class="text-sm font-medium leading-none">
                        {{ layer.default_layer_name }}
                      </label>
                    </div>
                  </div>
                </TabsContent>
                <TabsContent value="Base">
                  <span class="text-sm text-gray-500 italic">Add more default BaseLayer for your project
                    (Optional)</span>
                  <div class="max-h-48 overflow-y-auto border border-gray-200 rounded-md mt-2 p-4">
                    <div v-for="layer in more_base_layer" :key="layer.default_base_layer_id"
                      class="flex items-center space-x-2 mb-2">
                      <Checkbox :id="layer.default_base_layer_id.toString()"
                        :model-value="editBtags.includes(layer.default_base_layer_id)"
                        @update:model-value="handleEditBaseLayerChange($event, layer.default_base_layer_id)"
                        class="data-[state=checked]:bg-blue-500 data-[state=checked]:border-blue-600 data-[state=checked]:text-white data-[state=checked]:font-bold" />
                      <label :for="layer.default_base_layer_id.toString()" class="text-sm font-medium leading-none">
                        {{ layer.default_base_layer_name }}
                      </label>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
            <DialogFooter>
              <Button type="submit" class="bg-blue-500 hover:bg-blue-600 text-white" :disabled="isSubmitting">
                Save
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
      <!-- Delete Confirmation Dialog -->
      <AlertDialog v-model:open="deleteDialogOpen">
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirm Deletion</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this project?Your project will be moved to the Recycle Bin.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <Button class="bg-red-500 hover:bg-red-600 text-white" @click="deleteProject">
              Delete
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
    <div v-else class="h-full w-full">
      <Dialog>
        <DialogTrigger as-child>
          <Button
            class="text-9xl text-center text-neutral-400 bg-zinc-100 hover:cursor-pointer hover:bg-zinc-200 border-2 border-stone-300 border-dashed h-80 w-80 pb-9">
            +
          </Button>
        </DialogTrigger>
        <DialogContent class="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Create new Vector Project</DialogTitle>
            <DialogDescription>
              Make new to your project here. Click save when you're done.
            </DialogDescription>
          </DialogHeader>
          <form @submit.prevent="submitForm">
            <div class="grid gap-4 py-4">
              <!-- Name Field -->
              <div class="grid grid-cols-4 items-center gap-4">
                <Label for="name" class="text-right">Name</Label>
                <Input id="name" placeholder="Example: GeoJSON Map,..." class="col-span-3" v-model="form.project_name"
                  :class="{ 'border-red-500': formErrors.project_name }" required />
                <span v-if="formErrors.project_name" class="text-red-500 text-xs col-span-4">{{ formErrors.project_name
                  }}</span>
              </div>

              <!-- Picture Field -->
              <div class="grid grid-cols-4 items-center gap-4">
                <Label for="picture" class="text-right">Picture</Label>
                <Input id="picture" type="file" class="col-span-3 w-full" ref="project_img"
                  @change="handleImageUpload" />
              </div>

              <!-- Tabs -->
              <Tabs default-value="Vector" class="w-[450px]">
                <TabsList class="w-full">
                  <TabsTrigger value="Vector">
                    Default Vetor Layer
                  </TabsTrigger>
                  <TabsTrigger value="Base">
                    Default Base Layer
                  </TabsTrigger>
                </TabsList>
                <TabsContent value="Vector">
                  <span class="text-sm text-gray-500 italic">Choose default VectorLayer for your project
                    (Optional)</span>
                  <div class="max-h-48 overflow-y-auto border border-gray-200 rounded-md mt-2 p-4">
                    <!-- Checkbox List -->
                    <div v-for="layer in vector_layer" :key="layer.default_layer_id"
                      class="flex items-center space-x-2 mb-2">
                      <Checkbox :id="layer.default_layer_id.toString()"
                        :model-value="Vtags.includes(layer.default_layer_id)"
                        @update:model-value="(checked) => handleVectorLayerChange(checked, layer.default_layer_id)"
                        class="data-[state=checked]:bg-blue-500 data-[state=checked]:border-blue-600 data-[state=checked]:text-white data-[state=checked]:font-bold" />
                      <label :for="layer.default_layer_id.toString()"
                        class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                        {{ layer.default_layer_name }}
                      </label>
                    </div>
                  </div>
                </TabsContent>
                <TabsContent value="Base">
                  <span class="text-sm text-gray-500 italic">Choose default BaseLayer for your project (Optional)</span>
                  <div class="max-h-48 overflow-y-auto border border-gray-200 rounded-md mt-2 p-4">
                    <!-- Checkbox List -->
                    <div v-for="layer in base_layer" :key="layer.default_base_layer_id"
                      class="flex items-center space-x-2 mb-2">
                      <Checkbox :id="layer.default_base_layer_id.toString()"
                        :model-value="Btags.includes(layer.default_base_layer_id)"
                        @update:model-value="(checked) => handleBaseLayerChange(checked, layer.default_base_layer_id)"
                        class="data-[state=checked]:bg-blue-500 data-[state=checked]:border-blue-600 data-[state=checked]:text-white data-[state=checked]:font-bold" />
                      <label :for="layer.default_base_layer_id.toString()"
                        class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                        {{ layer.default_base_layer_name }}
                      </label>
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
            <DialogFooter>
              <Button type="submit" class="bg-blue-500 hover:bg-blue-600 text-white"
                :disabled="isSubmitting">Save</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  </div>
  <div v-else
    class="flex flex-col justify-center items-center space-y-3 absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
    <Skeleton class="h-[175px] w-[375px] rounded-xl" />
    <div class="space-y-2">
      <Skeleton class="h-5 w-[375px]" />
      <Skeleton class="h-5 w-[325px]" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'
import { Card, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Checkbox } from '@/components/ui/checkbox'
import { Form, FormField, FormItem, FormLabel, FormControl } from '@/components/ui/form'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { MapPinned, MoreVertical, EditIcon, TrashIcon } from 'lucide-vue-next'
import { useRouter } from 'vue-router';
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from '@/components/ui/dropdown-menu'
import { AlertDialog, AlertDialogContent, AlertDialogHeader, AlertDialogFooter, AlertDialogTitle, AlertDialogDescription, AlertDialogCancel } from '@/components/ui/alert-dialog'
import { format, formatDistanceToNow } from 'date-fns'; // Nhập date-fns
// State
const form = ref({
  project_name: '',
  project_type: 'P001', // Giá trị mặc định từ fetchProjectsByType
  project_img: null,
})
const router = useRouter();
const projects = ref([])
const isSubmitting = ref(false)
const isLoading = ref(false)
const error = ref('')
const success = ref('')
const vector_layer = ref([])
const more_vector_layer = ref([])
const more_base_layer = ref([])
const base_layer = ref([
  {
    "default_base_layer_id": 1, "default_base_layer_name": "Google Maps", "avatar": "/src/assets/map_logo/googlemaps.png"
  },
  {
    "default_base_layer_id": 2, "default_base_layer_name": "Mapbox", "avatar": "/src/assets/map_logo/mapbox.png"
  },
  {
    "default_base_layer_id": 3, "default_base_layer_name": "CartoDB", "avatar": "/src/assets/map_logo/cartoDB.png"
  },
  {
    "default_base_layer_id": 4, "default_base_layer_name": "ESRI ArcGIS Online", "avatar": "/src/assets/map_logo/esri.png"
  },
])
const Vtags = ref([])
const Btags = ref([])
const editVtags = ref([])
const editBtags = ref([])
const project_img = ref(null) // Ref cho input file
const edit_project_img = ref(null)
const editDialogOpen = ref(false)
const deleteDialogOpen = ref(false)
const selectedProjectId = ref(null)
const imagePreview = ref(null)
const formErrors = ref({ project_name: '' })
const editFormErrors = ref({ project_name: '' })
const editForm = ref({
  project_id: null,
  project_name: '',
  project_type: 'P001', // Giá trị mặc định từ fetchProjectsByType
  project_img: null,
})
const default_layers = ref([])
// Xử lý upload ảnh
const handleImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    if (file.size > 5 * 1024 * 1024) {
      Swal.fire('Have an error!', 'Image size must be less than 5MB', 'error')
      project_img.value.value = null
      return
    }
    const reader = new FileReader()
    reader.onload = (e) => {
      form.value.project_img = e.target.result.split(',')[1]
      imagePreview.value = e.target.result
    }
    reader.readAsDataURL(file)
  } else {
    form.value.project_img = null
    imagePreview.value = null
  }
}

const handleEditImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    if (file.size > 5 * 1024 * 1024) {
      Swal.fire('Have an error!', 'Image size must be less than 5MB', 'error')
      edit_project_img.value.value = null
      return
    }
    const reader = new FileReader()
    reader.onload = (e) => {
      editForm.value.project_img = e.target.result.split(',')[1]
    }
    reader.readAsDataURL(file)
  }
}

// Hàm xử lý cho Vector Layer
const handleVectorLayerChange = (checked, layerId) => {
  if (checked) {
    // Nếu trạng thái mới là "đã chọn" (true), thêm ID vào mảng
    Vtags.value.push(layerId);
  } else {
    // Nếu trạng thái mới là "bỏ chọn" (false), tìm và xóa ID khỏi mảng
    const index = Vtags.value.indexOf(layerId);
    if (index > -1) {
      Vtags.value.splice(index, 1);
    }
  }
};

// Hàm xử lý cho Base Layer
const handleBaseLayerChange = (checked, layerId) => {
  if (checked) {
    Btags.value.push(layerId);
  } else {
    const index = Btags.value.indexOf(layerId);
    if (index > -1) {
      Btags.value.splice(index, 1);
    }
  }
};

const handleEditVectorLayerChange = (checked, layerId) => {
  if (checked) {
    // Nếu trạng thái mới là "đã chọn" (true), thêm ID vào mảng
    editVtags.value.push(layerId);
  } else {
    // Nếu trạng thái mới là "bỏ chọn" (false), tìm và xóa ID khỏi mảng
    const index = editVtags.value.indexOf(layerId);
    if (index > -1) {
      editVtags.value.splice(index, 1);
    }
  }
}

const handleEditBaseLayerChange = (checked, layerId) => {
  if (checked) {
    editBtags.value.push(layerId);
  } else {
    const index = editBtags.value.indexOf(layerId);
    if (index > -1) {
      editBtags.value.splice(index, 1);
    }
  }
}

const validateForm = () => {
  formErrors.value.project_name = form.value.project_name ? '' : 'Name is required'
  return !formErrors.value.project_name
}

const validateEditForm = () => {
  editFormErrors.value.project_name = editForm.value.project_name ? '' : 'Name is required'
  return !editFormErrors.value.project_name
}

// Submit form
const submitForm = async () => {
  if(!form.value.project_img){
    Swal.fire('Have an error!', `Project's image is required!!!`, 'error')
    return;
  }
  isSubmitting.value = true
  error.value = ''
  success.value = ''
  try {
    const create_project_response = await axios.post(
      'http://localhost:8000/projects',
      {
        ...form.value,
      },
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      }
    )
    const project_id = create_project_response.data.project_id
    const base_result = Btags.value.join('-')
    const informs = vector_layer.value
      .filter((layer) => Vtags.value.includes(layer.default_layer_id))
      .map((layer) => ({
        project_id: project_id,
        default_layer_id: layer.default_layer_id,
        layer_name: layer.default_layer_name,
        base: base_result, // Có thể thay đổi giá trị base nếu cần
      }))
    console.log("informs: ", informs)
    if (informs.length > 0) {
      await axios.post(
        'http://localhost:8000/default-vector-layer-informs/',
        { informs },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json',
          },
        }
      )
    }
    const list_default_layer_id = informs.map(item => item.default_layer_id)
    try {
      const get_default_feature_id_response = await axios.post(
        'http://localhost:8000/default-features/feature_ids-by-layer-ids',
        list_default_layer_id,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json',
          },
        }
      );
      const list_feature_id = get_default_feature_id_response.data
      const data = {
        project_id: project_id,
        layers: list_feature_id
      }
      const insert_setting_default_feature_response = await axios.post('http://localhost:8000/default-feature-settings',data,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json',
          },
        }
      );
    } catch(error){
      console.error(error)
    }

    success.value = 'Project created successfully!'
    form.value = { project_name: '', project_type: 'P001', project_img: null }
    imagePreview.value = null
    project_img.value.value = null
    Vtags.value = []
    Btags.value = []
    await fetchProjectsByType()
    Swal.fire(`${success.value}`, 'Your project is now ready!', 'success')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to create project'
    Swal.fire('Have an error!', `${error.value}`, 'error')

  } finally {
    isSubmitting.value = false
  }
};
// Lấy danh sách project theo loại
const fetchProjectsByType = async () => {
  isLoading.value = true
  try {
    const response = await axios.get(`http://localhost:8000/projects/by-type/P001`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
    })
    projects.value = response.data
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load projects'
    projects.value = []
  } finally {
    isLoading.value = false
  }
}

// Lấy danh sách vector layer mặc định
const fetchDefaultVectorLayer = async () => {
  try {
    const response = await axios.get('http://localhost:8000/default-vector-layers', {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
    })
    vector_layer.value = response.data
    console.log(vector_layer.value)
  } catch (err) {
    console.error('Failed to fetch vector layers:', err)
    vector_layer.value = []
  }
}

const openEditDialog = async (project) => {
  const default_vector_layer_response = await axios.get(`http://localhost:8000/default-vector-layer-informs/${project.project_id}`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json',
    },
  })
  default_layers.value = default_vector_layer_response.data
  more_vector_layer.value = vector_layer.value.filter(layerA => !default_layers.value.some(layerB => layerB.default_layer_id == layerA.default_layer_id))
  const layerIds = default_layers.value[0].base
    .split('-')
    .map(id => parseInt(id, 10))
    .filter(id => !isNaN(id));
  more_base_layer.value = base_layer.value.filter(base_layerA => !layerIds.some(base_layerB => base_layerB == base_layerA.default_base_layer_id))
  editForm.value.project_id = project.project_id
  editForm.value.project_name = project.project_name
  editVtags.value = []
  editBtags.value = []
  editDialogOpen.value = true
}

const updateProject = async () => {
  if (!validateEditForm()) return
  isSubmitting.value = true
  try {
    const payload = {
      project_name: editForm.value.project_name,
      project_type: editForm.value.project_type,
    }
    if (editForm.value.project_img && edit_project_img.value) {
      payload.project_img = editForm.value.project_img
    }
    const response = await axios.put(`http://localhost:8000/projects/${editForm.value.project_id}`, payload, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
    })
    if (editVtags.value.length != 0) {
      const informs = editVtags.value.map((layer) => ({
        project_id: editForm.value.project_id,
        default_layer_id: layer,
        layer_name: layer.default_layer_name,
        base: '', // Giá trị cố định
      }));
      await axios.post(
        'http://localhost:8000/default-vector-layer-informs/',
        { informs },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
            'Content-Type': 'application/json',
          },
        }
      )
      const list_default_layer_id = informs.map(item => item.default_layer_id)
      try {
        const get_default_feature_id_response = await axios.post(
          'http://localhost:8000/default-features/feature_ids-by-layer-ids',
          list_default_layer_id,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`,
              'Content-Type': 'application/json',
            },
          }
        );
        const list_feature_id = get_default_feature_id_response.data
        const data = {
          project_id: editForm.value.project_id,
          layers: list_feature_id
        }
        const insert_setting_default_feature_response = await axios.post('http://localhost:8000/default-feature-settings', data,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('access_token')}`,
              'Content-Type': 'application/json',
            },
          }
        );
      } catch (error) {
        console.error(error)
      }
    }
    const new_base = `${default_layers.value[0].base}-${editBtags.value.join('-')}`
    await axios.put('http://localhost:8000/default-vector-layer-informs/', {
      project_id: parseInt(editForm.value.project_id),
      base: new_base,
    }, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
    });
    await fetchProjectsByType()
    editDialogOpen.value = false
    editBtags.value = []
    editBtags.value = []
    editForm.value = { project_name: '', project_type: 'P001', project_img: null }
    Swal.fire('Your project has been updated successfully.', '', 'success')
  } catch (error) {
    Swal.fire('Have an error!', `${error}`, 'error')
  } finally {
    isSubmitting.value = false
  }
}

const openDeleteDialog = (projectId) => {
  selectedProjectId.value = projectId
  deleteDialogOpen.value = true
}

const deleteProject = async () => {
  isSubmitting.value = true
  console.log("Token: ",localStorage.getItem('access_token'))
  try {
    const response = await axios.patch(`http://localhost:8000/projects/${selectedProjectId.value}`,{}, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
    })
    if (response.status == 200) {
      projects.value = projects.value.filter(p => p.project_id !== selectedProjectId.value)
      Swal.fire('Project deleted successfully!!', '', 'success')
    }
    deleteDialogOpen.value = false
  } catch (error) {
    Swal.fire('Have an error!', `${error}`, 'error')
  } finally {
    isSubmitting.value = false
  }
}

// Định dạng ngày
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const formatRelativeTime = (date) => {
  if (!date) return 'N/A';
  try {
    return formatDistanceToNow(new Date(date), { addSuffix: true }); // e.g., "3 months ago"
  } catch (error) {
    console.error('Error formatting relative time:', error);
    return 'Invalid date';
  }
};

const navigateToProject = (project_id) => {
  const encodedId = btoa(project_id.toString());
  router.push({ name: 'UserVectorProject', params: { encodedId } });
}

// Gọi API khi component được mount
onMounted(async () => {
  await fetchProjectsByType()
  await fetchDefaultVectorLayer()
})
</script>