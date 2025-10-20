<template>
  <div class="flex justify-center items-center w-full h-full">
    <div class="w-[500px] h-[500px]">
      <Pie :data="formattedData" :options="options" />
    </div>
  </div>
</template>

<script setup>
import { Pie } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title, Tooltip, Legend,
  ArcElement
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, ArcElement)

const props = defineProps({
  data: {
    type: Array,
    required: true
  }
})

const formattedData = {
  labels: props.data.map(d => d.year),
  datasets: [{
    label: 'Number of disasters',
    backgroundColor: [
      '#f87171', '#60a5fa', '#34d399', '#fbbf24', '#c084fc',
      '#f472b6', '#22d3ee', '#a3e635', '#fb923c', '#c084fc'
    ],
    data: props.data.map(d => d.count)
  }]
}

const options = {
  responsive: true,
  maintainAspectRatio: false, // 👈 để chart fit theo div bọc
  plugins: {
    legend: {
      display: false
    }
  }
}
</script>
