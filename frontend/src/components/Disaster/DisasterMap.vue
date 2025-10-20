<template>
  <div class="h-screen w-full flex flex-col">
    <!-- Header với các Select -->
    <div class="p-4 bg-gray-100 flex justify-end gap-4">
      <Select v-model:model-value="selectedCountry">
        <SelectTrigger class="w-[180px]">
          <SelectValue placeholder="Select Country" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="">Worldwide</SelectItem>
          <SelectItem v-for="country in countries" :key="country" :value="country">{{ country }}</SelectItem>
        </SelectContent>
      </Select>

      <Select v-model:model-value="selectedYear">
        <SelectTrigger class="w-[180px]">
          <SelectValue placeholder="Select Year" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="2025">2025</SelectItem>
          <SelectItem value="2024">2024</SelectItem>
          <SelectItem value="2023">2023</SelectItem>
        </SelectContent>
      </Select>
    </div>

    <!-- Bản đồ -->
    <div class="flex-1" ref="mapContainer"></div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue';
import mapboxgl from 'mapbox-gl';
import 'mapbox-gl/dist/mapbox-gl.css';
import { createMap } from '@/modules/mapbox';
import axios from 'axios';
import {
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from '../ui/select';

// Refs
const mapContainer = ref(null);
const map = ref(null);
const markers = ref([]); // Lưu trữ các marker để xóa sau này

// State
const selectedCountry = ref(''); // Mặc định không chọn quốc gia
const selectedYear = ref('2025');

// Danh sách 195 quốc gia (dựa trên ISO 3166-1)
const countries = [
  'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Antigua and Barbuda', 'Argentina', 'Armenia', 'Australia', 'Austria',
  'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados', 'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan',
  'Bolivia', 'Bosnia and Herzegovina', 'Botswana', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cabo Verde', 'Cambodia',
  'Cameroon', 'Canada', 'Central African Republic', 'Chad', 'Chile', 'China', 'Colombia', 'Comoros', 'Congo (Congo-Brazzaville)', 'Costa Rica',
  'Croatia', 'Cuba', 'Cyprus', 'Czechia', 'Denmark', 'Djibouti', 'Dominica', 'Dominican Republic', 'Ecuador', 'Egypt',
  'El Salvador', 'Equatorial Guinea', 'Eritrea', 'Estonia', 'Eswatini', 'Ethiopia', 'Fiji', 'Finland', 'France', 'Gabon',
  'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Grenada', 'Guatemala', 'Guinea', 'Guinea-Bissau', 'Guyana',
  'Haiti', 'Honduras', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq', 'Ireland', 'Israel',
  'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya', 'Kiribati', 'Kuwait', 'Kyrgyzstan', 'Laos',
  'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya', 'Liechtenstein', 'Lithuania', 'Luxembourg', 'Madagascar', 'Malawi',
  'Malaysia', 'Maldives', 'Mali', 'Malta', 'Marshall Islands', 'Mauritania', 'Mauritius', 'Mexico', 'Micronesia', 'Moldova',
  'Monaco', 'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nauru', 'Nepal', 'Netherlands',
  'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'North Korea', 'North Macedonia', 'Norway', 'Oman', 'Pakistan', 'Palau',
  'Panama', 'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar', 'Romania', 'Russia',
  'Rwanda', 'Saint Kitts and Nevis', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Samoa', 'San Marino', 'Sao Tome and Principe', 'Saudi Arabia', 'Senegal', 'Serbia',
  'Seychelles', 'Sierra Leone', 'Singapore', 'Slovakia', 'Slovenia', 'Solomon Islands', 'Somalia', 'South Africa', 'South Korea', 'South Sudan',
  'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland', 'Syria', 'Taiwan', 'Tajikistan', 'Tanzania',
  'Thailand', 'Timor-Leste', 'Togo', 'Tonga', 'Trinidad and Tobago', 'Tunisia', 'Turkey', 'Turkmenistan', 'Tuvalu', 'Uganda',
  'Ukraine', 'United Arab Emirates', 'United Kingdom', 'United States', 'Uruguay', 'Uzbekistan', 'Vanuatu', 'Vatican City', 'Venezuela', 'Vietnam',
  'Yemen', 'Zambia', 'Zimbabwe'
];

// Hàm tạo bản đồ với nền trắng
const initializeMap = () => {
  if (!mapContainer.value) return;
  map.value = createMap(mapContainer.value, {
    style: 'mapbox://styles/mapbox/light-v11', // Sử dụng style sáng (gần giống nền trắng)
    center: [0, 20], // Trung tâm bản đồ toàn cầu
    zoom: 2, // Zoom để hiển thị toàn thế giới
    attributionControl: false,
  });
};

// Hàm lấy dữ liệu từ ReliefWeb API
const fetchDisasters = async () => {
  // Xóa các marker cũ
  markers.value.forEach(marker => marker.remove());
  markers.value = [];

  // Xây dựng bộ lọc
  const filters = [
    {
      field: 'status',
      value: ['ongoing', 'alert'], // Lấy các thiên tai đang xảy ra
    },
  ];

  // Thêm bộ lọc thời gian
  const year = selectedYear.value;
  filters.push({
    field: 'date.created',
    value: {
      from: `${year}-01-01T00:00:00+00:00`,
      to: `${year}-12-31T23:59:59+00:00`,
    },
  });

  // Thêm bộ lọc theo quốc gia nếu đã chọn (khác Worldwide)
  if (selectedCountry.value) {
    filters.push({
      field: 'country.name',
      value: selectedCountry.value,
    });
  }

  try {
    const res = await axios.post('https://api.reliefweb.int/v2/disasters?appname=vue-app&profile=full&limit=1000', {
      filter: {
        operator: 'AND',
        conditions: filters,
      },
    });

    const data = res.data;
    console.log('Dữ liệu API:', data);

    if (data.data && data.data.length > 0) {
      data.data.forEach(disaster => {
        disaster.fields.country.forEach(location => {
          if (location.location && (!selectedCountry.value || location.name == selectedCountry.value)) {
            const lat = location.location.lat;
            const lon = location.location.lon;

            // Chọn icon dựa trên loại thiên tai
            let iconHtml = '<div style="background: red; width: 20px; height: 20px; border-radius: 50%;"></div>'; // Mặc định là đỏ
            if (disaster.fields.type?.[0]?.name == 'Flood') iconHtml = '<div style="background: blue; width: 20px; height: 20px; border-radius: 50%;"></div>';
            if (disaster.fields.type?.[0]?.name == 'Storm') iconHtml = '<div style="background: orange; width: 20px; height: 20px; border-radius: 50%;"></div>';

            const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(`
              <b>${disaster.fields.name || 'Unknown'}</b><br>
              ${disaster.fields.type?.[0]?.name || 'Unknown'}<br>
              ${new Date(disaster.fields.date.created).toLocaleDateString()}
            `);

            const marker = new mapboxgl.Marker({ element: createCustomMarker(iconHtml) })
              .setLngLat([lon, lat])
              .setPopup(popup)
              .addTo(map.value);
            markers.value.push(marker);
          }
        });
      });
    } else {
      console.log('Không tìm thấy thiên tai nào.');
    }
  } catch (error) {
    console.error('Lỗi khi lấy dữ liệu thiên tai:', error);
  }
};
// Hàm tạo marker tùy chỉnh
const createCustomMarker = (html) => {
  const el = document.createElement('div');
  el.innerHTML = html;
  return el.firstChild;
};

// Watch để debug
watch(selectedCountry, (newVal) => {
  if(newVal){
    fetchDisasters();
  }
});

watch(selectedYear, (newVal) => {
  if(newVal){
    fetchDisasters();
  }
});

// Khởi tạo bản đồ và gọi API khi component mount
onMounted(() => {
  initializeMap();
  fetchDisasters();
});
</script>

<style scoped>
/* Tùy chỉnh giao diện nếu cần */
</style>