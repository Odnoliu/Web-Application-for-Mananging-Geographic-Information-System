<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { Home, Briefcase, Globe, Cloud, Users, StarIcon, UserIcon, CreditCardIcon, BellIcon, LogOutIcon, Recycle } from "lucide-vue-next";
import {
  SidebarFooter,
  SidebarHeader,
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubItem,
  SidebarMenuSubButton,
} from "@/components/ui/sidebar";
import {
  Collapsible,
  CollapsibleTrigger,
  CollapsibleContent
} from '@/components/ui/collapsible'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { ChevronUpIcon, ChevronDownIcon } from '@radix-icons/vue';
import axios from 'axios';

const props = defineProps<{
  active: string;
}>();

const emit = defineEmits(['update:active']);

// Menu items
const items = [
  {
    title: "Home",
    url: "#",
    icon: Home,
    iconColor: "text-blue-600 hover:text-blue-800",
    name: "UserHome",
  },
  {
    title: "Project",
    url: "#",
    icon: Briefcase,
    iconColor: "text-amber-600 hover:text-amber-700",
    subItems: [
      { title: "Vector Layer Project", url: "#", name: "CustomGISProject" },
    ],
  },
  {
    title: "Service Map",
    url: "#",
    icon: Globe,
    iconColor: "text-emerald-600 hover:text-emerald-700",
    subItems: [
      { title: "Tourism Destination", url: "#", name: "Tourism" },
    ],
  },
  {
    title: "Weather Services",
    url: "#",
    icon: Cloud,
    iconColor: "text-sky-500 hover:text-sky-700",
    subItems: [
      { title: "Satellite Weather", url: "#", name: "SatelliteWeather" },
    ],
  },
  {
    title: "GIS Service",
    url: "#",
    icon: Users,
    iconColor: "text-purple-600 hover:text-purple-800",
    name: "GISCommunity"
  },
  {
    title: "Recycle Bin",
    url: "#",
    icon: Recycle,
    iconColor: "text-green-600 hover:text-green-800",
    name: "RecycleBin"
  }
];

// State để lưu thông tin người dùng
const userInfo = ref({
  username: null,
  email: null,
  full_name: null,
});
const userImage = ref<string | null>(null);

// Hàm lấy thông tin người dùng
const fetchUserProfile = async () => {
  try {
    const token = localStorage.getItem('access_token');
    const response = await axios.get('http://localhost:8000/user/profile', {
      headers: { Authorization: `Bearer ${token}` },
    });
    userInfo.value = response.data;
  } catch (error) {
    console.error('Error fetching user profile:', error);
  }
};

// Hàm lấy ảnh người dùng
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

// Gọi API khi component được mount
onMounted(() => {
  fetchUserProfile();
  fetchUserImage();
});

// Hiển thị username hoặc email
const displayName = () => {
  return userInfo.value.username || userInfo.value.email || 'User';
};
const displayFullName = () => {
  return userInfo.value.full_name
}

const handleClick = (title: string) => {
  emit('update:active', title); // Gửi component, không gửi chuỗi
}
const logout = async () => {
  try {
    localStorage.removeItem('access_token');
    window.location.href = '/';
  } catch (error) {
    console.error('Logout failed:', error);
  }
};
</script>

<template>
  <Sidebar>
    <SidebarHeader>
      <SidebarMenu>
        <SidebarMenuItem>
          <SidebarMenuButton class="flex h-20 hover:bg-gray-200">
            <img src="/logo.png" alt="System Logo" class="h-12 w-12 rounded-full" />
            <div class="w-full flex flex-col">
              <span class="text-lg font-semibold h-5 flex items-center">FID</span>
              <span class="text-sm text-gray-600 h-5">Flexible Integrated for Development</span>
            </div>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarHeader>
    <SidebarContent>
      <SidebarGroup>
        <SidebarGroupLabel class="text-lg mb-2">Application</SidebarGroupLabel>
        <SidebarGroupContent>
          <SidebarMenu class="flex flex-col gap-2">
            <template v-for="item in items" :key="item.title">

              <!-- Không có subItems: render như bình thường -->
              <SidebarMenuItem v-if="!item.subItems">
                <SidebarMenuButton class="hover:cursor-pointer hover:bg-gray-200 text-base cursor-pointer"
                  :class="{ 'bg-gray-300': props.active == item.name }" @click="handleClick(item.name)">
                  <component :is="item.icon" :class="['transition duration-300', item.iconColor]"
                    style="height: 20px; width: 20px;" />
                  <span>{{ item.title }}</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <Collapsible v-else-if="item.title == 'Project'">
                <CollapsibleTrigger asChild>
                  <SidebarMenuButton class="hover:cursor-pointer hover:bg-gray-200 text-base">
                    <component :is="item.icon" :class="['transition duration-300', item.iconColor]"
                      style="height: 20px; width: 20px;" />
                    <span>{{ item.title }}</span>
                    <ChevronDownIcon class="ml-auto" />
                  </SidebarMenuButton>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <SidebarMenuSub>
                    <SidebarMenuSubItem v-for="subItem in item.subItems" :key="subItem.title">
                      <SidebarMenuSubButton asChild class="hover:cursor-pointer hover:bg-gray-200 text-base"
                        :class="{ 'bg-gray-200': props.active == subItem.name }" @click="handleClick(subItem.name)">
                        <span>{{ subItem.title }}</span>
                      </SidebarMenuSubButton>
                    </SidebarMenuSubItem>
                  </SidebarMenuSub>
                </CollapsibleContent>
              </Collapsible>
              <Collapsible v-else-if="item.title == 'Service Map'">
                <CollapsibleTrigger asChild>
                  <SidebarMenuButton class="hover:cursor-pointer hover:bg-gray-200 text-base">
                    <component :is="item.icon" :class="['transition duration-300', item.iconColor]"
                      style="height: 20px; width: 20px;" />
                    <span>{{ item.title }}</span>
                    <ChevronDownIcon class="ml-auto" />
                  </SidebarMenuButton>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <SidebarMenuSub>
                    <SidebarMenuSubItem v-for="subItem in item.subItems" :key="subItem.title">
                      <SidebarMenuSubButton asChild class="hover:cursor-pointer hover:bg-gray-200 text-base"
                        :class="{ 'bg-gray-200': props.active == subItem.name }" @click="handleClick(subItem.name)">
                        <span>{{ subItem.title }}</span>
                      </SidebarMenuSubButton>
                    </SidebarMenuSubItem>
                  </SidebarMenuSub>
                </CollapsibleContent>
              </Collapsible>
              <!-- Collapsible Menu (ví dụ Weather Services) -->
              <Collapsible v-else-if="item.title == 'Weather Services'">
                <CollapsibleTrigger asChild>
                  <SidebarMenuButton class="hover:cursor-pointer hover:bg-gray-200 text-base">
                    <component :is="item.icon" :class="['transition duration-300', item.iconColor]"
                      style="height: 20px; width: 20px;" />
                    <span>{{ item.title }}</span>
                    <ChevronDownIcon class="ml-auto" />
                  </SidebarMenuButton>
                </CollapsibleTrigger>
                <CollapsibleContent>
                  <SidebarMenuSub>
                    <SidebarMenuSubItem v-for="subItem in item.subItems" :key="subItem.title">
                      <SidebarMenuSubButton asChild class="hover:cursor-pointer hover:bg-gray-200 text-base"
                        :class="{ 'bg-gray-200': props.active == subItem.name }" @click="handleClick(subItem.name)">
                        <span>{{ subItem.title }}</span>
                      </SidebarMenuSubButton>
                    </SidebarMenuSubItem>
                  </SidebarMenuSub>
                </CollapsibleContent>
              </Collapsible>
            </template>
          </SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </SidebarContent>
    <SidebarFooter>
      <SidebarMenu>
        <SidebarMenuItem>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <SidebarMenuButton class="flex h-20 hover:bg-gray-200 hover:cursor-pointer relative">
                <!-- Hiển thị ảnh người dùng nếu có, nếu không thì dùng icon User2 -->
                <img v-if="userImage" :src="userImage" alt="User Image" class="h-14 w-14 rounded-md"/>
                <div class="flex flex-col">
                  <span class="text-lg font-semibold h-5 flex items-center mb-1">{{ displayName() }}</span>
                  <span class="text-sm text-gray-600 h-5">{{ displayFullName() }}</span>
                </div>
                <ChevronUpIcon class="ml-auto" />
              </SidebarMenuButton>
            </DropdownMenuTrigger>
            <DropdownMenuContent side="right"
              class="w-[--reka-popper-anchor-width] z-[1001] bg-white rounded-md shadow-md border border-gray-200 mb-2 ml-1">
              <DropdownMenuItem class="flex items-center px-4 py-2 text-sm hover:bg-gray-100" @click="logout">
                <LogOutIcon class="w-4 h-4 mr-2" />
                <span>Log out</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </SidebarMenuItem>
      </SidebarMenu>
    </SidebarFooter>
  </Sidebar>
</template>