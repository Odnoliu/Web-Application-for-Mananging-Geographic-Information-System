<template>
  <div class="p-4 border rounded-xl shadow">
    <h2 class="text-xl font-bold mb-2">📈 Thống kê thiên tai tại Việt Nam</h2>
    <div class="flex gap-2 mb-2">
      <select v-model="selectedType" class="p-1 border rounded">
        <option v-for="t in disasterTypes" :key="t">{{ t }}</option>
      </select>
      <select v-model="chartType" class="p-1 border rounded">
        <option value="bar">Biểu đồ cột</option>
        <option value="pie">Biểu đồ tròn</option>
        <option value="area">Biểu đồ miền</option>
      </select>
    </div>

    <component :is="chartTypeComponent" :data="chartData" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import BarChart from '../Charts/BarChart.vue'
import PieChart from '../Charts/PieChart.vue'
import AreaChart from '../Charts/AreaChart.vue'

const disasters = ref([])
const selectedType = ref('Bão')
const chartType = ref('bar')
const disasterTypes = ref([])

const chartTypeComponent = computed(() => {
  return {
    bar: BarChart,
    pie: PieChart,
    area: AreaChart
  }[chartType.value]
})

onMounted(async () => {
  const res = await fetch('https://api.reliefweb.int/v1/disasters?appname=vue-app&profile=lite&limit=100')
  const data = await res.json()
  disasters.value = data.data.filter(d => d.fields.country?.some(c => c.name === 'Viet Nam'))
  disasterTypes.value = [...new Set(disasters.value.flatMap(d => d.fields.type.map(t => t.name)))]
})

const chartData = computed(() => {
  const filtered = disasters.value.filter(d => d.fields.type.some(t => t.name === selectedType.value))
  const byYear = {}
  filtered.forEach(d => {
    const year = new Date(d.fields.date.created).getFullYear()
    byYear[year] = (byYear[year] || 0) + 1
  })
  return Object.entries(byYear).map(([year, count]) => ({ year, count }))
})
</script>
