<template>
  <Bar :data="formattedData" :options="options" />
</template>

<script setup>
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title, Tooltip, Legend,
  BarElement, CategoryScale, LinearScale
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)

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
    backgroundColor: '#3b82f6',
    data: props.data.map(d => d.count)
  }]
}

const options = {
  responsive: true,
  plugins: {
    legend: {
      display: false
    }
  }
}
</script>
