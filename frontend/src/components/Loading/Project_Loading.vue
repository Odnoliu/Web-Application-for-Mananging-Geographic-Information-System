<template>
  <div class="flex flex-col items-center justify-center h-screen bg-white">
    <!-- Map Icon with floating animation -->
    <MapPin class="w-40 h-40 text-red-500 animate-float z-10" />
    
    <!-- Loading text with animated dots -->
    <div class="mt-6 text-3xl font-bold text-gray-700 z-10">
      Please wait a moment, your project is being initialized{{ dots }}
    </div>
    
    <!-- Spinning gear icon -->
    <Settings class="absolute w-120 h-120 mt-4 text-gray-400 animate-spin opacity-20" />
  </div>
</template>

<script>
import { MapPin, Settings } from 'lucide-vue-next';
import { onMounted, onBeforeUnmount, ref } from 'vue';

export default {
  name: 'LoadingComponent',
  components: {
    MapPin,
    Settings,
  },
  setup() {
    const dots = ref('');

    const animateDots = () => {
      const interval = setInterval(() => {
        if (dots.value.length < 3) {
          dots.value += '.';
        } else {
          dots.value = '';
        }
      }, 500);

      // Clean up interval on component unmount
      onBeforeUnmount(() => {
        clearInterval(interval);
      });
    };

    onMounted(() => {
      animateDots();
    });

    return {
      dots,
    };
  },
};
</script>

<style scoped>
/* Floating animation for the map icon */
.animate-float {
  animation: float 2s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

/* Spinning animation for the gear icon */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>