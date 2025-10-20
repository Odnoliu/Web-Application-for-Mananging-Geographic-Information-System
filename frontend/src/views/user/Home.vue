<script setup lang="ts">
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import AppHeader from "@/components/Header/AppHeader.vue";
import AppSidebar from "@/components/SideBar/AppSideBar.vue";
import CustomGISProject from '@/components/CustomGISProject.vue';
import SatelliteWeather from '@/components/SatelliteWeather.vue';
import GISCommunity from '@/components/GISCommunity.vue';
import UserHome from '@/components/UserHome.vue';
import Tourism from "@/components/Tourism.vue";
import RecycleBin from "@/components/RecycleBin.vue";
import AppFooter from "@/components/Footer/AppFooter.vue";
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router';

// Sử dụng route để kiểm tra URL hiện tại
const route = useRoute();
const router = useRouter();

const componentsMap = {
  UserHome,
  CustomGISProject,
  SatelliteWeather,
  GISCommunity,
  Tourism,
  RecycleBin,
  AppFooter
};;
const activeComponentName = ref('UserHome');
const activeComponent = computed(() => componentsMap[activeComponentName.value]);
const isSidebarOpen = ref(false);

const closeSidebar = () => {
  isSidebarOpen.value = false;
};
const breadcrumbItems = computed(() => {
  const mapping = {
    UserHome: { items: ['Home'], parent: null, subItems: null },
    CustomGISProject: { 
      items: ['Project', 'Vector Layer Project'], 
      parent: 'Project', 
      subItems: [
        { label: 'Vector Layer Project', name: 'CustomGISProject' },
    ]
    },
    SatelliteWeather: { 
      items: ['Weather Services', 'Satellite Weather'], 
      parent: 'Weather Services', 
      subItems: [
        { label: 'Satellite Weather', name: 'SatelliteWeather' }
      ]
    },
    GISCommunity: { items: ['GIS Community'], parent: null, subItems: null },
    Tourism: { 
      items: ['Service Map', 'Tourism Destination'], 
      parent: 'Service Map', 
      subItems: [
        { label: 'Tourism Destination', name: 'Tourism' },
      ]
    },
    RecycleBin: { items: ['Recycle Bin'], parent: null, subItems: null },
  }
  return mapping[activeComponentName.value] || { items: ['Home'], parent: null, subItems: null }
})

const handleSubItemSelect = (name: string) => {
  activeComponentName.value = name
}
const token = ref(null)
onMounted(() => {
  const accessToken = route.query.access_token;
   const error = route.query.error
  if (accessToken) {
    localStorage.setItem('access_token', accessToken as string);
    // Xóa query parameter khỏi URL để tránh lặp lại
    router.replace({ path: '/home', query: {} });
  }
  token.value = localStorage.getItem('access_token')
});
</script>

<template>
  <SidebarProvider style="--sidebar-width: 20rem;" v-if="token">
    <div class="fixed inset-0 flex z-[1000] w-fit transform transition-transform duration-350 ease-in-out"
      :class="{ 'translate-x-0': isSidebarOpen, '-translate-x-full': !isSidebarOpen }">
      <AppSidebar v-model:active="activeComponentName"/>
    </div>
    <div class="fixed inset-0 flex z-[999] transform transition-transform duration-10 ease-in-out"
    :class="{ 'translate-y-0': isSidebarOpen, 'translate-y-full': !isSidebarOpen }">
      <div class="flex-1 bg-black background"  @click="closeSidebar"></div>
    </div>
    <main class="flex-1 flex flex-col min-h-screen">
      <div class="w-full sticky top-0 z-10">
        <AppHeader 
        :sidebar-open="isSidebarOpen"
        @update:sidebarOpen="isSidebarOpen = $event"
        @update:activeComponentName="handleSubItemSelect"
        :breadcrumb-data="breadcrumbItems"
        class="w-full shadow-md transition-shadow duration-300 bg-white"
        />
      </div>
      <div class="flex-1 bg-zinc-100">
        <component v-if="route.path == '/home'" :is="activeComponent" @update:active="activeComponentName = $event" />
        <router-view v-else />
      </div>
    </main>
  </SidebarProvider>
  <AppFooter/>
</template>

<style scoped>
.background{
  opacity: 0.3;
}
</style>