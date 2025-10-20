<template>
  <div class="p-4 border rounded-xl shadow">
    <h2 class="text-xl font-bold mb-2">📄 Danh sách thiên tai tại Việt Nam</h2>
    <select v-model="type" class="mb-2 p-2 border rounded">
      <option value="All">Tất cả</option>
      <option v-for="t in disasterTypes" :key="t">{{ t }}</option>
    </select>
    <ul class="overflow-y-auto max-h-60">
      <li v-for="(d, i) in filteredDisasters" :key="i">
        ✅ {{ d.fields.name }} - {{ d.fields.type[0].name }}
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'

const disasters = ref([])
const type = ref('Bão')
const disasterTypes = ref([])

const fetchData = async () => {
  const res = await fetch('https://api.reliefweb.int/v1/disasters?appname=vue-app&profile=lite&limit=100')
  const data = await res.json()
  disasters.value = data.data.filter(d => d.fields.country?.some(c => c.name === 'Viet Nam'))
  disasterTypes.value = [...new Set(disasters.value.flatMap(d => d.fields.type.map(t => t.name)))]
}

onMounted(fetchData)

const filteredDisasters = computed(() => {
  if (type.value === 'All') return disasters.value
  return disasters.value.filter(d => d.fields.type.some(t => t.name === type.value))
})
</script>
