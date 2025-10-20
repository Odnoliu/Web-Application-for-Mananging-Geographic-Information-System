<template>
  <div class="container mx-auto p-4">
    <h3 class="italic opacity-75 flex items-center gap-2 text-2xl font-bold mt-6 mb-4 border-b border-gray-300">
      <img src="@/assets/Recycle.gif" alt="Community GIF" class="h-6 w-6 animate-pulse">
      GIS COMMUNITY
    </h3>
    <Tabs default-value="project" class="w-full">
      <TabsList class="grid w-80 h-13 grid-cols-2 bg-gray-300">
        <TabsTrigger value="project">Project</TabsTrigger>
        <TabsTrigger value="user-layers">User Layers</TabsTrigger>
      </TabsList>

      <!-- TabsContent: Project -->
      <TabsContent value="project">
        <div class="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
          <div v-for="(item, index) in projectItems" :key="item.project_id" class="bg-white rounded-xl shadow hover:shadow-lg transition p-4 flex flex-col items-center text-center
             animate__animated animate__fadeInUp" :style="{ animationDelay: (index * 0.15) + 's' }">

            <!-- Hình ảnh -->
            <img :src="'data:image/jpeg;base64,' + item.project_img" alt="Project Image"
              class="w-full h-45 object-cover rounded-lg mb-3" />

            <!-- Tên dự án -->
            <h3 class="text-base font-semibold truncate w-full">{{ item.project_name }}</h3>

            <!-- Ngày xóa -->
            <p class="text-xs text-gray-500 mt-1">
              Deleted: {{ formatRelativeTime(item.updated_at) }}
            </p>

            <!-- Nút chức năng -->
            <div class="flex space-x-2 mt-3">
              <Button variant="outline" size="icon" class="rounded-full hover:bg-red-100 cursor-pointer"
                @click="deleteProject(item.project_id)">
                <Trash2 class="h-4 w-4 text-red-500" />
              </Button>
              <Button variant="outline" size="icon" class="rounded-full hover:bg-green-100 cursor-pointer"
                @click="restoreProject(item.project_id)">
                <ArchiveRestore class="h-4 w-4 text-green-500" />
              </Button>
            </div>
          </div>
        </div>
      </TabsContent>


      <!-- TabsContent: Layer -->
      <TabsContent value="user-layers">
        <div class="divide-y divide-gray-100">
          <div v-for="(layer, index) in userLayerItems" :key="layer.layer_id" class="flex items-center justify-between mb-2 py-3 px-4 bg-white rounded-md transition transform
             hover:shadow-md hover:scale-[1.02] animate__animated animate__fadeInUp"
            :style="{ animationDelay: (index * 0.1) + 's' }">

            <!-- Tên layer -->
            <div class="flex items-center space-x-3 w-48">
              <div class="w-5 h-5 rounded-sm border"
                :style="{ backgroundColor: layer.fill, borderColor: layer.stroke }"></div>
              <span class="text-sm font-semibold truncate">{{ layer.layer_name }}</span>
            </div>

            <!-- Project name -->
            <span class="text-xs text-gray-500 w-40 truncate">Project: {{ layer.project_name }}</span>

            <!-- Ngày xóa -->
            <span class="text-xs text-gray-400 w-28 truncate">{{ formatRelativeTime(layer.updated_at) }}</span>

            <!-- Action -->
            <div class="flex space-x-2">
              <Button variant="outline" size="icon" class="rounded-full hover:bg-red-100 cursor-pointer"
                @click="deleteUserLayer(layer.layer_id)">
                <Trash2 class="h-4 w-4 text-red-500" />
              </Button>
              <Button variant="outline" size="icon" class="rounded-full hover:bg-green-100 cursor-pointer"
                @click="restoreUserLayer(layer.layer_id)">
                <ArchiveRestore class="h-4 w-4 text-green-500" />
              </Button>
            </div>
          </div>
        </div>
      </TabsContent>

    </Tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { Trash2, ArchiveRestore } from 'lucide-vue-next'
import axios from 'axios'
import { format, formatDistanceToNow } from 'date-fns'; // Nhập date-fns
const projectItems = ref([])
const userLayerItems = ref([])
const formatRelativeTime = (date) => {
  if (!date) return 'N/A';
  try {
    return formatDistanceToNow(new Date(date), { addSuffix: true }); // e.g., "3 months ago"
  } catch (error) {
    console.error('Error formatting relative time:', error);
    return 'Invalid date';
  }
};
onMounted(async () => {
  const token = localStorage.getItem('access_token');
  try {
    const project_response = await axios.get('http://localhost:8000/projects/recycle/P001',{
      headers: { Authorization: `Bearer ${token}` },
    })
    projectItems.value = project_response.data
    console.log(projectItems.value)
    const user_layer_response = await axios.get('http://localhost:8000/layers/recycle',{
      headers: { Authorization: `Bearer ${token}` },
    })
    userLayerItems.value = user_layer_response.data
    console.log(userLayerItems.value)
  } catch (error) {
    console.error('Error fetching recycle bin data:', error)
  }
})

const deleteProject = async (id) => {
  const token = localStorage.getItem('access_token');
  try {
    projectItems.value = projectItems.value.filter(item => item.project_id != id)
    await axios.delete(`http://localhost:8000/projects/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
  } catch (error) {
    console.error(`Error deleting:`, error)
  }
}
const deleteUserLayer = async(id) =>{
  const token = localStorage.getItem('access_token');
  try{
    userLayerItems.value = userLayerItems.value.filter(item => item.layer_id != id)
    await axios.delete(`http://localhost:8000/layers/${id}`, {
      headers: { Authorization: `Bearer ${token}` },
    })
  } catch(error){
    console.error(`Error deleting layer:`, error)
  }

}

const restoreProject = async (id) => {
  try {
    await axios.patch(`http://localhost:8000/projects/recycle/${id}`,{}, {
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
    })
    // Update the corresponding array by removing the item
    projectItems.value = projectItems.value.filter(item => item.project_id != id)
  } catch (error) {
    console.error(`Error restoring project:`, error)
  }
}
const restoreUserLayer = async (id) => {
  try{
    await axios.patch(`http://localhost:8000/layers/recycle/${id}`,{},{
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
    })
    userLayerItems.value = userLayerItems.value.filter(item => item.layer_id !== id)
  }catch (error) {
    console.error(`Error restoring layer:`, error)
  }
}
</script>

<style scoped>
/* TailwindCSS is already included, so no additional styles needed */
</style>