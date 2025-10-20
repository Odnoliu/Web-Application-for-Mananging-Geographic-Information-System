<template>
  <div class="container mx-auto p-4">
    <h3 class="italic opacity-75 flex items-center gap-2 text-2xl font-bold mt-6 mb-4 border-b border-gray-300">
      <img src="@/assets/community.gif" alt="Community GIF" class="h-6 w-6 animate-pulse">
      GIS COMMUNITY
    </h3>

    <!-- Div điều khiển bố cục grid/list -->
    <div class="flex justify-end mb-4">
      <div class="flex">
        <Button v-tooltip.bottom="'List mode'" class="w-15 h-10 rounded-sm rounded-r-none cursor-pointer shadow-lg"
          :class="viewMode == 'list' ? 'bg-sky-300 hover:bg-sky-400' : 'bg-gray-200 hover:bg-gray-300'"
          @click="viewMode = 'list'" title="List view">
          <ListIcon class="w-8 h-8" />
        </Button>
        <Button v-tooltip.bottom="'Grid mode'" class="w-15 h-10 rounded-sm rounded-l-none cursor-pointer shadow-lg"
          :class="viewMode == 'grid' ? 'bg-sky-300 hover:bg-sky-400' : 'bg-gray-200 hover:bg-gray-300'"
          @click="viewMode = 'grid'" title="Grid view">
          <GridIcon class="w-8 h-8" />
        </Button>
      </div>
    </div>

    <!-- Tabs -->
    <Tabs v-model="activeTab" class="w-full">
      <TabsList class="grid w-200 h-13 grid-cols-4 bg-gray-300">
        <TabsTrigger value="layer">Layer Community</TabsTrigger>
        <TabsTrigger value="feature">Feature Community</TabsTrigger>
        <TabsTrigger value="friends">Shared With Me</TabsTrigger>
        <TabsTrigger value="user">My Data</TabsTrigger>
      </TabsList>

      <!-- Tab Content: Layer Community -->
      <TabsContent value="layer" class="mt-3">
        <div class="h-full w-full" v-if="sortedLayerCommunities.length">
          <div v-if="viewMode == 'grid'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card v-for="item in sortedLayerCommunities" :key="item.layer_community_id"
              class="transition-transform duration-200 ease-in-out gap-2 transform hover:scale-105 hover:shadow-lg h-80">
              <CardHeader>
                <CardTitle class="text-lg font-semibold truncate">{{ item.layer_community_name }}</CardTitle>
              </CardHeader>
              <CardContent class="flex flex-col gap-2">
                <p class="text-sm text-gray-600 truncate">{{ item.layer_community_description || 'No description' }}</p>
                <img v-if="item.layer_community_image" :src="formatImageSrc(item.layer_community_image)"
                  alt="Layer image" class="h-40 w-full rounded"
                  @error="handleImageError(item.layer_community_id, 'layer')" />
              </CardContent>
              <CardFooter class="flex justify-end gap-2">
                <Button v-tooltip.bottom="'Review'" class="bg-sky-400 text-white hover:bg-sky-500 cursor-pointer" size="icon"
                  @click="changeLayer(item.layer_id)">
                  <View class="w-4 h-4" />
                </Button>
              </CardFooter>
            </Card>
          </div>
          <div v-else class="w-full h-full">
            <div class="py-4 px-6">
              <!-- Header Row -->
              <div class="flex items-center border-b">
                <div class="flex-shrink-0 w-20 h-10 flex items-center justify-center text-gray-600">Image</div>
                <div v-tooltip="'Sort by name'" class="flex-1 min-w-0 flex items-center gap-1 cursor-pointer hover:bg-gray-200 px-4 py-2 rounded"
                  @click="toggleSort('name')">
                  <span class="text-gray-700 font-normal">Name</span>
                  <span :class="{ 'rotate-180': sortDirection.name == 'desc' }"
                    class="transition-transform duration-200">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </span>
                </div>
                <div class="w-32 flex items-center justify-center text-gray-600">Owner</div>
                <div v-tooltip="'Sort by date'" class="w-33 flex items-center gap-1 cursor-pointer hover:bg-gray-200 px-2 py-2 rounded"
                  @click="toggleSort('date')">
                  <span class="text-gray-700 font-normal">Created Date</span>
                  <span :class="{ 'rotate-180': sortDirection.date == 'desc' }"
                    class="transition-transform duration-200">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </span>
                </div>
                <div class="w-16"></div>
              </div>
            </div>
            <div v-for="item in sortedLayerCommunities" :key="item.layer_community_id"
              class="transition-transform py-4 px-6 w-full bg-white rounded-lg mb-4 flex items-center gap-4 hover:scale-[1.02] hover:shadow-md duration-200 ease-in-out">
              <!-- Image -->
              <div class="flex-shrink-0 w-20 h-20">
                <img v-if="item.layer_community_image" :src="formatImageSrc(item.layer_community_image)"
                  alt="Layer image" class="w-full h-full object-cover rounded-md shadow-md"
                  @error="handleImageError(item.layer_community_id, 'layer')" />
                <div v-else class="w-full h-full bg-gray-200 rounded-md flex items-center justify-center text-gray-500">
                  No Image
                </div>
              </div>

              <!-- Name and Description -->
              <div class="flex-1 min-w-0">
                <h3 class="text-lg font-semibold text-gray-800 truncate">{{ item.layer_community_name }}</h3>
                <p class="text-sm text-gray-600 line-clamp-2">{{ item.layer_community_description }}</p>
              </div>

              <!-- Owner -->
              <div class="w-32 flex items-center gap-2">
                <img v-if="getUserImage(item.user_id)" :src="getUserImage(item.user_id)" alt="User image"
                  class="w-10 h-10 rounded-full object-cover" @error="handleImageError(item.user_id, 'user')" />
                <div v-else
                  class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 text-xs">
                  No Img
                </div>
                <span class="text-sm text-gray-700 truncate">{{ getUserName(item.user_id) }}</span>
              </div>

              <!-- Created At -->
              <div class="w-32 text-sm text-gray-600">
                {{ formatDate(item.created_at) }}
              </div>

              <!-- Actions -->
              <div class="flex gap-2">

                <button v-tooltip.bottom="'Review'" class="p-2 bg-sky-400 text-white rounded-full cursor-pointer hover:bg-sky-500 transition-colors"
                  @click="changeLayer(item.layer_id)">
                  <View class="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="h-full w-full flex items-center justify-center text-center">
          <p class="text-gray-500 text-lg">
            No layers have been uploaded to the community yet.
          </p>
        </div>
      </TabsContent>

      <!-- Tab Content: Feature Community -->
      <TabsContent value="feature" class="mt-3">
        <div class="h-full w-full" v-if="sortedFeatureCommunities.length">
          <div v-if="viewMode == 'grid'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card v-for="item in sortedFeatureCommunities" :key="item.feature_community_id"
              class="transition-transform duration-200 ease-in-out gap-2 transform hover:scale-105 hover:shadow-lg h-80">
              <CardHeader>
                <CardTitle class="text-lg font-semibold truncate">{{ item.feature_community_name }}</CardTitle>
              </CardHeader>
              <CardContent class="flex flex-col gap-2">
                <p class="text-sm text-gray-600 truncate">{{ item.feature_community_description || 'No description' }}
                </p>
                <img v-if="item.feature_community_image" :src="formatImageSrc(item.feature_community_image)"
                  alt="Feature image" class="h-40 w-full rounded"
                  @error="handleImageError(item.feature_community_id, 'feature')" />
              </CardContent>
              <CardFooter class="flex justify-end gap-2">
                <Button v-tooltip.bottom="'Review'" class="bg-sky-400 text-white hover:bg-sky-500 cursor-pointer" size="icon"
                  @click="changeFeature(item.feature_id)">
                  <View class="w-4 h-4" />
                </Button>
              </CardFooter>
            </Card>
          </div>
          <div v-else class="w-full h-full">
            <div class="py-4 px-6">
              <!-- Header Row -->
              <div class="flex items-center border-b">
                <div class="flex-shrink-0 w-20 h-10 flex items-center justify-center text-gray-600">Image</div>
                <div v-tooltip="'Sort by name'" class="flex-1 min-w-0 flex items-center gap-1 cursor-pointer hover:bg-gray-200 px-4 py-2 rounded"
                  @click="toggleFeatureSort('name')">
                  <span class="text-gray-700 font-normal">Name</span>
                  <span :class="{ 'rotate-180': sortDirection.name == 'desc' }"
                    class="transition-transform duration-200">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </span>
                </div>
                <div class="w-32 flex items-center justify-center text-gray-600">Owner</div>
                <div v-tooltip="'Sort by date'" class="w-33 flex items-center gap-1 cursor-pointer hover:bg-gray-200 px-2 py-2 rounded"
                  @click="toggleFeatureSort('date')">
                  <span class="text-gray-700 font-normal">Created Date</span>
                  <span :class="{ 'rotate-180': sortDirection.date == 'desc' }"
                    class="transition-transform duration-200">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </span>
                </div>
                <div class="w-16"></div>
              </div>
            </div>
            <div v-for="item in sortedFeatureCommunities" :key="item.feature_community_id"
              class="transition-transform py-4 px-6 w-full bg-white rounded-lg mb-4 flex items-center gap-4 hover:scale-[1.02] hover:shadow-md duration-200 ease-in-out">
              <!-- Image -->
              <div class="flex-shrink-0 w-20 h-20">
                <img v-if="item.feature_community_image" :src="formatImageSrc(item.feature_community_image)"
                  alt="Feature image" class="w-full h-full object-cover rounded-md shadow-md"
                  @error="handleImageError(item.feature_community_id, 'layer')" />
                <div v-else class="w-full h-full bg-gray-200 rounded-md flex items-center justify-center text-gray-500">
                  No Image
                </div>
              </div>

              <!-- Name and Description -->
              <div class="flex-1 min-w-0">
                <h3 class="text-lg font-semibold text-gray-800 truncate">{{ item.feature_community_name }}</h3>
                <p class="text-sm text-gray-600 line-clamp-2">{{ item.feature_community_description }}</p>
              </div>

              <!-- Owner -->
              <div class="w-32 flex items-center gap-2">
                <img v-if="getUserImage(item.user_id)" :src="getUserImage(item.user_id)" alt="User image"
                  class="w-10 h-10 rounded-full object-cover" @error="handleImageError(item.user_id, 'user')" />
                <div v-else
                  class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 text-xs">
                  No Img
                </div>
                <span class="text-sm text-gray-700 truncate">{{ getUserName(item.user_id) }}</span>
              </div>

              <!-- Created At -->
              <div class="w-32 text-sm text-gray-600">
                {{ formatDate(item.created_at) }}
              </div>

              <!-- Actions -->
              <div class="flex gap-2">
                <button v-tooltip.bottom="'Review'" class="p-2 bg-sky-400 text-white rounded-full cursor-pointer hover:bg-sky-500 transition-colors"
                  @click="changeFeature(item.feature_id)">
                  <View class="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="h-full w-full flex items-center justify-center text-center">
          <p class="text-gray-500 text-lg">
            No layers have been uploaded to the community yet.
          </p>
        </div>
      </TabsContent>

      <!-- Tab Content: Your friends share with you -->
      <TabsContent value="friends" class="mt-3">
        <section>
          <h2 class="text-lg font-semibold text-muted-foreground mt-2">Layers</h2>
          <div class="flex-1 flex items-center justify-center text-center"
            v-if="!filteredSortedLayerCommunities.length">
            <p class="text-gray-500 text-lg">
              No layers have been shared to you yet.
            </p>
          </div>
          <div class="flex-1" v-else>
            <div v-if="viewMode == 'grid'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card v-for="item in filteredSortedLayerCommunities" :key="item.layer_community_id"
                class="transition-transform duration-200 ease-in-out gap-2 transform mt-2 hover:scale-105 hover:shadow-lg h-80">
                <CardHeader>
                  <CardTitle class="text-lg font-semibold truncate">{{ item.layer_community_name }}</CardTitle>
                </CardHeader>
                <CardContent class="flex flex-col gap-2">
                  <p class="text-sm text-gray-600 truncate">{{ item.layer_community_description || 'No description' }}
                  </p>
                  <img v-if="item.layer_community_image" :src="formatImageSrc(item.layer_community_image)"
                    alt="Layer image" class="h-40 w-full rounded"
                    @error="handleImageError(item.layer_community_id, 'layer')" />
                </CardContent>
                <CardFooter class="flex justify-end gap-2">
                  <Button v-tooltip.bottom="'Review'" class="bg-sky-400 text-white hover:bg-sky-500 cursor-pointer" size="icon"
                    @click="changeLayer(item.layer_id)">
                    <View class="w-4 h-4" />
                  </Button>
                </CardFooter>
              </Card>
            </div>
            <div v-else class="w-full h-full">
              <div class="py-2 px-6">
                <!-- Header Row -->
                <div class="flex items-center border-b">
                  <div class="flex-shrink-0 w-20 h-10 flex items-center justify-center text-gray-600">Image</div>
                  <div v-tooltip="'Sort by name'" class="flex-1 min-w-0 flex items-center gap-1 cursor-pointer hover:bg-gray-200 px-4 py-2 rounded"
                    @click="toggleSort('name')">
                    <span class="text-gray-700 font-normal">Name</span>
                    <span :class="{ 'rotate-180': sortDirection.name == 'desc' }"
                      class="transition-transform duration-200">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </span>
                  </div>
                  <div class="w-32 flex items-center justify-center text-gray-600">Owner</div>
                  <div v-tooltip="'Sort by date'" class="w-33 flex items-center gap-1 cursor-pointer hover:bg-gray-200 px-2 py-2 rounded"
                    @click="toggleSort('date')">
                    <span class="text-gray-700 font-normal">Created Date</span>
                    <span :class="{ 'rotate-180': sortDirection.date == 'desc' }"
                      class="transition-transform duration-200">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </span>
                  </div>
                  <div class="w-16"></div>
                </div>
              </div>
              <div v-for="item in filteredSortedLayerCommunities" :key="item.layer_community_id"
                class="transition-transform py-4 px-6 w-full bg-white rounded-lg mb-4 flex items-center gap-4 hover:scale-[1.02] hover:shadow-md duration-200 ease-in-out">
                <!-- Image -->
                <div class="flex-shrink-0 w-20 h-20">
                  <img v-if="item.layer_community_image" :src="formatImageSrc(item.layer_community_image)"
                    alt="Layer image" class="w-full h-full object-cover rounded-md shadow-md"
                    @error="handleImageError(item.layer_community_id, 'layer')" />
                  <div v-else
                    class="w-full h-full bg-gray-200 rounded-md flex items-center justify-center text-gray-500">
                    No Image
                  </div>
                </div>

                <!-- Name and Description -->
                <div class="flex-1 min-w-0">
                  <h3 class="text-lg font-semibold text-gray-800 truncate">{{ item.layer_community_name }}</h3>
                  <p class="text-sm text-gray-600 line-clamp-2">{{ item.layer_community_description }}</p>
                </div>

                <!-- Owner -->
                <div class="w-32 flex items-center gap-2">
                  <img v-if="getUserImage(item.user_id)" :src="getUserImage(item.user_id)" alt="User image"
                    class="w-10 h-10 rounded-full object-cover" @error="handleImageError(item.user_id, 'user')" />
                  <div v-else
                    class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 text-xs">
                    No Img
                  </div>
                  <span class="text-sm text-gray-700 truncate">{{ getUserName(item.user_id) }}</span>
                </div>

                <!-- Created At -->
                <div class="w-32 text-sm text-gray-600">
                  {{ formatDate(item.created_at) }}
                </div>

                <!-- Actions -->
                <div class="flex gap-2">

                  <button v-tooltip.bottom="'Review'"
                    class="p-2 bg-sky-400 text-white rounded-full cursor-pointer hover:bg-sky-500 transition-colors"
                    @click="changeLayer(item.layer_id)">
                    <View class="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
        <Separator class="mt-4 mb-2" />
        <section>
          <h2 class="text-lg font-semibold text-muted-foreground mt-4">Features</h2>
          <div class="flex-1 flex items-center justify-center text-center"
            v-if="!filteredSortedFeatureCommunities.length">
            <p class="text-gray-500 text-lg">
              No features have been shared to you yet.
            </p>
          </div>
          <div class="h-full w-full" v-else>
            <div v-if="viewMode == 'grid'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-2">
              <Card v-for="item in filteredSortedFeatureCommunities" :key="item.feature_community_id"
                class="transition-transform duration-200 ease-in-out gap-2 transform hover:scale-105 hover:shadow-lg h-80">
                <CardHeader>
                  <CardTitle class="text-lg font-semibold truncate">{{ item.feature_community_name }}</CardTitle>
                </CardHeader>
                <CardContent class="flex flex-col gap-2">
                  <p class="text-sm text-gray-600 truncate">{{ item.feature_community_description || 'No description' }}
                  </p>
                  <img v-if="item.feature_community_image" :src="formatImageSrc(item.feature_community_image)"
                    alt="Feature image" class="h-40 w-full rounded"
                    @error="handleImageError(item.feature_community_id, 'feature')" />
                </CardContent>
                <CardFooter class="flex justify-end gap-2">
                  <Button v-tooltip.bottom="'Review'" class="bg-sky-400 text-white hover:bg-sky-500 cursor-pointer" size="icon"
                    @click="changeFeature(item.feature_id)">
                    <View class="w-4 h-4" />
                  </Button>
                </CardFooter>
              </Card>
            </div>
            <div v-else class="w-full h-full">
              <div class="py-2 px-6">
                <!-- Header Row -->
                <div class="flex items-center border-b">
                  <div class="flex-shrink-0 w-20 h-10 flex items-center justify-center text-gray-600">Image</div>
                  <div v-tooltip="'Sort by name'" class="flex-1 min-w-0 flex items-center gap-1 cursor-pointer hover:bg-gray-200 px-4 py-2 rounded"
                    @click="toggleFeatureSort('name')">
                    <span class="text-gray-700 font-normal">Name</span>
                    <span :class="{ 'rotate-180': sortDirection.name == 'desc' }"
                      class="transition-transform duration-200">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </span>
                  </div>
                  <div class="w-32 flex items-center justify-center text-gray-600">Owner</div>
                  <div v-tooltip="'Sort by date'" class="w-33 flex items-center gap-1 cursor-pointer hover:bg-gray-200 px-2 py-2 rounded"
                    @click="toggleFeatureSort('date')">
                    <span class="text-gray-700 font-normal">Created Date</span>
                    <span :class="{ 'rotate-180': sortDirection.date == 'desc' }"
                      class="transition-transform duration-200">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </span>
                  </div>
                  <div class="w-16"></div>
                </div>
              </div>
              <div v-for="item in filteredSortedFeatureCommunities" :key="item.feature_community_id"
                class="transition-transform py-4 px-6 w-full bg-white rounded-lg mb-4 flex items-center gap-4 hover:scale-[1.02] hover:shadow-md duration-200 ease-in-out">
                <!-- Image -->
                <div class="flex-shrink-0 w-20 h-20">
                  <img v-if="item.feature_community_image" :src="formatImageSrc(item.feature_community_image)"
                    alt="Feature image" class="w-full h-full object-cover rounded-md shadow-md"
                    @error="handleImageError(item.feature_community_id, 'layer')" />
                  <div v-else
                    class="w-full h-full bg-gray-200 rounded-md flex items-center justify-center text-gray-500">
                    No Image
                  </div>
                </div>

                <!-- Name and Description -->
                <div class="flex-1 min-w-0">
                  <h3 class="text-lg font-semibold text-gray-800 truncate">{{ item.feature_community_name }}</h3>
                  <p class="text-sm text-gray-600 line-clamp-2">{{ item.feature_community_description }}</p>
                </div>

                <!-- Owner -->
                <div class="w-32 flex items-center gap-2">
                  <img v-if="getUserImage(item.user_id)" :src="getUserImage(item.user_id)" alt="User image"
                    class="w-10 h-10 rounded-full object-cover" @error="handleImageError(item.user_id, 'user')" />
                  <div v-else
                    class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 text-xs">
                    No Img
                  </div>
                  <span class="text-sm text-gray-700 truncate">{{ getUserName(item.user_id) }}</span>
                </div>

                <!-- Created At -->
                <div class="w-32 text-sm text-gray-600">
                  {{ formatDate(item.created_at) }}
                </div>

                <!-- Actions -->
                <div class="flex gap-2">
                  <button v-tooltip.bottom="'Review'"
                    class="p-2 bg-sky-400 text-white rounded-full cursor-pointer hover:bg-sky-500 transition-colors"
                    @click="changeFeature(item.feature_id)">
                    <View class="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </TabsContent>
      <TabsContent value="user" class="mt-3">
        <section>
          <h2 class="text-lg font-semibold text-muted-foreground mt-2">Your Layers Community</h2>
          <div class="flex-1 flex items-center justify-center text-center" v-if="!sortedUserLayerCommunities.length">
            <p class="text-gray-500 text-lg">
              No layers have been shared with others yet.
            </p>
          </div>
          <div class="flex-1" v-else>
            <div v-if="viewMode == 'grid'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <Card v-for="item in sortedUserLayerCommunities" :key="item.layer_community_id"
                class="transition-transform duration-200 ease-in-out gap-2 transform mt-2 hover:scale-105 hover:shadow-lg h-80">
                <CardHeader>
                  <CardTitle class="text-lg font-semibold truncate">{{ item.layer_community_name }}</CardTitle>
                </CardHeader>
                <CardContent class="flex flex-col gap-2">
                  <p class="text-sm text-gray-600 truncate">{{ item.layer_community_description || 'No description' }}
                  </p>
                  <img v-if="item.layer_community_image" :src="formatImageSrc(item.layer_community_image)"
                    alt="Layer image" class="h-40 w-full rounded"
                    @error="handleImageError(item.layer_community_id, 'layer')" />
                </CardContent>
                <CardFooter class="flex justify-end gap-2">
                  <Button v-tooltip.bottom="'Review'" class="bg-sky-400 text-white hover:bg-sky-500 cursor-pointer" size="icon"
                    @click="changeLayer(item.layer_id)">
                    <View class="w-4 h-4" />
                  </Button>
                  <Button v-tooltip.bottom="'Edit'" class="bg-lime-400 text-white hover:bg-lime-500 cursor-pointer" size="icon"
                    @click="openEditLayerDialog(item)">
                    <Pencil class="w-4 h-4" />
                  </Button>
                  <Button v-tooltip.bottom="'Delete'" class="bg-red-400 text-white hover:bg-red-500 cursor-pointer" size="icon"
                    @click="deleteLayerCommunity(item.layer_community_id)">
                    <Trash2 class="w-4 h-4" />
                  </Button>
                </CardFooter>
              </Card>
            </div>
            <div v-else class="w-full h-full">
              <div class="py-2 px-6">
                <!-- Header Row -->
                <div class="flex items-center border-b">
                  <div class="flex-shrink-0 w-20 h-10 flex items-center justify-center text-gray-600">Image</div>
                  <div v-tooltip="'Sort by name'" class="flex-1 min-w-0 flex items-center gap-1 cursor-pointer hover:bg-gray-200 px-4 py-2 rounded"
                    @click="toggleSort('name')">
                    <span class="text-gray-700 font-normal">Name</span>
                    <span :class="{ 'rotate-180': sortDirection.name == 'desc' }"
                      class="transition-transform duration-200">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </span>
                  </div>
                  <div class="w-32 flex items-center justify-center text-gray-600">Owner</div>
                  <div v-tooltip="'Sort by date'" class="w-33 flex items-center gap-1 cursor-pointer hover:bg-gray-200 px-2 py-2 rounded"
                    @click="toggleSort('date')">
                    <span class="text-gray-700 font-normal">Created Date</span>
                    <span :class="{ 'rotate-180': sortDirection.date == 'desc' }"
                      class="transition-transform duration-200">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </span>
                  </div>
                  <div class="w-16"></div>
                </div>
              </div>
              <div v-for="item in sortedUserLayerCommunities" :key="item.layer_community_id"
                class="transition-transform py-4 px-6 w-full bg-white rounded-lg mb-4 flex items-center gap-4 hover:scale-[1.02] hover:shadow-md duration-200 ease-in-out">
                <!-- Image -->
                <div class="flex-shrink-0 w-20 h-20">
                  <img v-if="item.layer_community_image" :src="formatImageSrc(item.layer_community_image)"
                    alt="Layer image" class="w-full h-full object-cover rounded-md shadow-md"
                    @error="handleImageError(item.layer_community_id, 'layer')" />
                  <div v-else
                    class="w-full h-full bg-gray-200 rounded-md flex items-center justify-center text-gray-500">
                    No Image
                  </div>
                </div>

                <!-- Name and Description -->
                <div class="flex-1 min-w-0">
                  <h3 class="text-lg font-semibold text-gray-800 truncate">{{ item.layer_community_name }}</h3>
                  <p class="text-sm text-gray-600 line-clamp-2">{{ item.layer_community_description }}</p>
                </div>

                <!-- Owner -->
                <div class="w-32 flex items-center gap-2">
                  <img v-if="getUserImage(item.user_id)" :src="getUserImage(item.user_id)" alt="User image"
                    class="w-10 h-10 rounded-full object-cover" @error="handleImageError(item.user_id, 'user')" />
                  <div v-else
                    class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 text-xs">
                    No Img
                  </div>
                  <span class="text-sm text-gray-700 truncate">{{ getUserName(item.user_id) }}</span>
                </div>

                <!-- Created At -->
                <div class="w-32 text-sm text-gray-600">
                  {{ formatDate(item.created_at) }}
                </div>

                <!-- Actions -->
                <div class="flex gap-2">

                  <button v-tooltip.bottom="'Review'"
                    class="p-2 bg-sky-400 text-white rounded-full cursor-pointer hover:bg-sky-500 transition-colors"
                    @click="changeLayer(item.layer_id)">
                    <View class="h-4 w-4" />
                  </button>
                  <button v-tooltip.bottom="'Edit'"
                    class="p-2 bg-lime-400 text-white rounded-full cursor-pointer hover:bg-lime-500 transition-colors"
                    @click="openEditLayerDialog(item)">
                    <Pencil class="h-4 w-4" />
                  </button>
                  <button v-tooltip.bottom="'Delete'"
                    class="p-2 bg-red-400 text-white rounded-full cursor-pointer hover:bg-red-500 transition-colors"
                    @click="deleteLayerCommunity(item.layer_community_id)">
                    <Trash2 class="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
        <Separator class="mt-4 mb-2" />
        <section>
          <h2 class="text-lg font-semibold text-muted-foreground mt-4">Your Features Community</h2>
          <div class="flex-1 flex items-center justify-center text-center" v-if="!sortedUserFeatureCommunities.length">
            <p class="text-gray-500 text-lg">
              No features have been shared with others yet.
            </p>
          </div>
          <div class="h-full w-full" v-else>
            <div v-if="viewMode == 'grid'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-2">
              <Card v-for="item in sortedUserFeatureCommunities" :key="item.feature_community_id"
                class="transition-transform duration-200 ease-in-out gap-2 transform hover:scale-105 hover:shadow-lg h-80">
                <CardHeader>
                  <CardTitle class="text-lg font-semibold truncate">{{ item.feature_community_name }}</CardTitle>
                </CardHeader>
                <CardContent class="flex flex-col gap-2">
                  <p class="text-sm text-gray-600 truncate">{{ item.feature_community_description || 'No description' }}
                  </p>
                  <img v-if="item.feature_community_image" :src="formatImageSrc(item.feature_community_image)"
                    alt="Feature image" class="h-40 w-full rounded"
                    @error="handleImageError(item.feature_community_id, 'feature')" />
                </CardContent>
                <CardFooter class="flex justify-end gap-2">
                  <Button v-tooltip.bottom="'Review'" class="bg-sky-400 text-white hover:bg-sky-500 cursor-pointer" size="icon"
                    @click="changeFeature(item.feature_id)">
                    <View class="w-4 h-4" />
                  </Button>
                  <Button v-tooltip.bottom="'Edit'" class="bg-lime-400 text-white hover:bg-lime-500 cursor-pointer" size="icon"
                    @click="openEditFeatureDialog(item)">
                    <Pencil class="w-4 h-4" />
                  </Button>
                  <Button v-tooltip.bottom="'Delete'" class="bg-red-400 text-white hover:bg-red-500 cursor-pointer" size="icon"
                    @click="deleteFeatureCommunity(item.feature_community_id)">
                    <Trash2 class="w-4 h-4" />
                  </Button>
                </CardFooter>
              </Card>
            </div>
            <div v-else class="w-full h-full">
              <div class="py-2 px-6">
                <!-- Header Row -->
                <div class="flex items-center border-b">
                  <div class="flex-shrink-0 w-20 h-10 flex items-center justify-center text-gray-600">Image</div>
                  <div v-tooltip="'Sort by name'" class="flex-1 min-w-0 flex items-center gap-1 cursor-pointer hover:bg-gray-200 px-4 py-2 rounded"
                    @click="toggleFeatureSort('name')">
                    <span class="text-gray-700 font-normal">Name</span>
                    <span :class="{ 'rotate-180': sortDirection.name == 'desc' }"
                      class="transition-transform duration-200">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </span>
                  </div>
                  <div class="w-32 flex items-center justify-center text-gray-600">Owner</div>
                  <div v-tooltip="'Sort by date'" class="w-33 flex items-center gap-1 cursor-pointer hover:bg-gray-200 px-2 py-2 rounded"
                    @click="toggleFeatureSort('date')">
                    <span class="text-gray-700 font-normal">Created Date</span>
                    <span :class="{ 'rotate-180': sortDirection.date == 'desc' }"
                      class="transition-transform duration-200">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                      </svg>
                    </span>
                  </div>
                  <div class="w-16"></div>
                </div>
              </div>
              <div v-for="item in sortedUserFeatureCommunities" :key="item.feature_community_id"
                class="transition-transform py-4 px-6 w-full bg-white rounded-lg mb-4 flex items-center gap-4 hover:scale-[1.02] hover:shadow-md duration-200 ease-in-out">
                <!-- Image -->
                <div class="flex-shrink-0 w-20 h-20">
                  <img v-if="item.feature_community_image" :src="formatImageSrc(item.feature_community_image)"
                    alt="Feature image" class="w-full h-full object-cover rounded-md shadow-md"
                    @error="handleImageError(item.feature_community_id, 'layer')" />
                  <div v-else
                    class="w-full h-full bg-gray-200 rounded-md flex items-center justify-center text-gray-500">
                    No Image
                  </div>
                </div>

                <!-- Name and Description -->
                <div class="flex-1 min-w-0">
                  <h3 class="text-lg font-semibold text-gray-800 truncate">{{ item.feature_community_name }}</h3>
                  <p class="text-sm text-gray-600 line-clamp-2">{{ item.feature_community_description }}</p>
                </div>

                <!-- Owner -->
                <div class="w-32 flex items-center gap-2">
                  <img v-if="getUserImage(item.user_id)" :src="getUserImage(item.user_id)" alt="User image"
                    class="w-10 h-10 rounded-full object-cover" @error="handleImageError(item.user_id, 'user')" />
                  <div v-else
                    class="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 text-xs">
                    No Img
                  </div>
                  <span class="text-sm text-gray-700 truncate">{{ getUserName(item.user_id) }}</span>
                </div>

                <!-- Created At -->
                <div class="w-32 text-sm text-gray-600">
                  {{ formatDate(item.created_at) }}
                </div>

                <!-- Actions -->
                <div class="flex gap-2">
                  <button v-tooltip.bottom="'Review'"
                    class="p-2 bg-sky-400 text-white rounded-full cursor-pointer hover:bg-sky-500 transition-colors"
                    @click="changeFeature(item.feature_id)">
                    <View class="h-4 w-4" />
                  </button>
                  <button v-tooltip.bottom="'Edit'"
                    class="p-2 bg-lime-400 text-white rounded-full cursor-pointer hover:bg-lime-500 transition-colors"
                    @click="openEditFeatureDialog(item)">
                    <Pencil class="h-4 w-4" />
                  </button>
                  <button v-tooltip.bottom="'Delete'"
                    class="p-2 bg-red-400 text-white rounded-full cursor-pointer hover:bg-red-500 transition-colors"
                    @click="deleteFeatureCommunity(item.feature_community_id)">
                    <Trash2 class="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>
      </TabsContent>
    </Tabs>
  </div>
  <ReviewVectorLayer v-if="isOpen" :openDialog="isOpen" :layer_id="selectedLayerId"
    @update:openDialog="isOpen = $event"></ReviewVectorLayer>
  <ReviewFeature v-if="isFeatureOpen" :openDialog="isFeatureOpen" :feature_id="selectedFeatureId"
    @update:openFeatureDialog="isFeatureOpen = $event"></ReviewFeature>
  <!-- Edit Layer Community Dialog -->
  <AlertDialog v-model:open="isEditLayerDialogOpen">
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>Edit Layer Community</AlertDialogTitle>
        <AlertDialogDescription>
          Update the details of your layer community below.
        </AlertDialogDescription>
      </AlertDialogHeader>
      <div class="grid gap-4 py-4">
        <div class="grid grid-cols-4 items-center gap-4">
          <Label for="layer-name" class="text-right">Name</Label>
          <Input id="layer-name" v-model="editLayerForm.layer_community_name" class="col-span-3" />
        </div>
        <div class="grid grid-cols-4 items-center gap-4">
          <Label for="layer-description" class="text-right">Description</Label>
          <Textarea id="layer-description" v-model="editLayerForm.layer_community_description" class="col-span-3" />
        </div>
        <div class="grid grid-cols-4 items-center gap-4">
          <Label for="layer-image" class="text-right">Image</Label>
          <div class="col-span-3">
            <Input id="layer-image" type="file" accept="image/*" @change="handleLayerImageUpload" />
            <img v-if="editLayerForm.layer_community_image" :src="formatImageSrc(editLayerForm.layer_community_image)"
              alt="Preview" class="mt-2 h-20 w-20 object-cover rounded" />
          </div>
        </div>
        <div class="grid grid-cols-4 items-center gap-4">
          <Label for="layer-access_rights" class="text-right">Access Rights</Label>
          <Select v-model="editLayerForm.access_rights" class="col-span-3">
            <SelectTrigger>
              <SelectValue placeholder="Select access rights" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Public">Public</SelectItem>
              <SelectItem value="Restricted">Restricted</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div v-if="editLayerForm.access_rights == 'Restricted'" class="grid grid-cols-4 items-center gap-4">
          <Label for="layer-tags" class="text-right">Access Tags</Label>
          <TagsInput v-model="editLayerForm.tags" class="col-span-3">
            <TagsInputItem v-for="item in editLayerForm.tags" :key="item" :value="item">
              <TagsInputItemText />
              <TagsInputItemDelete />
            </TagsInputItem>
            <TagsInputInput placeholder="Enter your friend's username or email..." />
          </TagsInput>
        </div>
      </div>
      <AlertDialogFooter>
        <AlertDialogCancel @click="isEditLayerDialogOpen = false">Cancel</AlertDialogCancel>
        <AlertDialogAction @click="submitLayerEditForm">Save</AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>

  <!-- Edit Feature Community Dialog -->
  <AlertDialog v-model:open="isEditFeatureDialogOpen">
    <AlertDialogContent>
      <AlertDialogHeader>
        <AlertDialogTitle>Edit Feature Community</AlertDialogTitle>
        <AlertDialogDescription>
          Update the details of your feature community below.
        </AlertDialogDescription>
      </AlertDialogHeader>
      <div class="grid gap-4 py-4">
        <div class="grid grid-cols-4 items-center gap-4">
          <Label for="feature-name" class="text-right">Name</Label>
          <Input id="feature-name" v-model="editFeatureForm.feature_community_name" class="col-span-3" />
        </div>
        <div class="grid grid-cols-4 items-center gap-4">
          <Label for="feature-description" class="text-right">Description</Label>
          <Textarea id="feature-description" v-model="editFeatureForm.feature_community_description"
            class="col-span-3" />
        </div>
        <div class="grid grid-cols-4 items-center gap-4">
          <Label for="feature-image" class="text-right">Image</Label>
          <div class="col-span-3">
            <Input id="feature-image" type="file" accept="image/*" @change="handleFeatureImageUpload" />
            <img v-if="editFeatureForm.feature_community_image"
              :src="formatImageSrc(editFeatureForm.feature_community_image)" alt="Preview"
              class="mt-2 h-20 w-20 object-cover rounded" />
          </div>
        </div>
        <div class="grid grid-cols-4 items-center gap-4">
          <Label for="feature-access_rights" class="text-right">Access Rights</Label>
          <Select v-model="editFeatureForm.access_rights" class="col-span-3">
            <SelectTrigger>
              <SelectValue placeholder="Select access rights" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="Public">Public</SelectItem>
              <SelectItem value="Restricted">Restricted</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div v-if="editFeatureForm.access_rights == 'Restricted'" class="grid grid-cols-4 items-center gap-4">
          <Label for="layer-tags" class="text-right">Access Tags</Label>
          <TagsInput v-model="editFeatureForm.tags" class="col-span-3">
            <TagsInputItem v-for="item in editFeatureForm.tags" :key="item" :value="item">
              <TagsInputItemText />
              <TagsInputItemDelete />
            </TagsInputItem>
            <TagsInputInput placeholder="Enter your friend's username or email..." />
          </TagsInput>
        </div>
      </div>
      <AlertDialogFooter>
        <AlertDialogCancel @click="isEditFeatureDialogOpen = false">Cancel</AlertDialogCancel>
        <AlertDialogAction @click="submitFeatureEditForm">Save</AlertDialogAction>
      </AlertDialogFooter>
    </AlertDialogContent>
  </AlertDialog>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'
import { AlertDialog, AlertDialogContent, AlertDialogHeader, AlertDialogTitle, AlertDialogDescription, AlertDialogFooter, AlertDialogCancel, AlertDialogAction } from '@/components/ui/alert-dialog'
import Separator from './ui/separator/Separator.vue'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select'
import { TagsInput, TagsInputItem, TagsInputItemText, TagsInputItemDelete, TagsInputInput } from '@/components/ui/tags-input'
import { Button } from '@/components/ui/button'
import { Pencil, Trash2, View } from 'lucide-vue-next'
import axios from 'axios'
import { LayoutGrid as GridIcon, List as ListIcon } from 'lucide-vue-next'
import ReviewVectorLayer from './ReviewMap/ReviewVectorLayer.vue'
import ReviewFeature from './ReviewMap/ReviewFeature.vue'
import Swal from 'sweetalert2'
const activeTab = ref('layer')
const viewMode = ref<'grid' | 'list'>('list')
const layerCommunities = ref<any[]>([])
const users = ref([]);
const sortDirection = ref({ name: 'asc', date: 'desc' });
const sortFeatureDirection = ref({ name: 'asc', date: 'desc'})
const featureCommunities = ref<any[]>([])
const selectedLayerId = ref(1)
const isOpen = ref(false);
const selectedFeatureId = ref(1)
const isFeatureOpen = ref(false);
const friendSharedData = ref({});
const user_layer_data = ref([]);
const user_feature_data = ref([]);
const isEditLayerDialogOpen = ref(false)
const editLayerForm = ref({
  layer_community_id: null,
  layer_community_name: '',
  layer_community_description: '',
  access_rights: '',
  layer_community_image: '',
  tags: []
})
const isEditFeatureDialogOpen = ref(false)
const editFeatureForm = ref({
  feature_community_id: null,
  feature_community_name: '',
  feature_community_description: '',
  access_rights: '',
  feature_community_image: '',
  tags: []
})
const formatImageSrc = (base64String) => {
  return `data:image/jpeg;base64,${base64String}`;
};

const getUserImage = (userId) => {
  const user = users.value.find(u => u.user_id == userId);
  if (user?.user_image) {
    return `data:image/jpeg;base64,${user.user_image}`;
  }
  return user?.avatar || null;
};

const getUserName = (userId) => {
  const user = users.value.find(u => u.user_id == userId);
  return user?.username || user?.email || 'Unknown';
};

const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('vi-VN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

const handleImageError = (id, type) => {
  console.error(`Error loading ${type} image for ID: ${id}`);
};
const changeLayer = (newId) => {
  selectedLayerId.value = newId;
  isOpen.value = true; // Mở Dialog khi thay đổi layer
};
const changeFeature = (newId) => {
  selectedFeatureId.value = newId;
  isFeatureOpen.value = true; // Mở Dialog khi thay đổi layer
};
onMounted(async () => {
  try {
    const token = localStorage.getItem('access_token');
    // Fetch all users
    const user_profile_response = await axios.get('http://localhost:8000/user/all', {
      headers: { Authorization: `Bearer ${token}` },
    });
    users.value = user_profile_response.data;

    // Fetch layer_community
    const layerResponse = await axios.get('http://localhost:8000/layer_community', {
      headers: { Authorization: `Bearer ${token}` },
    });
    layerCommunities.value = layerResponse.data.map(item => ({
      ...item,
      layer_community_image: item.layer_community_image || null,
    }));
    console.log(layerCommunities.value)
    // Fetch feature_community
    const featureResponse = await axios.get('http://localhost:8000/feature_community', {
      headers: { Authorization: `Bearer ${token}` },
    });
    featureCommunities.value = featureResponse.data.map(item => ({
      ...item,
      feature_community_image: item.feature_community_image || null,
    }));
    console.log("Feature:", featureCommunities.value)
    const friendShareResponse = await axios.get('http://localhost:8000/community_access_control/get-access-controls',{
      headers: { Authorization: `Bearer ${token}` },
    });
    console.log(friendShareResponse.data)
    friendSharedData.value = friendShareResponse.data
    const userLayerResponse = await axios.get('http://localhost:8000/layer_community/by-user',{
      headers: { Authorization: `Bearer ${token}` },
    });
    user_layer_data.value = userLayerResponse.data
    const userFeatureDataResponse = await axios.get('http://localhost:8000/feature_community/by-user',{
      headers: { Authorization: `Bearer ${token}` },
    });
    user_feature_data.value = userFeatureDataResponse.data

  } catch (error) {
    console.error('Error fetching community data:', error);
  }
});
const sortedLayerCommunities = computed(() => {
  return [...layerCommunities.value].sort((a, b) => {
    if (sortDirection.value.name != null) {
      const nameA = a.layer_community_name || '';
      const nameB = b.layer_community_name || '';
      return sortDirection.value.name == 'asc'
        ? nameA.localeCompare(nameB)
        : nameB.localeCompare(nameA);
    }
    if (sortDirection.value.date != null) {
      return sortDirection.value.date == 'desc'
        ? new Date(b.created_at) - new Date(a.created_at)
        : new Date(a.created_at) - new Date(b.created_at);
    }
    return 0;
  });
});
const sortedFeatureCommunities = computed(() => {
  return [...featureCommunities.value].sort((a, b) => {
    if (sortFeatureDirection.value.name != null) {
      const nameA = a.feature_community_name || '';
      const nameB = b.feature_community_name || '';
      return sortFeatureDirection.value.name == 'asc'
        ? nameA.localeCompare(nameB)
        : nameB.localeCompare(nameA);
    }
    if (sortFeatureDirection.value.date != null) {
      return sortFeatureDirection.value.date == 'desc'
        ? new Date(b.created_at) - new Date(a.created_at)
        : new Date(a.created_at) - new Date(b.created_at);
    }
    return 0;
  });
});
// Biến computed để lọc và sắp xếp layerCommunities
const filteredSortedLayerCommunities = computed(() => {

  return friendSharedData.value.list_layer_id.sort((a, b) => {
    if (sortDirection.value.name != null) {
      const nameA = a.layer_community_name || '';
      const nameB = b.layer_community_name || '';
      return sortDirection.value.name == 'asc'
        ? nameA.localeCompare(nameB)
        : nameB.localeCompare(nameA);
    }
    if (sortDirection.value.date != null) {
      return sortDirection.value.date == 'desc'
        ? new Date(b.created_at) - new Date(a.created_at)
        : new Date(a.created_at) - new Date(b.created_at);
    }
    return 0;
  });
});

// Biến computed để lọc và sắp xếp featureCommunities
const filteredSortedFeatureCommunities = computed(() => {
  return friendSharedData.value.list_feature_id.sort((a, b) => {
    console.log(friendSharedData.value.list_feature_id)
    if (sortFeatureDirection.value.name != null) {
      const nameA = a.feature_community_name || '';
      const nameB = b.feature_community_name || '';
      return sortFeatureDirection.value.name == 'asc'
        ? nameA.localeCompare(nameB)
        : nameB.localeCompare(nameA);
    }
    if (sortFeatureDirection.value.date != null) {
      return sortFeatureDirection.value.date == 'desc'
        ? new Date(b.created_at) - new Date(a.created_at)
        : new Date(a.created_at) - new Date(b.created_at);
    }
    return 0;
  });
});

const sortedUserLayerCommunities = computed(() => {
  return [...user_layer_data.value].sort((a, b) => {
    if (sortDirection.value.name != null) {
      const nameA = a.layer_community_name || '';
      const nameB = b.layer_community_name || '';
      return sortDirection.value.name == 'asc'
        ? nameA.localeCompare(nameB)
        : nameB.localeCompare(nameA);
    }
    if (sortDirection.value.date != null) {
      return sortDirection.value.date == 'desc'
        ? new Date(b.created_at) - new Date(a.created_at)
        : new Date(a.created_at) - new Date(b.created_at);
    }
    return 0;
  });
});
const sortedUserFeatureCommunities = computed(() => {
  return [...user_feature_data.value].sort((a, b) => {
    if (sortFeatureDirection.value.name != null) {
      const nameA = a.feature_community_name || '';
      const nameB = b.feature_community_name || '';
      return sortFeatureDirection.value.name == 'asc'
        ? nameA.localeCompare(nameB)
        : nameB.localeCompare(nameA);
    }
    if (sortFeatureDirection.value.date != null) {
      return sortFeatureDirection.value.date == 'desc'
        ? new Date(b.created_at) - new Date(a.created_at)
        : new Date(a.created_at) - new Date(b.created_at);
    }
    return 0;
  });
});
const toggleSort = (type) => {
  if (type == 'name') {
    sortDirection.value.name = sortDirection.value.name == 'asc' ? 'desc' : 'asc';
    sortDirection.value.date = null;
  } else if (type == 'date') {
    sortDirection.value.date = sortDirection.value.date == 'desc' ? 'asc' : 'desc';
    sortDirection.value.name = null;
  }
};
const toggleFeatureSort = (type) => {
  if (type == 'name') {
    sortFeatureDirection.value.name = sortFeatureDirection.value.name == 'asc' ? 'desc' : 'asc';
    sortFeatureDirection.value.date = null;
  } else if (type == 'date') {
    sortFeatureDirection.value.date = sortFeatureDirection.value.date == 'desc' ? 'asc' : 'desc';
    sortFeatureDirection.value.name = null;
  }
};
const handleLayerImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      editLayerForm.value.layer_community_image = e.target.result.split(',')[1]
    }
    reader.readAsDataURL(file)
  }
}

const handleFeatureImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      editFeatureForm.value.feature_community_image = e.target.result.split(',')[1]
    }
    reader.readAsDataURL(file)
  }
}

const openEditLayerDialog = async (item) => {
  editLayerForm.value = {
    layer_community_id: item.layer_community_id,
    layer_community_name: item.layer_community_name,
    layer_community_description: item.layer_community_description || '',
    access_rights: item.access_rights,
    layer_community_image: item.layer_community_image || '',
    tags: []
  }
  if (item.access_rights == 'Restricted') {
    try {
      const token = localStorage.getItem('access_token')
      const response = await axios.get(`http://localhost:8000/community_access_control/layer_community/${item.layer_community_id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      editLayerForm.value.tags = response.data
      console.log(editLayerForm.value.tags)
    } catch (error) {
      console.error('Error fetching layer access rights:', error)
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Failed to load access rights'
      })
    }
  }
  isEditLayerDialogOpen.value = true
}

const openEditFeatureDialog = async (item) => {
  editFeatureForm.value = {
    feature_community_id: item.feature_community_id,
    feature_community_name: item.feature_community_name,
    feature_community_description: item.feature_community_description || '',
    access_rights: item.access_rights,
    feature_community_image: item.feature_community_image || '',
    tags: []
  }
  if (item.access_rights == 'Restricted') {
    try {
      const token = localStorage.getItem('access_token')
      const response = await axios.get(`http://localhost:8000/community_access_control/feature_community/${item.feature_community_id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      editFeatureForm.value.tags = response.data
      console.log(response.data)
    } catch (error) {
      console.error('Error fetching feature access rights:', error)
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Failed to load access rights'
      })
    }
  }
  isEditFeatureDialogOpen.value = true
}

const submitLayerEditForm = async () => {
  try {
    const token = localStorage.getItem('access_token')
    const payload = {
      layer_community_name: editLayerForm.value.layer_community_name,
      layer_community_description: editLayerForm.value.layer_community_description,
      access_rights: editLayerForm.value.access_rights,
      layer_community_image: editLayerForm.value.layer_community_image
    }
    const response = await axios.put(
      `http://localhost:8000/layer_community/${editLayerForm.value.layer_community_id}`,
      payload,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    )
    // Update local data
    const index = user_layer_data.value.findIndex(
      item => item.layer_community_id == editLayerForm.value.layer_community_id
    )
    if (index != -1) {
      user_layer_data.value[index] = response.data
    }
    // Handle tags if access_rights is Restricted
    if (editLayerForm.value.access_rights == 'Restricted' && editLayerForm.value.tags.length > 0) {
      const delete_response = await axios.delete(`http://localhost:8000/community_access_control/delete-by-layer/${editLayerForm.value.layer_community_id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      if(delete_response.status){
        await axios.post(`http://localhost:8000/community_access_control/add-layer-access/`,
          {
            layer_community_id: editLayerForm.value.layer_community_id,
            user_informs: editLayerForm.value.tags
          },
          { headers: { Authorization: `Bearer ${token}` } }
        )
      }
    }
    const layerResponse = await axios.get('http://localhost:8000/layer_community', {
      headers: { Authorization: `Bearer ${token}` },
    });
    layerCommunities.value = layerResponse.data.map(item => ({
      ...item,
      layer_community_image: item.layer_community_image || null,
    }));
    isEditLayerDialogOpen.value = false
    Swal.fire({
      icon: 'success',
      title: 'Success',
      text: 'Layer Community updated successfully!'
    })
  } catch (error) {
    console.error('Error updating layer community:', error)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: error.response?.data?.detail || 'Failed to update Layer Community'
    })
  }
}

const submitFeatureEditForm = async () => {
  try {
    const token = localStorage.getItem('access_token')
    const payload = {
      feature_community_name: editFeatureForm.value.feature_community_name,
      feature_community_description: editFeatureForm.value.feature_community_description,
      access_rights: editFeatureForm.value.access_rights,
      feature_community_image: editFeatureForm.value.feature_community_image
    }
    const response = await axios.put(
      `http://localhost:8000/feature_community/${editFeatureForm.value.feature_community_id}`,
      payload,
      {
        headers: { Authorization: `Bearer ${token}` }
      }
    )
    // Update local data
    const index = user_feature_data.value.findIndex(
      item => item.feature_community_id == editFeatureForm.value.feature_community_id
    )
    if (index != -1) {
      user_feature_data.value[index] = response.data
    }
    // Handle tags if access_rights is Restricted
    if (editFeatureForm.value.access_rights == 'Restricted' && editFeatureForm.value.tags.length > 0) {
      const delete_feature_response = await axios.delete(`http://localhost:8000/community_access_control/delete-by-feature/${editFeatureForm.value.feature_community_id}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      console.log(editFeatureForm.value.tags)
      if(delete_feature_response.status){
        await axios.post(
          `http://localhost:8000/community_access_control/add-feature-access/`,
          {
            feature_community_id: editFeatureForm.value.feature_community_id,
            user_informs: editFeatureForm.value.tags
          },
          { headers: { Authorization: `Bearer ${token}` } }
        )
      }
    }
    const featureResponse = await axios.get('http://localhost:8000/feature_community', {
      headers: { Authorization: `Bearer ${token}` },
    });
    featureCommunities.value = featureResponse.data.map(item => ({
      ...item,
      feature_community_image: item.feature_community_image || null,
    }));
    isEditFeatureDialogOpen.value = false
    Swal.fire({
      icon: 'success',
      title: 'Success',
      text: 'Feature Community updated successfully!'
    })
  } catch (error) {
    console.error('Error updating feature community:', error)
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: error.response?.data?.detail || 'Failed to update Feature Community'
    })
  }
}
const deleteLayerCommunity = async(layer_community_id) => {
  try{
    const deleteLayerResponse = await axios.patch(`http://localhost:8000/layer_community/${layer_community_id}`,{},{
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
    });
    console.log(deleteLayerResponse.data)
    user_layer_data.value = user_layer_data.value.filter( item => item.layer_community_id != layer_community_id)
    Swal.fire({
    icon: 'success',
    title: 'Success',
    text: `Your VectorLayer Community has been moved to Recycle Bin!`,
  })
  }catch(error){
    console.log(error)
  }
}

const deleteFeatureCommunity = async(feature_community_id) => {
    try{
    const deleteFeatureResponse = await axios.patch(`http://localhost:8000/feature_community/${feature_community_id}`,{},{
      headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
    });
    console.log(deleteFeatureResponse.data)
    user_feature_data.value = user_feature_data.value.filter( item => item.feature_community_id != layer_feature_id)
    Swal.fire({
    icon: 'success',
    title: 'Success',
    text: `Your Feature Community has been moved to Recycle Bin!`,
  })
  }catch(error){
    console.log(error)
  }
}
</script>