<template>
  <Line :data="formattedData" :options="options" />
</template>

<script setup>
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title, Tooltip, Legend,
  LineElement, PointElement, CategoryScale, LinearScale, Filler
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, Filler)

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
    backgroundColor: 'rgba(59, 130, 246, 0.3)',
    borderColor: '#3b82f6',
    fill: true,
    tension: 0.4,
    data: props.data.map(d => d.count)
  }]
}

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    x: {
      ticks: {
        autoSkip: true,   // tự động bỏ bớt label
        maxTicksLimit: 10, // chỉ hiển thị tối đa 10 nhãn
        callback: function(value, index, ticks) {
          let label = this.getLabelForValue(value)
          return label.length > 10 ? label.substring(0, 10) + '…' : label
        }
      }
    }
  }
}
</script>
