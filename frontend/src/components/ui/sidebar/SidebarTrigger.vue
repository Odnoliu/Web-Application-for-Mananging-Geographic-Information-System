<script setup lang="ts">
import type { HTMLAttributes } from 'vue'
import {  MenuIcon, PanelLeft } from 'lucide-vue-next'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { useSidebar } from './utils'

const props = defineProps<{
  class?: HTMLAttributes['class']
}>()

</script>

<template>
  <Button
    data-sidebar="trigger"
    data-slot="sidebar-trigger"
    variant="ghost"
    :class="cn('h-12 w-12', props.class)"
    class="[&_svg:not([class*='size-'])]:size-6 bg-neutral-100 hover:bg-neutral-200 hover:cursor-pointer"
  >
    <MenuIcon class="h-12 w-12"></MenuIcon>
  </Button>
</template>
