<template>
  <div class="container mx-auto px-6 lg:px-20 w-full h-full relative">
    <!-- Loading state -->
    <div v-if="loading"
      class="flex flex-col justify-center items-center space-y-3 absolute inset-0 bg-white/60 backdrop-blur-md z-50">
      <Skeleton class="h-[175px] w-[375px] rounded-2xl shadow-md" />
      <div class="space-y-2">
        <Skeleton class="h-5 w-[375px] rounded-md" />
        <Skeleton class="h-5 w-[325px] rounded-md" />
      </div>
    </div>

    <!-- Main Content -->
    <div v-else class="w-full h-full bg-gradient-to-b from-zinc-50 to-zinc-100 py-8">
      <!-- Menu -->
      <div class="w-full p-6">
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          <div v-for="(item, index) in menuItems" :key="index"
            class="flex flex-col items-center justify-center p-5 rounded-2xl border border-gray-200 bg-white shadow-sm transition-all duration-300 cursor-pointer group hover:shadow-xl hover:-translate-y-1 hover:border-l-4"
            :class="item.hover" @click="handleMenuClick(item.name)">
            <component :is="item.icon" class="w-10 h-10 mb-3 transition-transform duration-300 group-hover:scale-110"
              :class="item.color" />
            <span class="text-sm font-semibold text-gray-700 group-hover:text-black tracking-wide">
              {{ item.label }}
            </span>
          </div>
        </div>
      </div>
      <!-- GIS Introduction -->
      <div class="max-w-7xl mx-auto flex gap-4 items-center p-4">

        <!-- Card Flip -->
        <RotatingCard
          frontImage="https://images.squarespace-cdn.com/content/v1/5ef40ad4d12d183b9a464793/1644930329261-76QHRZ08YHXS8XR67O91/shutterstock_722938309.jpg"
          frontTitle="What is GIS?" frontDescription="Hover to discover how Vector GIS works"
          backImage="https://onekeyresources.milwaukeetool.com/hubfs/GIS-Blog-Header.jpg"
          backTitle="GIS & Vector Format" backDescription="GIS (Geographic Information System) is a framework for capturing,
            managing, and analyzing spatial data. Vector formats (points, lines,
            polygons) allow precise geographic representation and advanced
            spatial analysis." />
        <!-- Feature list -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <!-- Card 1 -->
          <div
            class="p-6 shadow-md rounded-2xl hover:shadow-lg hover:scale-[1.02] transition transform bg-white flex flex-col items-start gap-3">
            <span class="text-green-600 text-2xl">📊</span>
            <h4 class="font-bold text-lg">FID - Flexible Integrated for Development</h4>
            <p class="text-gray-600 text-sm">
              A system providing essential tools for managing and processing
              vector-based GIS files, along with fast and reliable geospatial
              services.
            </p>
          </div>

          <!-- Card 2 -->
          <div
            class="p-6 shadow-md rounded-2xl hover:shadow-lg hover:scale-[1.02] transition transform bg-white flex flex-col items-start gap-3">
            <span class="text-green-600 text-2xl">🗂️</span>
            <h4 class="font-bold text-lg">Supported GIS Formats</h4>
            <p class="text-gray-600 text-sm">
              Our system supports JSON, GeoJSON, Shapefile, Geopackage, and KMZ
              formats, ensuring compatibility with diverse GIS workflows.
            </p>
          </div>

          <!-- Card 3 -->
          <div
            class="p-6 shadow-md rounded-2xl hover:shadow-lg hover:scale-[1.02] transition transform bg-white flex flex-col items-start gap-3">
            <span class="text-green-600 text-2xl">👥</span>
            <h4 class="font-bold text-lg">Strong GIS Community</h4>
            <p class="text-gray-600 text-sm">
              A smooth and creative map experience where users can freely share
              and access geographic data from peers and communities.
            </p>
          </div>

          <!-- Card 4 -->
          <div
            class="p-6 shadow-md rounded-2xl hover:shadow-lg hover:scale-[1.02] transition transform bg-white flex flex-col items-start gap-3">
            <span class="text-green-600 text-2xl">🗺️</span>
            <h4 class="font-bold text-lg">Mapping Technology</h4>
            <p class="text-gray-600 text-sm">
              Built on OpenLayers and Mapbox, delivering efficient and powerful
              map rendering and management solutions.
            </p>
          </div>
        </div>

      </div>
      <!-- GIS News -->
      <h3 class="flex items-center gap-3 text-2xl font-semibold mt-8 mb-4 border-b pb-2 border-gray-200 text-gray-800">
        <img src="@/assets/earth.gif" alt="News GIF" class="h-7 w-7">
        GIS News
      </h3>
      <div class="flex-1 flex flex-col mb-20">
        <Carousel :plugins="[Autoplay({ delay: 4000 })]" :opts="{ loop: true, align: 'start' }"
          @init-api="carouselApi = $event" class="bg-white rounded-2xl shadow-md">
          <CarouselContent>
            <CarouselItem v-for="article in filteredArticles" :key="article.url">
              <div class="flex gap-4 p-4">
                <img :src="article.urlToImage" alt="newsImage"
                  class="h-52 w-72 object-cover rounded-xl shadow-sm hover:scale-105 transition-transform duration-300">
                <div class="flex-1 flex flex-col gap-3">
                  <p class="text-xl font-semibold text-gray-800 line-clamp-2">{{ article.title }}</p>
                  <p class="text-gray-600 line-clamp-3">{{ article.description || 'Không có mô tả' }}</p>
                  <Button as="a" :href="article.url" target="_blank"
                    class="w-fit px-4 py-2 bg-gradient-to-r from-lime-500 to-green-500 text-white rounded-lg shadow hover:shadow-lg hover:opacity-90 transition-all">
                    Read more →
                  </Button>
                </div>
              </div>
            </CarouselItem>
          </CarouselContent>
        </Carousel>
      </div>

      <!-- Weather -->
      <h3 class="flex items-center gap-3 text-2xl font-semibold mt-8 mb-4 border-b pb-2 border-gray-200 text-gray-800">
        <img src="@/assets/weather.gif" alt="Weather GIF" class="h-8 w-8">
        Weather Broadcast
      </h3>
      <div
        class="flex flex-1 border border-gray-200 shadow-md rounded-2xl bg-gradient-to-br from-sky-50 to-white overflow-hidden">
        <!-- Weather Info -->
        <div v-if="weatherData" class="flex-1 p-6">
          <!-- City + Date -->
          <div class="flex items-center gap-3 mb-6">
            <h3 class="text-2xl font-bold text-blue-900">{{ weatherData.city }}, {{ weatherData.country }}</h3>
            <span class="text-gray-600">{{ formattedDate }}</span>
          </div>

          <!-- Weather stats -->
          <div class="grid grid-cols-2 gap-4 text-gray-700">
            <div class="flex items-center gap-2">
              <img src="../assets/temp-high-svgrepo-com.svg" class="h-6 w-6">
              <b>Temperature:</b> {{ weatherData.temperature }}
            </div>
            <div class="flex items-center gap-2">
              <img src="../assets/weather-svgrepo-com.svg" class="h-6 w-6">
              <b>Weather:</b> {{ weatherData.description }}
            </div>
            <div class="flex items-center gap-2">
              <img src="../assets/humidity-svgrepo-com.svg" class="h-6 w-6">
              <b>Humidity:</b> {{ weatherData.humidity }}
            </div>
            <div class="flex items-center gap-2">
              <img src="../assets/sea-level-rise-svgrepo-com.svg" class="h-6 w-6">
              <b>Sea level:</b> {{ weatherData.sea_level }}
            </div>
            <div class="flex items-center gap-2">
              <img src="../assets/wind-svgrepo-com.svg" class="h-6 w-6">
              <b>Wind speed:</b> {{ weatherData.wind_speed }}
            </div>
          </div>

          <!-- Forecast line -->
          <div class="mt-6 p-4 rounded-xl bg-blue-50 border border-blue-100 shadow-sm">
            <p class="text-blue-800 font-medium italic">
              🌤️ Today’s Forecast:
              <span class="font-semibold">{{ weatherData.forecast || weatherData.description }}</span>
            </p>
          </div>
        </div>

        <!-- Map -->
        <div class="h-80 w-96" ref="mapContainer"></div>
      </div>

      <!-- Videos -->
      <h3 class="flex items-center gap-3 text-2xl font-semibold mt-12 mb-4 border-b pb-2 border-gray-200 text-gray-800">
        <img src="@/assets/youtube.gif" alt="YouTube GIF" class="h-8 w-8" />
        Explore the World of GIS Through Videos
      </h3>

      <Carousel class="w-full">
        <CarouselContent>
          <CarouselItem v-for="(item, index) in newsItems" :key="index" class="md:basis-1/3">
            <div
              class="video-card opacity-0 translate-y-8 p-4 h-full rounded-2xl shadow-md bg-white transition-all duration-700">
              <iframe :src="item.videoUrl" class="w-full h-44 rounded-lg" frameborder="0" allowfullscreen></iframe>
              <div class="p-2">
                <h4 class="text-lg font-semibold text-yellow-600 mb-2 hover:underline">
                  {{ item.title }}
                </h4>
                <p class="text-gray-600 text-sm">{{ item.description }}</p>
              </div>
            </div>
          </CarouselItem>
        </CarouselContent>
      </Carousel>
    </div>
  </div>
</template>


<script setup lang="ts">
import RotatingCard from '../components/rotatingCards/RotatingCard.vue'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious } from './ui/carousel';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import axios from 'axios';
import { ref, onMounted, computed, nextTick, defineEmits } from 'vue'; // Thêm nextTick
import Autoplay from 'embla-carousel-autoplay';
import { Icon } from '@iconify/vue';
import { weatherIconMap, iconColorMap } from '@/modules/weather_icon';
import { createMap, addUserPosition } from '@/modules/mapbox';
import { Home, Layers, Map, GraduationCap, Hospital, Store, Waves, CloudSun, Database, Recycle } from "lucide-vue-next";
const articles = ref([]);
const formattedDate = ref('');
const loading = ref(true);
const error = ref('');
const carouselApi = ref();
const weatherData = ref(null);
const mapContainer = ref<HTMLDivElement | null>(null);
const emit = defineEmits(['update:active']);
const menuItems = [
  { label: 'Home', icon: Home, color: 'text-blue-600', hover: 'hover:bg-blue-50', name: 'UserHome' },
  { label: 'GIS Project', icon: Layers, color: 'text-green-600', hover: 'hover:bg-green-50', name: 'CustomGISProject' },
  { label: 'GIS Service', icon: Database, color: 'text-teal-600', hover: 'hover:bg-teal-50', name: 'GISCommunity' },
  { label: 'Recycle Bin', icon: Recycle, color: 'text-lime-600', hover: 'hover:bg-lime-50', name: 'RecycleBin' }
];
const handleMenuClick = (name: string) => {
  console.log(name)
  emit('update:active', name);
};
const fetchNews = async () => {
  try {
    const response = await axios.get('http://localhost:8000/news/get_news');
    if (response.status === 200) {
      articles.value = response.data.articles;
    } else {
      error.value = response.data.error;
    }
  } catch (err) {
    error.value = 'Lỗi khi tải tin tức';
    console.error('Fetch news error:', err);
  }
};

const fetchWeather = async () => {
  let lat: number, lon: number;

  const getPosition = (): Promise<GeolocationPosition> => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Trình duyệt không hỗ trợ định vị.'));
      } else {
        navigator.geolocation.getCurrentPosition(resolve, reject, {
          enableHighAccuracy: true,
          timeout: 5000,
          maximumAge: 0,
        });
      }
    });
  };

  try {
    const position = await getPosition();
    lat = position.coords.latitude;
    lon = position.coords.longitude;

    const response = await axios.post('http://localhost:8000/weather/get_weather', {
      lat,
      lon,
    });
    weatherData.value = response.data;
    console.log('Weather data:', weatherData.value);
    return { lat, lon };
  } catch (err: any) {
    error.value = err.message || 'Lỗi khi lấy dữ liệu thời tiết';
    console.error('Fetch weather error:', err.message);
    return null;
  }
};

const newsItems = ref([
  {
    videoUrl: "https://www.youtube.com/embed/WpoSofhf9Y0", // Thay bằng ID video thực tế
    title: "What is GIS? Overview of GIS",
    description: "Geospatial Information Systems (GIS) is a unique problem-solving technology with remarkable impact",
  },
  {
    videoUrl: "https://www.youtube.com/embed/3DVgQFALxCo", // Thay bằng ID video thực tế
    title: "Vector vs Raster Data - GIS Explained",
    description: "In the subject of Geographic Information Systems (GIS), the vector and raster formats are two ways of representing real-world phenomena on a digital map",
  },
  {
    videoUrl: "https://www.youtube.com/embed/zHDHDC6dWS4", // Thay bằng ID video thực tế
    title: "AI and GIS",
    description: "AI combined with location technology is helping organizations around the world realize the promise of building a better future.",
  },
]);
const visibleItems = ref([]);
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

const updateDate = () => {
  const today = new Date();
  formattedDate.value = today.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
};

const filteredArticles = computed(() => {
  return articles.value
    .filter((article) => article.urlToImage)
    .filter((article) => {
      return (
        article.source.name.includes('Esri.com') &&
        formatDate(article.publishedAt) !== 'May 14, 2025'
      );
    });
});

const createUserMap = async (container: HTMLDivElement, lat: number, lon: number) => {
  if (!container) {
    console.error('mapContainer is null');
    return;
  }
  try {
    const map = createMap(container, {
      center: [105.769154, 10.031100], // Mapbox dùng [longitude, latitude]
      zoom: 15,
      attributionControl: false,
    });
    await addUserPosition(map, 105.769154, 10.031100);
    console.log('Map initialized successfully');
  } catch (err) {
    console.error('Error creating map:', err);
  }
};

onMounted(async () => {
  updateDate();
  await Promise.all([fetchNews(), fetchWeather()]).then(async ([_, coords]) => {
    loading.value = false;
    // Đợi DOM cập nhật sau khi loading = false
    await nextTick();
    if (coords && mapContainer.value) {
      createUserMap(mapContainer.value, coords.lat, coords.lon);
    } else {
      console.error('Map container or coordinates not available', {
        mapContainer: mapContainer.value,
        coords,
      });
      if (!coords) {
        error.value = 'Không thể lấy tọa độ vị trí. Vui lòng cấp quyền vị trí hoặc kiểm tra kết nối.';
      }
      if (!mapContainer.value) {
        error.value = 'Không tìm thấy container bản đồ. Vui lòng kiểm tra giao diện.';
      }
    }
  });
    const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("animate-floatIn");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.2 }
  );

  document.querySelectorAll(".video-card").forEach((el) => {
    observer.observe(el);
  });
});
</script>
<style scoped>
.perspective {
  perspective: 1000px;
}
.backface-hidden {
  backface-visibility: hidden;
  transform-style: preserve-3d;
}
/* custom float-in animation */
@keyframes floatIn {
  0% {
    opacity: 0;
    transform: translateY(40px);
  }
  100% {
    opacity: 1;
    transform: translateY(-40px);
  }
}
.animate-floatIn {
  animation: floatIn 0.9s ease-out forwards;
}
</style>
