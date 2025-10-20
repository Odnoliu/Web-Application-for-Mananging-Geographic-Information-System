<script setup>
import { ref, computed } from 'vue'
import {
  Bolt, X,
  ZoomIn, ZoomOut,
  RotateCcw, RotateCw,
  Undo2
} from 'lucide-vue-next'

const props = defineProps({
  map: {
    type: Object,
    required: true,
  }
})

const isOpen = ref(false)
const direction = ref('right') // 'top', 'bottom', 'left', 'right'

const positionClass = computed(() => {
  switch (direction.value) {
    case 'top': return 'bottom-full mb-2'
    case 'bottom': return 'top-full mt-2'
    case 'left': return 'right-full mr-2'
    case 'right': return 'left-full ml-2'
    default: return 'top-full mt-2'
  }
})

const layoutClass = computed(() => {
  return ['top', 'bottom'].includes(direction.value)
    ? 'flex flex-col items-center w-fit h-fit'
    : 'flex flex-row items-center w-fit h-fit'
})

const animationClass = computed(() => {
  return ['left', 'right'].includes(direction.value) ? 'slide-x' : 'slide-y'
})

const toggle = () => {
  isOpen.value = !isOpen.value
}

// Map controls
const zoomIn = () => {
  const view = props.map?.getView()
  view?.setZoom(view.getZoom() + 1)
}
const zoomOut = () => {
  const view = props.map?.getView()
  view?.setZoom(view.getZoom() - 1)
}
const rotateLeft = () => {
  const view = props.map?.getView()
  view?.setRotation(view.getRotation() - (30 * Math.PI / 180))
}
const rotateRight = () => {
  const view = props.map?.getView()
  view?.setRotation(view.getRotation() + (30 * Math.PI / 180))
}
const resetView = () => {
  if (props.map) {
    props.map.getView().setCenter([11744829.667838804 , 1951403.1096575279])
    props.map.getView().setZoom(5.5)        
    props.map.getView().setRotation(0)   
  }
}
</script>

<template>
  <div class="relative inline-flex items-center justify-center">
    <!-- Button chính -->
    <button @click="toggle" v-tooltip.right="'Control button'"
      class="w-10 h-10 rounded-md bg-gray-400 hover:bg-gray-500 text-white flex items-center justify-center transition-transform duration-400 hover:cursor-pointer">
      <component :is="isOpen ? X : Bolt" class="w-6 h-6" />
    </button>

    <!-- Các button mở rộng -->
    <transition-group tag="div" :name="animationClass" class="absolute z-10" :class="[positionClass, layoutClass]">
      <button v-tooltip.bottom="'Zoom in'" v-if="isOpen" key="zoom-in" @click="zoomIn"
        class="w-10 h-10 m-1 rounded-md bg-neutral-400 hover:bg-neutral-500 text-white flex items-center justify-center shadow hover:cursor-pointer">
        <ZoomIn class="w-6 h-6" />
      </button>
      <button v-tooltip.bottom="'Zoom out'" v-if="isOpen" key="zoom-out" @click="zoomOut"
        class="w-10 h-10 m-1 rounded-md bg-neutral-400 hover:bg-neutral-500 text-white flex items-center justify-center shadow hover:cursor-pointer">
        <ZoomOut class="w-6 h-6" />
      </button>
      <button v-tooltip.bottom="'Rotate left'" v-if="isOpen" key="rotate-left" @click="rotateLeft"
        class="w-10 h-10 m-1 rounded-md bg-neutral-400 hover:bg-neutral-500 text-white flex items-center justify-center shadow hover:cursor-pointer">
        <RotateCcw class="w-6 h-6" />
      </button>
      <button v-tooltip.bottom="'Rotate right'" v-if="isOpen" key="rotate-right" @click="rotateRight"
        class="w-10 h-10 m-1 rounded-md bg-neutral-400 hover:bg-neutral-500 text-white flex items-center justify-center shadow hover:cursor-pointer">
        <RotateCw class="w-6 h-6" />
      </button>
      <button v-tooltip.bottom="'Reset'" v-if="isOpen" key="reset" @click="resetView"
        class="w-10 h-10 m-1 rounded-md bg-neutral-400 hover:bg-neutral-500 text-white flex items-center justify-center shadow hover:cursor-pointer">
        <Undo2 class="w-6 h-6" />
      </button>
    </transition-group>

  </div>
</template>

<style scoped>
.slide-y-enter-active,
.slide-y-leave-active {
  transition: all 0.4s ease;
}

.slide-y-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.slide-y-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

.slide-x-enter-active,
.slide-x-leave-active {
  transition: all 0.4s ease;
}

.slide-x-enter-from {
  opacity: 0;
  transform: translateX(10px);
}

.slide-x-leave-to {
  opacity: 0;
  transform: translateX(10px);
}
</style>
