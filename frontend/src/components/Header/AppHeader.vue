<script setup lang="ts">
import { onMounted, ref } from 'vue';
import axios from 'axios';
import SidebarTrigger from '../ui/sidebar/SidebarTrigger.vue';
import { Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbSeparator } from '@/components/ui/breadcrumb'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { ChevronDownIcon, LogOut } from 'lucide-vue-next';
const emit = defineEmits(['update:sidebarOpen']);

const props = defineProps<{
  sidebarOpen: boolean
  breadcrumbData: { items: string[], parent: string | null, subItems: { label: string, name: string }[] | null }
}>()
const toggleSidebar = () => {
  emit('update:sidebarOpen',  !props.sidebarOpen);
};
const userImage = ref<string | null>(null);
const selectSubItem = (name: string) => {
  emit('update:activeComponentName', name) // Emit để cập nhật activeComponentName (cần xử lý ở Home.vue)
}
const fetchUserImage = async () => {
  try {
    const token = localStorage.getItem('access_token');
    const response = await axios.get('http://localhost:8000/user/image', {
      headers: { Authorization: `Bearer ${token}` },
    });
    console.log(response.data)
    if (response.data.user_image) {
      userImage.value = `data:image/jpeg;base64,${response.data.user_image}`;
    } else if (response.data.avatar) {
      userImage.value = response.data.avatar;
    }
  } catch (error) {
    console.error('Error fetching user image:', error);
  }
};
const logout = async () => {
  try {
    localStorage.removeItem('access_token');
    window.location.href = '/';
  } catch (error) {
    console.error('Logout failed:', error);
  }
};
onMounted( async() => {
  fetchUserImage()
})
</script>
<template>
  <header class="flex items-center justify-between px-6 py-2 bg-stone-50 border-b border-gray-200">
    <div class="flex gap-3 items-center">
      <SidebarTrigger class="h-12 w-12 text-gray-600 hover:bg-gray-100 rounded-md p-2" @click="toggleSidebar" />
      <Breadcrumb>
        <!-- Hiển thị các item trước parent (nếu có) -->
        <template v-for="(item, index) in props.breadcrumbData.items" :key="index">
          <!-- Nếu không có parent hoặc item chưa phải là parent -->
          <BreadcrumbItem v-if="!props.breadcrumbData.parent || index < props.breadcrumbData.items.length - 2">
            <BreadcrumbLink :href="`#`" class="text-gray-600 hover:text-gray-900" v-if="item != 'GIS Community'">
              {{ item }}
            </BreadcrumbLink>
            <BreadcrumbLink :href="`#`" class="text-gray-600 hover:text-gray-900" v-else>
              GIS Service
            </BreadcrumbLink>
            <BreadcrumbSeparator v-if="index < props.breadcrumbData.items.length - 1" />
          </BreadcrumbItem>
          <!-- Nếu có parent và đây là parent -->
          <BreadcrumbItem v-else-if="props.breadcrumbData.parent && item == props.breadcrumbData.parent">
            <DropdownMenu>
              <DropdownMenuTrigger as-child>
                <button
                  class="flex items-center space-x-1 text-gray-600 hover:text-gray-900 focus:outline-none hover:cursor-pointer">
                  <span>{{ item }}</span>
                  <ChevronDownIcon />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent side="bottom" align="start" class="w-48">
                <DropdownMenuItem v-for="subItem in props.breadcrumbData.subItems" :key="subItem.name"
                  @click="selectSubItem(subItem.name)">
                  <span>{{ subItem.label }}</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
            <BreadcrumbSeparator />
          </BreadcrumbItem>
          <!-- Hiển thị item cuối (menu con) -->
          <BreadcrumbItem v-else-if="index == props.breadcrumbData.items.length - 1">
            <BreadcrumbLink :href="`#`" class="text-gray-600 hover:text-gray-900 ml-1">
              {{ item }}
            </BreadcrumbLink>
          </BreadcrumbItem>
        </template>
      </Breadcrumb>
    </div>
    <div class="flex items-center space-x-2 gap-1">
      <button class="cursor-pointer hover:outline p-2 rounded-full" @click="logout" ><LogOut class="w-6 h-6 rotate-y-180 text-gray-400"></LogOut></button>
      <img v-if="userImage" :src="userImage" alt="User Image" class="h-12 w-12 rounded-full"/>
      <img src="/logo.png" alt="System Logo" class="h-12 w-12 rounded-full ml-10" />
      <div class="w-full flex flex-col">
        <span class="text-lg font-semibold h-5 flex items-center">FID</span>
        <span class="text-sm text-gray-600 h-5">Flexible Integrated for Development</span>
      </div>
    </div>
  </header>
</template>