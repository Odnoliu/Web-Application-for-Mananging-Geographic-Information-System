<template>
  <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none"
    stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
    class="lucide lucide-map-pin-check-inside-icon lucide-map-pin-check-inside">
    
    <!-- Gradient đỏ -->
    <defs>
      <linearGradient id="redGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#ef4444" />
        <stop offset="100%" stop-color="#f43f5e" />
      </linearGradient>
    </defs>

    <!-- Viền ngoài -->
    <path
      d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"
      :stroke="outerColor || 'url(#redGradient)'" />

    <!-- Dấu tích -->
    <path d="m9 10 2 2 4-4" :stroke="checkColor" />
  </svg>
</template>

<script setup>
defineProps({
  // Cho phép ghi đè màu viền ngoài, nếu không có sẽ dùng gradient đỏ
  outerColor: {
    type: String,
    default: '' // để trống thì dùng gradient mặc định
  },
  // Dấu tích màu vàng sáng (tốt trên nền biển và xanh lá)
  checkColor: {
    type: String,
    default: '#af4c0f'
  }
})
</script>
