<script setup lang="ts">
import {Pointer, Layers} from 'lucide-vue-next'
defineProps<{
  frontImage: string;
  frontTitle: string;
  frontDescription: string;
  backImage: string;
  backTitle: string;
  backDescription: string;
}>();
</script>

<template>
  <div class="w-full h-full rounded-2xl cursor-pointer mx-auto">
    <div class="relative w-full h-117 rounded-lg shadow-md ring-2 ring-green-500 card-rotate">
      <!-- Front -->
      <div
        class="absolute inset-0 flex flex-col items-center justify-center rounded-lg bg-cover bg-center front-background"
        :style="{ backgroundImage: `url(${frontImage})` }">
        <div class="absolute inset-0 bg-black/70 rounded-lg"></div>
        <div class="relative pt-7 p-6 text-center">
          <div class="flex items-center justify-center w-full">
            <Pointer class="text-white h-12 w-12 my-3" />
          </div>
          <h3 class="text-white text-2xl font-bold" v-html="frontTitle"></h3>
          <p class="text-white text-center">
            {{ frontDescription }}
          </p>
        </div>
      </div>

      <!-- Back -->
      <div
        class="absolute inset-0 flex flex-col items-center justify-center rounded-lg bg-cover bg-center back-background"
        :style="{ backgroundImage: `url(${backImage})` }">
        <div class="absolute inset-0 bg-black/70 rounded-lg"></div>
         <div class="relative pt-7 p-6 text-center">
          <div class="flex items-center justify-center w-full">
            <Layers class="text-white h-12 w-12 my-3" />
          </div>
          <h3 class="text-white text-2xl font-bold" v-html="backTitle"></h3>
          <p class="text-white text-center">
            {{ backDescription }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card-rotate {
  transition: transform 0.7s ease-in-out;
  transform-style: preserve-3d;
}
.card-rotate:hover {
  transform: rotateY(180deg);
}
.front-background,
.back-background {
  backface-visibility: hidden;
}
.back-background {
  transform: rotateY(180deg);
}
</style>