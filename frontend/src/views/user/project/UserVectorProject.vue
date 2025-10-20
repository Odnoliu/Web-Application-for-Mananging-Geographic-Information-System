<template>
  <Project_Loading v-if="isLoading && map"></Project_Loading>
  <div v-else class="flex h-screen w-screen bg-background text-foreground">
    <div class="relative flex-1">
      <div id="map" ref="mapContainer" class="absolute inset-0 z-10" />
      <!-- Component ControlButtonGroup -->
      <ControlButtonGroup :map="map" class="absolute top-4 left-4 z-20" v-if="map" />

      <!-- Component DrawButtonGroup -->
      <DrawButtonGroup :map="map" :user-data="user_layer" @update:drawing="isDrawing = $event"
        @update:savingFeature="isSaving = $event" v-if="map" class="absolute top-15 right-6 z-20" />
      <ControlBaseButtonGroup :map="map" :layerIds="baseIds" class="absolute top-177 left-4 z-20" v-if="!isLoading" />
    </div>

    <div class="w-[25rem] h-full border-l p-4">
      <Tabs default-value="informs" class="w-full h-full">
        <TabsList class="grid w-full grid-cols-3">
          <TabsTrigger value="informs">
            INFORMS
          </TabsTrigger>
          <TabsTrigger value="vector-layers">
            VECTOR LAYERS
          </TabsTrigger>
          <TabsTrigger value="features">
            FEATURES
          </TabsTrigger>
        </TabsList>
        <TabsContent value="informs" class="mt-4 h-full">
          <div class="mb-2">
            <Label for="title-select" class="text-sm font-medium text-gray-600">Select Title</Label>
            <Select v-model="selectedTitle" id="title-select">
              <SelectTrigger class="w-full">
                <SelectValue placeholder="Select a title" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="All">All</SelectItem>
                <SelectItem v-for="title in uniqueTitles" :key="title" :value="title">
                  {{ title }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <ScrollArea v-if="filteredFeatures.length" class="h-[600px] space-y-6">
            <div class="space-y-4">
              <div v-for="feature in filteredFeatures" :key="feature.feature_id" class="border rounded-lg p-3">
                <div class="text-sm">
                  <strong>Feature Name:</strong> {{ feature.name || 'Unnamed Feature' }}
                </div>
                <div class="text-sm">
                  <strong>Country:</strong> {{ feature.properties?.COUNTRY || 'N/A' }}
                </div>
                <div class="text-sm">
                  <strong>Layer ID:</strong> {{ feature.layer_id || 'N/A' }}
                </div>
              </div>
              <div v-if="!filteredFeatures.length" class="text-sm text-gray-500">
                No features found for the selected title.
              </div>
            </div>
          </ScrollArea>
        </TabsContent>
        <TabsContent value="vector-layers" class="mt-4 h-full">
          <div class="flex mb-4 gap-2 items-center">
            <Combobox by="layer_name" class="flex justify-center flex-1">
              <ComboboxAnchor class="w-full">
                <div class="relative w-full max-w-sm items-center border rounded-md">
                  <ComboboxInput :display-value="(val) => val?.layer_name ?? ''" v-model="searchQuery"
                    placeholder="Find your layer..." />
                  <span class="absolute start-0 inset-y-0 flex items-center justify-center px-3">
                    <Search class="size-4 text-muted-foreground" />
                  </span>
                </div>
              </ComboboxAnchor>
              <ComboboxList>
                <ComboboxEmpty>
                  No layer found.
                </ComboboxEmpty>
                <ComboboxGroup>
                  <ComboboxItem v-for="layer in display_layer" :key="layer.layer_name" :value="layer">
                    {{ layer.layer_name }}
                    <ComboboxItemIndicator>
                      <Check :class="cn('ml-auto h-4 w-4')" />
                    </ComboboxItemIndicator>
                  </ComboboxItem>
                </ComboboxGroup>
              </ComboboxList>
            </Combobox>
            <button v-tooltip.bottom="'Add new Vector Layer'" class="text-white bg-gray-400 cursor-pointer h-9 w-9 flex items-center justify-center rounded-md"
              @click="openAddLayerDialog()">
              <Plus class="w-6 h-6"></Plus>
            </button>
          </div>
          <ScrollArea v-if="displayData" class="h-[635px]">
            <div class="w-full flex justify-end mb-4">
              <Button v-if="isOrderChanged" @click="saveNewOrder" class="bg-green-600 mr-3 cursor-pointer text-white hover:bg-green-700">
                Save Priority Changes
              </Button>
            </div>

            <section>
              <h2 class="text-xl font-semibold text-gray-700 mb-3 border-b pb-2">Default Layers</h2>
              <draggable v-if="draggableDefaultLayers?.length" v-model="draggableDefaultLayers"
                item-key="default_layer_id" @end="onDragEndDefault" class="space-y-3" tag="div">
                <template #item="{ element: layer }">
                  <Card
                    class="w-full h-40 shadow-md gap-2 transition relative duration-200 ease-in-out transform hover:scale-95 hover:shadow-lg pt-2 cursor-move">
                    <div class="absolute top-2 right-2" v-if="layer.default_layer_id == 7">
                      <button v-tooltip.left="'Change version'" class="cursor-pointer text-gray-600 hover:text-blue-600 focus:outline-none"
                        @click="changeVersion(7)">
                        <Merge class="w-5 h-5" />
                      </button>
                    </div>
                    <CardHeader class="h-[54px] px-2 flex justify-center">
                      <CardTitle class="text-base text-center flex items-center font-semibold h-[54px]">{{
                        layer.layer_name }}</CardTitle>
                    </CardHeader>
                    <CardContent class="flex gap-2 items-center px-2 justify-center">
                      <div class="flex gap-1 items-center justify-center w-20">
                        <label class="text-sm text-muted-foreground">Fill: </label>
                        <div class="rounded border w-10 h-6" :style="{ backgroundColor: layer.fill }"></div>
                      </div>
                      <div class="flex gap-1 items-center justify-center w-20">
                        <label class="text-sm text-muted-foreground">Stroke: </label>
                        <div class="rounded border w-10 h-6" :style="{ backgroundColor: layer.stroke }"></div>
                      </div>
                      <div class="flex gap-2 items-center justify-center w-20">
                        <label class="text-sm text-muted-foreground">Priority: </label>
                        <span class="rounded w-fit h-6 font-bold text-blue-600">{{ layer.z_index }}</span>
                      </div>
                      <div class="flex justify-center items-center w-10">
                        <Switch :model-value="DefaultlayerStates[layer.default_layer_id]"
                          @update:model-value="() => toggleDefaultLayerVisibility(layer.default_layer_id)"
                          class="cursor-pointer" />
                      </div>
                    </CardContent>
                    <span class="px-2 py-2 flex gap-2 justify-center items-center">
                      <p class="text-sm text-muted-foreground italic">Created at: {{
                        formatRelativeTime(layer.created_at) }}</p>
                      <div class="flex flex-1 items-center justify-center">
                        <button v-tooltip.bottom="'Edit layer'"
                          class="cursor-pointer text-white bg-blue-700 hover:bg-blue-800 focus:outline-none rounded-full text-sm px-3 py-2.5 text-center mr-2"
                          @click="openEditDialog(layer.default_layer_id, true)">
                          <Pencil class="w-4 h-4"></Pencil>
                        </button>
                        <button v-tooltip.bottom="'Delete layer'"
                          class="cursor-pointer text-white bg-red-700 hover:bg-red-800 focus:outline-none rounded-full text-sm px-3 py-2.5 text-center"
                          @click="deleteLayer(layer.default_layer_id, true)">
                          <Trash class="w-4 h-4"></Trash>
                        </button>
                      </div>
                    </span>
                  </Card>
                </template>
              </draggable>
            </section>

            <Separator class="my-6" />

            <section>
              <h2 class="text-xl font-semibold text-gray-700 mb-3 border-b pb-2">User Layers</h2>
              <draggable v-if="draggableUserLayers?.length" v-model="draggableUserLayers" item-key="layer_id"
                @end="onDragEndUser" class="space-y-3" tag="div">
                <template #item="{ element: layer }">
                  <Card v-tooltip="'Drag to change priority'"
                    class=" relative w-full h-40 shadow-md gap-2 transition duration-200 ease-in-out transform hover:scale-95 hover:shadow-lg pt-2 cursor-move">
                    <div class="absolute top-2 right-2">
                      <button v-tooltip.left="'Share layer'" class="cursor-pointer text-gray-600 hover:text-blue-600 focus:outline-none"
                        @click="openShareDialog(layer)">
                        <ExternalLink class="w-5 h-5" />
                      </button>
                    </div>
                    <CardHeader class="h-[54px] px-2 flex justify-center">
                      <CardTitle class="text-base text-center flex items-center font-semibold h-[54px]">{{
                        layer.layer_name }}</CardTitle>
                    </CardHeader>
                    <CardContent class="flex gap-2 items-center px-2 justify-center">
                      <div class="flex gap-1 items-center justify-center w-20">
                        <label class="text-sm text-muted-foreground">Fill: </label>
                        <div class="rounded border w-10 h-6" :style="{ backgroundColor: layer.fill }"></div>
                      </div>
                      <div class="flex gap-1 items-center justify-center w-20">
                        <label class="text-sm text-muted-foreground">Stroke: </label>
                        <div class="rounded border w-10 h-6" :style="{ backgroundColor: layer.stroke }"></div>
                      </div>
                      <div class="flex gap-2 items-center justify-center w-20">
                        <label class="text-sm text-muted-foreground">Priority: </label>
                        <span class="rounded w-fit h-6 font-bold text-blue-600">{{ layer.z_index }}</span>
                      </div>
                      <div class="flex justify-center items-center w-10">
                        <Switch :model-value="UserlayerStates[layer.layer_id]"
                          @update:model-value="() => toggleUserLayerVisibility(layer.layer_id)"
                          class="cursor-pointer" />
                      </div>
                    </CardContent>
                    <span class="px-2 py-2 flex gap-2 justify-center items-center">
                      <p class="text-sm text-muted-foreground italic">Created at: {{
                        formatRelativeTime(layer.created_at) }}</p>
                      <div class="flex flex-1 items-center justify-center">
                        <button v-tooltip.bottom="'Add more feature'"
                          class="cursor-pointer text-white bg-sky-600 hover:bg-sky-700 focus:outline-none rounded-full text-sm px-3 py-2.5 text-center mr-2"
                          @click="openAddFeatureDialog(layer.layer_id)">
                          <MapPlus class="w-4 h-4"></MapPlus>
                        </button>
                        <button v-tooltip.bottom="'Edit layer'"
                          class="cursor-pointer text-white bg-blue-700 hover:bg-blue-800 focus:outline-none rounded-full text-sm px-3 py-2.5 text-center mr-2"
                          @click="openEditDialog(layer.layer_id, false)">
                          <Pencil class="w-4 h-4"></Pencil>
                        </button>
                        <button v-tooltip.bottom="'Delete layer'"
                          class="cursor-pointer text-white bg-red-700 hover:bg-red-800 focus:outline-none rounded-full text-sm px-3 py-2.5 text-center"
                          @click="deleteLayer(layer.layer_id, false)">
                          <Trash class="w-4 h-4"></Trash>
                        </button>
                      </div>
                    </span>
                  </Card>
                </template>
              </draggable>
            </section>
          </ScrollArea>
        </TabsContent>
        <TabsContent value="features" class="mt-4 h-full">
          <ScrollArea v-if="display_default_feature && display_user_feature" class="h-[635px] space-y-6">

            <!-- 🟢 Default Layers -->
            <section>
              <h2 class="text-lg font-semibold text-muted-foreground mb-2">Default Layers</h2>
              <div class="space-y-4">
                <Card v-for="block in display_default_feature" :key="'default-' + block.layer_inform.layer_id">
                  <CardHeader class="flex items-center justify-between">
                    <CardTitle class="text-base">
                      {{ block.layer_inform.layer_name }}
                    </CardTitle>
                    <div class="flex items-center space-x-2">
                      <div class="w-4 h-4 rounded" :style="{ backgroundColor: block.layer_inform.fill }" />
                      <div class="w-4 h-4 border"
                        :style="{ borderColor: block.layer_inform.stroke, borderWidth: '2px' }" />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <ul class="space-y-1 text-sm">
                      <li
                        v-for="feature in showAllDefault[block.layer_inform.layer_id] ? block.feature_inform : block.feature_inform.slice(0, 3)"
                        :key="feature.feature_id" class="flex justify-between items-center gap-2">
                        <span>
                          {{ feature.ENGTYPE_1 }} {{ splitCamelCaseUnicode(feature.NAME_1) }} - {{ feature.COUNTRY ||
                          'N/A' }}
                        </span>
                      </li>
                    </ul>
                    <div v-if="block.feature_inform.length > 3" class="mt-2">
                      <Button variant="link" class="px-0 text-xs"
                        @click="toggleShowAllDefault(block.layer_inform.layer_id)">
                        {{ showAllDefault[block.layer_inform.layer_id] ? 'Show less' : 'Show more' }}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </section>

            <Separator />

            <!-- 🔵 User Layers -->
            <section>
              <h2 class="text-lg font-semibold text-muted-foreground mb-2">User Layers</h2>
              <div class="space-y-4">
                <Card v-for="block in display_user_feature" :key="'user-' + block.layer_inform.layer_id">
                  <CardHeader class="flex items-center justify-between">
                    <CardTitle class="text-base">
                      {{ block.layer_inform.layer_name }}
                    </CardTitle>
                    <div class="flex items-center space-x-2">
                      <div class="w-4 h-4 rounded" :style="{ backgroundColor: block.layer_inform.fill }" />
                      <div class="w-4 h-4 border"
                        :style="{ borderColor: block.layer_inform.stroke, borderWidth: '2px' }" />
                    </div>
                  </CardHeader>
                  <CardContent>
                    <ul class="space-y-1 text-sm">
                      <li
                        v-for="feature in showAllUser[block.layer_inform.layer_id] ? block.feature_inform : block.feature_inform.slice(0, 3)"
                        :key="feature.feature_id" class="flex justify-between items-center gap-2">
                        <span>
                          {{ feature.name || 'Unnamed Feature' }} - {{ feature.properties?.COUNTRY || 'N/A' }}
                        </span>
                        <div class="flex gap-2">
                          <button v-tooltip.bottom="'Delete feature'" @click="deleteFeature(block.layer_inform.layer_id,feature.feature_id)"
                            class="text-red-500 hover:text-red-600">
                            <Trash2 :size="18" />
                          </button>
                          <button v-tooltip.bottom="'Share feature'" class="text-sky-500 hover:text-sky-600"
                            @click="openFeatureShareDialog(feature.feature_id)">
                            <ExternalLink :size="18" />
                          </button>
                        </div>
                      </li>
                    </ul>
                    <div v-if="block.feature_inform.length > 3" class="mt-2">
                      <Button variant="link" class="px-0 text-xs"
                        @click="toggleShowAllUser(block.layer_inform.layer_id)">
                        {{ showAllUser[block.layer_inform.layer_id] ? 'Show less' : 'Show more' }}
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </section>
          </ScrollArea>
        </TabsContent>
      </Tabs>
    </div>
    <Dialog v-model:open="createLayerDialog">
      <DialogContent class="sm:max-w-[500px] bg-background rounded-lg shadow-xl">
        <DialogHeader>
          <DialogTitle class="text-2xl text-center font-semibold">Add New Vector Layer</DialogTitle>
          <DialogDescription class="text-muted-foreground text-base text-center">
            Create a new vector layer with custom properties
          </DialogDescription>
        </DialogHeader>
        <DialogClose class="absolute right-4 top-4" />

        <form @submit.prevent="uploadLayer" class="space-y-6 mt-4">
          <!-- Layer Name -->
          <div class="space-y-2">
            <Label for="name" class="text-sm font-medium">Layer Name <span class="text-red-500">*</span></Label>
            <Input id="name" v-model="addLayerForm.layerName" placeholder="Enter layer name" required
              class="w-full border-input focus:ring-2 focus:ring-primary" />
          </div>

          <!-- Color Pickers -->
          <div class="flex gap-4">
            <div class="flex-1 space-y-2">
              <Label for="fillColor" class="text-sm font-medium">Fill Color</Label>
              <div class="flex items-center gap-2">
                <Input id="fillColor" v-model="addLayerForm.fillColor" type="color"
                  class="w-20 h-9 p-1 rounded-md border-input" />
                <span class="text-sm text-muted-foreground">{{ addLayerForm.fillColor }}</span>
              </div>
            </div>
            <div class="flex-1 space-y-2">
              <Label for="strokeColor" class="text-sm font-medium">Stroke Color</Label>
              <div class="flex items-center gap-2">
                <Input id="strokeColor" v-model="addLayerForm.strokeColor" type="color"
                  class="w-20 h-9 p-1 rounded-md border-input" />
                <span class="text-sm text-muted-foreground">{{ addLayerForm.strokeColor }}</span>
              </div>
            </div>
            <div class="flex-1 space-y-2">
              <NumberField id="priority" v-model:model-value="max_z_index" :default-value="max_z_index" :min="max_z_index">
                <Label for="priority" class="mb-1 mt-0.7">Priority</Label>
                <NumberFieldContent>
                  <NumberFieldDecrement />
                  <NumberFieldInput />
                  <NumberFieldIncrement />
                </NumberFieldContent>
              </NumberField>
            </div>
          </div>

          <!-- Layer Type Radio Group -->
          <div class="space-y-2">
            <RadioGroup v-model="layerType" class="flex gap-4">
              <div class="flex items-center space-x-2">
                <RadioGroupItem value="empty" id="empty" />
                <Label for="empty">Empty Layer (No Features)</Label>
              </div>
              <div class="flex items-center space-x-2">
                <RadioGroupItem value="withFeatures" id="withFeatures" />
                <Label for="withFeatures">Layer with your Features</Label>
              </div>
            </RadioGroup>
          </div>

          <!-- Conditional Tabs for Features -->
          <div v-if="layerType == 'withFeatures'" class="space-y-2">
            <Tabs default-value="gis-file" class="w-full" @update:model-value="handleTabChange">
              <TabsList class="grid w-full grid-cols-3">
                <TabsTrigger value="gis-file">GIS File</TabsTrigger>
                <TabsTrigger value="layer-community">Layer Community</TabsTrigger>
                <TabsTrigger value="feature-community">Feature Community</TabsTrigger>
              </TabsList>

              <TabsContent value="gis-file" class="mt-4">
                <Label for="gisFile" class="text-sm font-medium">Upload GIS File</Label>
                <Input ref="gisFileInputRef" id="gisFile" type="file" accept=".json,.geojson,.kmz,.gpkg,.zip"
                  class="mt-2 border-input" @change="handleFileUpload" />
              </TabsContent>

              <TabsContent value="layer-community" class="mt-4">
                <RadioGroup v-model="selectedLayerId">
                  <div
                    class="space-y-8 overflow-auto max-h-[200px] p-4 scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-100">
                    <section>
                      <h2 class="text-lg font-semibold text-gray-800 mb-4">Layer from GIS Community</h2>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead class="w-[50px]">Select</TableHead>
                            <TableHead>Name</TableHead>
                            <TableHead>Created Date</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          <TableRow v-for="layer in layer_communities" :key="layer.layer_community_id"
                            class="hover:bg-gray-50">
                            <TableCell class="text-center">
                              <RadioGroupItem :value="layer.layer_community_id"
                                :id="`layer-${layer.layer_community_id}`" />
                            </TableCell>
                            <TableCell class="whitespace-normal w-[200px] max-w-[300px]">{{ layer.layer_community_name
                              }}
                            </TableCell>
                            <TableCell>{{ formatDate(layer.created_at) }}</TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </section>

                    <section>
                      <h2 class="text-lg font-semibold text-gray-800 mb-4">Layer from other users</h2>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead class="w-[50px]">Select</TableHead>
                            <TableHead>Name</TableHead>
                            <TableHead>Created Date</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          <TableRow v-for="layer in friend_share_data.list_layer_id" :key="layer.layer_community_id"
                            class="hover:bg-gray-50">
                            <TableCell class="text-center">
                              <RadioGroupItem :value="layer.layer_community_id"
                                :id="`layer-${layer.layer_community_id}`" />
                            </TableCell>
                            <TableCell class="whitespace-normal w-[200px] max-w-[300px]">{{ layer.layer_community_name
                              }}
                            </TableCell>
                            <TableCell>{{ formatDate(layer.created_at) }}</TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </section>
                  </div>
                </RadioGroup>
              </TabsContent>

              <TabsContent value="feature-community" class="mt-4">
                <RadioGroup v-model="selectedFeatureId">
                  <div
                    class="space-y-8 overflow-auto max-h-[200px] p-4 scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-100">
                    <section>
                      <h2 class="text-lg font-semibold text-gray-800 mb-4">Feature from GIS Community</h2>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead class="w-[50px]">Select</TableHead>
                            <TableHead>Name</TableHead>
                            <TableHead>Created Date</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          <TableRow v-for="feature in feature_communities" :key="feature.feature_id"
                            class="hover:bg-gray-50">
                            <TableCell class="text-center">
                              <RadioGroupItem :value="feature.feature_community_id"
                                :id="`feature-${feature.feature_id}`" />
                            </TableCell>
                            <TableCell class="whitespace-normal w-[200px] max-w-[300px]">{{
                              feature.feature_community_name }}
                            </TableCell>
                            <TableCell>{{ formatDate(feature.created_at) }}</TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </section>

                    <section>
                      <h2 class="text-lg font-semibold text-gray-800 mb-4">Feature from other users</h2>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead class="w-[50px]">Select</TableHead>
                            <TableHead>Name</TableHead>
                            <TableHead>Created Date</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          <TableRow v-for="feature in friend_share_data.list_feature_id"
                            :key="feature.feature_community_id" class="hover:bg-gray-50">
                            <TableCell class="text-center">
                              <RadioGroupItem :value="feature.feature_community_id"
                                :id="`feature-${feature.feature_community_id}`" />
                            </TableCell>
                            <TableCell class="whitespace-normal w-[200px] max-w-[300px]">{{ feature.feature_community_name
                              }}
                            </TableCell>
                            <TableCell>{{ formatDate(feature.created_at) }}</TableCell>
                          </TableRow>
                        </TableBody>
                      </Table>
                    </section>
                  </div>
                </RadioGroup>
              </TabsContent>
            </Tabs>
          </div>
        </form>

        <DialogFooter class="mt-6">
          <Button type="submit" class="bg-primary text-primary-foreground hover:bg-primary/90" @click="uploadLayer">
            <Save class="h-5 w-5 mr-2" />
            Create Layer
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
    <Dialog v-model:open="editLayerDialog">
      <DialogContent class="sm:max-w-[500px] bg-background rounded-lg shadow-xl">
        <DialogTitle class="text-2xl text-center font-semibold">Edit Your Vector Layer</DialogTitle>
        <DialogDescription class="text-muted-foreground text-base text-center">
          Update for a new vector layer information with custom properties
        </DialogDescription>
        <DialogClose class="absolute right-4 top-4" />
        <form @submit.prevent="editLayer" class="space-y-6 mt-4">
          <div class="space-y-2">
            <Label for="name" class="text-sm font-medium">New Layer Name <span class="text-red-500">*</span></Label>
            <Input id="name" v-model="editLayerForm.layer_name" placeholder="Update new layer name" required
              class="w-full border-input focus:ring-2 focus:ring-primary" />
          </div>
          <div class="flex gap-4">
            <div class="flex-1 space-y-2">
              <Label for="fillColor" class="text-sm font-medium">New Fill Color</Label>
              <div class="flex items-center gap-2">
                <Input id="fillColor" v-model="editLayerForm.fill" type="color"
                  class="w-20 h-9 p-1 rounded-md border-input" />
                <span class="text-sm text-muted-foreground">{{ editLayerForm.fill }}</span>
              </div>
            </div>
            <div class="flex-1 space-y-2">
              <Label for="strokeColor" class="text-sm font-medium">New Stroke Color</Label>
              <div class="flex items-center gap-2">
                <Input id="strokeColor" v-model="editLayerForm.stroke" type="color"
                  class="w-20 h-9 p-1 rounded-md border-input" />
                <span class="text-sm text-muted-foreground">{{ editLayerForm.stroke }}</span>
              </div>
            </div>
            <div class="flex-1 space-y-2">
              <NumberField id="priority" :default-value="editLayerForm.stroke_width" :min="1">
                <Label for="priority" class="mb-1 mt-0.7">New Stroke Width</Label>
                <NumberFieldContent>
                  <NumberFieldDecrement />
                  <NumberFieldInput />
                  <NumberFieldIncrement />
                </NumberFieldContent>
              </NumberField>
            </div>
          </div>
        </form>
        <DialogFooter>
          <Button type="submit" class="bg-primary text-primary-foreground hover:bg-primary/90" @click="editLayer">
            <Save class="h-5 w-5 mr-2" />
            Update Layer
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
    <Dialog v-model:open="addFeatureDialog">
      <DialogContent class="sm:max-w-[500px] bg-background rounded-lg shadow-xl">
        <DialogHeader>
          <DialogTitle class="text-2xl text-center font-semibold">Add More Features</DialogTitle>
          <DialogDescription class="text-muted-foreground text-base text-center">
            Add more feature to your custom layer
          </DialogDescription>
        </DialogHeader>
        <DialogClose class="absolute right-4 top-4" />

        <form @submit.prevent="addFeature" class="space-y-6 mt-4">
          <!-- Conditional Tabs for Features -->
          <Tabs default-value="gis-file"> 
            <TabsList class="grid w-full grid-cols-3">
              <TabsTrigger value="gis-file">GIS File</TabsTrigger>
              <TabsTrigger value="layer-community">Layer Community</TabsTrigger>
              <TabsTrigger value="feature-community">Feature Community</TabsTrigger>
            </TabsList>

            <TabsContent value="gis-file" class="mt-4">
              <Label for="gisFile" class="text-sm font-medium">Upload GIS File</Label>
              <Input ref="gisFileInputRef" id="gisFile" type="file" accept=".json,.geojson,.kmz,.gpkg,.zip"
                class="mt-2 border-input" @change="handleAddFeatureFileUpload" />
            </TabsContent>

            <TabsContent value="layer-community" class="mt-4">
              <RadioGroup v-model="selectedLayerId">
                <div
                  class="space-y-8 overflow-auto max-h-[200px] p-4 scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-100">
                  <section>
                    <h2 class="text-lg font-semibold text-gray-800 mb-4">Layer from GIS Community</h2>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead class="w-[50px]">Select</TableHead>
                          <TableHead>Name</TableHead>
                          <TableHead>Created Date</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        <TableRow v-for="layer in layer_communities" :key="layer.layer_community_id"
                          class="hover:bg-gray-50">
                          <TableCell class="text-center">
                            <RadioGroupItem :value="layer.layer_community_id"
                              :id="`layer-${layer.layer_community_id}`" />
                          </TableCell>
                          <TableCell class="whitespace-normal w-[200px] max-w-[300px]">{{ layer.layer_community_name
                            }}
                          </TableCell>
                          <TableCell>{{ formatDate(layer.created_at) }}</TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </section>

                  <section>
                    <h2 class="text-lg font-semibold text-gray-800 mb-4">Layer from other users</h2>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead class="w-[50px]">Select</TableHead>
                          <TableHead>Name</TableHead>
                          <TableHead>Created Date</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        <TableRow v-for="layer in friend_share_data.list_layer_id" :key="layer.layer_community_id"
                          class="hover:bg-gray-50">
                          <TableCell class="text-center">
                            <RadioGroupItem :value="layer.layer_community_id"
                              :id="`layer-${layer.layer_community_id}`" />
                          </TableCell>
                          <TableCell class="whitespace-normal w-[200px] max-w-[300px]">{{ layer.layer_community_name
                            }}
                          </TableCell>
                          <TableCell>{{ formatDate(layer.created_at) }}</TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </section>
                </div>
              </RadioGroup>
            </TabsContent>

            <TabsContent value="feature-community" class="mt-4">
              <RadioGroup v-model="selectedFeatureId">
                <div
                  class="space-y-8 overflow-auto max-h-[200px] p-4 scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-100">
                  <section>
                    <h2 class="text-lg font-semibold text-gray-800 mb-4">Feature from GIS Community</h2>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead class="w-[50px]">Select</TableHead>
                          <TableHead>Name</TableHead>
                          <TableHead>Created Date</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        <TableRow v-for="feature in feature_communities" :key="feature.feature_id"
                          class="hover:bg-gray-50">
                          <TableCell class="text-center">
                            <RadioGroupItem :value="feature.feature_community_id"
                              :id="`feature-${feature.feature_id}`" />
                          </TableCell>
                          <TableCell class="whitespace-normal w-[200px] max-w-[300px]">{{
                            feature.feature_community_name }}
                          </TableCell>
                          <TableCell>{{ formatDate(feature.created_at) }}</TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </section>

                  <section>
                    <h2 class="text-lg font-semibold text-gray-800 mb-4">Feature from other users</h2>
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead class="w-[50px]">Select</TableHead>
                          <TableHead>Name</TableHead>
                          <TableHead>Created Date</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        <TableRow v-for="feature in friend_share_data.list_feature_id"
                          :key="feature.feature_community_id" class="hover:bg-gray-50">
                          <TableCell class="text-center">
                            <RadioGroupItem :value="feature.feature_community_id"
                              :id="`feature-${feature.feature_community_id}`" />
                          </TableCell>
                          <TableCell class="whitespace-normal w-[200px] max-w-[300px]">{{ feature.feature_community_name
                            }}
                          </TableCell>
                          <TableCell>{{ formatDate(feature.created_at) }}</TableCell>
                        </TableRow>
                      </TableBody>
                    </Table>
                  </section>
                </div>
              </RadioGroup>
            </TabsContent>
          </Tabs>
        </form>
        <DialogFooter class="mt-6">
          <Button type="submit" class="bg-primary text-primary-foreground hover:bg-primary/90" @click="addFeature">
            <Save class="h-5 w-5 mr-2" />
            Add features
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
    <Dialog v-model:open="isShareDialogOpen">
      <DialogContent class="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Share Layer to Community</DialogTitle>
          <DialogDescription>
            Fill in the details to share this layer to the community.
          </DialogDescription>
        </DialogHeader>
        <div class="grid gap-4 py-4">
          <div class="grid grid-cols-4 items-center gap-4">
            <Label for="layer_community_name" class="text-right">Name</Label>
            <Input id="layer_community_name" v-model="shareFormData.layer_community_name" class="col-span-3"
              placeholder="Enter community layer name" />
          </div>
          <div class="grid grid-cols-4 items-center gap-4">
            <Label for="layer_community_description" class="text-right">Description</Label>
            <Textarea id="layer_community_description" v-model="shareFormData.layer_community_description"
              class="col-span-3" placeholder="Enter community layer description" />
          </div>
          <div class="grid grid-cols-4 items-center gap-4">
            <Label for="layer_community_image" class="text-right">Image</Label>
            <Input id="layer_community_image" type="file" accept="image/*" class="col-span-3"
              @change="handleImageUpload" />
          </div>
          <div class="grid grid-cols-4 items-center gap-4">
            <Label for="access_rights" class="text-right">Access</Label>
            <Select id="access_rights" v-model="shareFormData.access_rights" class="col-span-3">
              <SelectTrigger>
                <SelectValue placeholder="Select access rights" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Public">Everyone</SelectItem>
                <SelectItem value="Restricted">Other Users</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div v-if="shareFormData.access_rights == 'Restricted'" class="grid grid-cols-4 items-center gap-4">
            <Label for="user_informs" class="text-right">Friends</Label>
            <TagsInput v-model="shareFormData.user_informs" class="col-span-3">
              <TagsInputItem v-for="item in shareFormData.user_informs" :key="item" :value="item">
                <TagsInputItemText />
                <TagsInputItemDelete />
              </TagsInputItem>
              <TagsInputInput placeholder="Enter other users's username or email..." />
            </TagsInput>
          </div>
        </div>
        <DialogFooter>
          <Button type="submit" :disabled="!isFormValid" @click="submitLayerCommunity">
            Share
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
    <Dialog v-model:open="isShareFeatureDialogOpen">
      <DialogContent class="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Share Feature to Community</DialogTitle>
          <DialogDescription>
            Fill in the details to share this feature to the community.
          </DialogDescription>
        </DialogHeader>
        <div class="grid gap-4 py-4">
          <div class="grid grid-cols-4 items-center gap-4">
            <Label for="layer_community_name" class="text-right">Name</Label>
            <Input id="layer_community_name" v-model="shareFeatureFormData.feature_community_name" class="col-span-3"
              placeholder="Enter community feature name" />
          </div>
          <div class="grid grid-cols-4 items-center gap-4">
            <Label for="layer_community_description" class="text-right">Description</Label>
            <Textarea id="layer_community_description" v-model="shareFeatureFormData.feature_community_description"
              class="col-span-3" placeholder="Enter community feature description" />
          </div>
          <div class="grid grid-cols-4 items-center gap-4">
            <Label for="layer_community_image" class="text-right">Image</Label>
            <Input id="layer_community_image" type="file" accept="image/*" class="col-span-3"
              @change="handleFeatureImageUpload" />
          </div>
          <div class="grid grid-cols-4 items-center gap-4">
            <Label for="access_rights" class="text-right">Access</Label>
            <Select id="access_rights" v-model="shareFeatureFormData.access_rights" class="col-span-3">
              <SelectTrigger>
                <SelectValue placeholder="Select access rights" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Public">Everyone</SelectItem>
                <SelectItem value="Restricted">Other Users</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div v-if="shareFeatureFormData.access_rights == 'Restricted'" class="grid grid-cols-4 items-center gap-4">
            <Label for="user_informs" class="text-right">Friends</Label>
            <TagsInput v-model="shareFeatureFormData.user_informs" class="col-span-3">
              <TagsInputItem v-for="item in shareFeatureFormData.user_informs" :key="item" :value="item">
                <TagsInputItemText />
                <TagsInputItemDelete />
              </TagsInputItem>
              <TagsInputInput placeholder="Enter other users's username or email..." />
            </TagsInput>
          </div>
        </div>
        <DialogFooter>
          <Button type="submit" :disabled="!isShareFeaturFormValid" @click="submitFeatureCommunity">
            Share
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
    <FeaturePopup v-if="map" @update:UpdateFeatureInforms="isUpdatePopup = $event" :map="map"
      :feature-data="filteredFeatureData" :is-drawing="isDrawing" />
  </div>
</template>

<script setup>
import axios from 'axios';
import ControlButtonGroup from '@/components/ExpandableActionButton/ControlButtonGroup.vue';
import DrawButtonGroup from '@/components/ExpandableActionButton/DrawButtonGroup.vue';
import FeaturePopup from '@/components/FeaturePopup/FeaturePopup.vue';
import ControlBaseButtonGroup from '@/components/ExpandableActionButton/ControlBaseButtonGroup.vue';
import { reactive, onMounted, ref, computed, watchEffect, watch, warn } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { createMap, createDefaultVectorLayer, addFeaturetoDefaultVectorLayer, createDefaultTileLayer, createUserVectorLayer, updateColorDefaultVectorLayer, updateColorUserVectorLayer, deleteDefaultVectorLayer, deleteUserVectorLayer, addFeaturetoUserLayer, deleteUserFeature, update_priority } from '@/modules/openlayer';
import { flashById, resetLayerStyles } from '@/modules/openlayer_animation';
import GeoJSON from 'ol/format/GeoJSON';
import VectorLayer from 'ol/layer/Vector';
import { cn } from '@/lib/utils'
import Project_Loading from '@/components/Loading/Project_Loading.vue';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger
} from '@/components/ui/dropdown-menu'
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger
} from '@/components/ui/tooltip'
import { Dialog, DialogContent, DialogClose, DialogFooter, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog';
import Button from '@/components/ui/button/Button.vue';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Combobox, ComboboxAnchor, ComboboxEmpty, ComboboxGroup, ComboboxInput, ComboboxItem, ComboboxItemIndicator, ComboboxList } from '@/components/ui/combobox'
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '@/components/ui/select'
import { formatDistanceToNow } from 'date-fns'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { Textarea } from '@/components/ui/textarea'
import {
  MapPin, Circle, Square, PenSquare, MousePointerClick,
  Layers, ZoomIn, ZoomOut, Globe, Satellite, Trash, Pencil,
  Search, Check, Plus, Save, MapPlus, Trash2, Share,
  ExternalLink, Merge
} from 'lucide-vue-next';
import {
  NumberField,
  NumberFieldContent,
  NumberFieldDecrement,
  NumberFieldIncrement,
  NumberFieldInput,
} from '@/components/ui/number-field'
import { TagsInput, TagsInputItem, TagsInputItemText, TagsInputItemDelete, TagsInputInput } from '@/components/ui/tags-input'
import Separator from '@/components/ui/separator/Separator.vue';
import Label from '@/components/ui/label/Label.vue';
import Swal from 'sweetalert2'
import draggable from 'vuedraggable'
const mapContainer = ref(null);
const map = ref(null)
const isDrawing = ref(false)
const isSaving = ref(false);
const isUpdatePopup = ref(false);
const baseIds = ref([]);
// Khởi tạo router và route
const route = useRoute();
const router = useRouter();
const MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024
// Khởi tạo trạng thái reactive
const state = reactive({
  projectId: null,
});
const layer_response = ref([]);
const user_layer = ref([]);
const draggableDefaultLayers = ref([]);
const draggableUserLayers = ref([]);
const isDefaultOrderChanged = ref(false);
const isUserOrderChanged = ref(false);
const isOrderChanged = computed(() => isDefaultOrderChanged.value || isUserOrderChanged.value);
const list_default_layer_id = ref([]);
const list_user_layer_id = ref([]);
const list_default_feature = ref([]);
const featureInforms = ref([])
const selectedTitle = ref('All')
const isLoading = ref(true);
const checked = ref(true)
const DefaultlayerStates = ref();
const UserlayerStates = ref();
const display_layer = ref([]);
const searchQuery = ref('');
const createLayerDialog = ref(false);
const editLayerDialog = ref(false);
const addFeatureDialog = ref(false);
const isShareDialogOpen = ref(false);
const isShareFeatureDialogOpen = ref(false);
const user_layer_data = ref([]);
const showAllDefault = ref([]);
const showAllUser = ref([]);
const new_version_feature = ref([])
const contron_version_status = ref(false);
const layer_communities = ref([])
const feature_communities = ref([])
const friend_share_data = ref([])
const friend_share_layer = ref([])
const friend_share_feature = ref([])
const Ltags = ref([])
const Ftags = ref([])
const selectedLayerId = ref(null);
const selectedFeatureId = ref(null);
const gisFileInputRef = ref(null);
const addLayerForm = ref({
  layerName: '',
  fillColor: '#1717CD',
  strokeColor: '#000000',
  layerType: 'empty',
  file: null,
  projectId: '',
  strokeWidth: 1,
  priority: null,
})
let max_z_index = ref(2)
const editLayerForm = ref({
  layer_id: 0,
  layer_name: '',
  fill: '',
  stroke: '',
  stroke_width: 1,
})
const addFeatureForm = ref({
  layer_id: 0,
  file: null,
})
const shareFormData = ref({
  layer_id: null,
  layer_community_name: '',
  layer_community_description: '',
  layer_community_image: null,
  access_rights: 'Public',
  user_informs: [],
})

const shareFeatureFormData = ref({
  feature_id: null,
  feature_community_name: '',
  feature_community_description: '',
  feature_community_image: null,
  access_rights: 'Public',
  user_informs: [],
})

const openShareDialog = (layer) => {
  shareFormData.value.layer_id = layer.layer_id
  shareFormData.value.layer_community_name = ''
  shareFormData.value.layer_community_description = ''
  shareFormData.value.layer_community_image = null
  shareFormData.value.access_rights = 'Public'
  shareFormData.value.user_informs = []
  isShareDialogOpen.value = true
}
const openFeatureShareDialog = (feature_id) => {
  shareFeatureFormData.value.feature_id = feature_id
  shareFeatureFormData.value.feature_community_name = ''
  shareFeatureFormData.value.feature_community_description = ''
  shareFeatureFormData.value.feature_community_image = null
  shareFeatureFormData.value.access_rights = 'Public'
  shareFeatureFormData.value.user_informs = []
  isShareFeatureDialogOpen.value = true
}
const handleTabChange = (newTabValue) => {
  console.log(`Tab changed to: ${newTabValue}`);
  // Reset các giá trị không liên quan đến tab hiện tại
  if (newTabValue == 'gis-file') {
    selectedLayerId.value = null;
    selectedFeatureId.value = null;
  } else if (newTabValue == 'layer-community') {
    selectedFeatureId.value = null;
    // Reset file input
    if (gisFileInputRef.value) {
      gisFileInputRef.value.value = '';
    }
    addLayerForm.value.file = null
  } else if (newTabValue == 'feature-community') {
    selectedLayerId.value = null;
    // Reset file input
    if (gisFileInputRef.value) {
      gisFileInputRef.value.value = '';
    }
    addLayerForm.value.file = null
  }
};
const handleAddFeatureTabChange = (newTabValue) => {
  console.log(`Tab changed to: ${newTabValue}`);
  // Reset các giá trị không liên quan đến tab hiện tại
  if (newTabValue == 'gis-file') {
    selectedLayerId.value = null;
    selectedFeatureId.value = null;
  } else if (newTabValue == 'layer-community') {
    selectedFeatureId.value = null;
    // Reset file input
    if (gisFileInputRef.value) {
      gisFileInputRef.value.value = '';
    }
    addFeatureForm.value.file = null
  } else if (newTabValue == 'feature-community') {
    selectedLayerId.value = null;
    // Reset file input
    if (gisFileInputRef.value) {
      gisFileInputRef.value.value = '';
    }
    addFeatureForm.value.file = null
  }
};
const handleImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      shareFormData.value.layer_community_image = e.target.result
    }
    reader.readAsDataURL(file)
  }
}
const handleFeatureImageUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (e) => {
      shareFeatureFormData.value.feature_community_image = e.target.result
    }
    reader.readAsDataURL(file)
  }
}
const isFormValid = computed(() => {
  if(shareFormData.value.access_rights == "Restricted" && shareFormData.value.user_informs.length == 0) return false
  return (
    shareFormData.value.layer_id !== null &&
    shareFormData.value.layer_community_name.trim() !== '' &&
    shareFormData.value.layer_community_image !== null
  )
})
const isShareFeaturFormValid = computed(() => {
  if(shareFeatureFormData.value.access_rights == "Restricted" && shareFeatureFormData.value.user_informs.length == 0) return false
  return (
    shareFeatureFormData.value.feature_id !== null &&
    shareFeatureFormData.value.feature_community_name.trim() !== '' &&
    shareFeatureFormData.value.feature_community_image !== null
  )
})
const submitLayerCommunity = async () => {
console.log(shareFormData.value)
  try {
    const response = await axios.post('http://localhost:8000/layer_community', {
      layer_id: shareFormData.value.layer_id,
      layer_community_name: shareFormData.value.layer_community_name,
      layer_community_description: shareFormData.value.layer_community_description,
      access_rights: shareFormData.value.access_rights,
      layer_community_image: shareFormData.value.layer_community_image,
    }, {
    headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
    })
    console.log(response.data)
    if (shareFormData.value.access_rights == 'Restricted') {
      const access_control_response = await axios.post('http://localhost:8000/community_access_control/add-layer-access', {
        layer_community_id: response.data.layer_community_id,
        user_informs: shareFormData.value.user_informs,
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      })
      console.log(access_control_response.data)
    }

    isShareDialogOpen.value = false
    shareFormData.value = {
      layer_id: null,
      layer_community_name: '',
      layer_community_description: '',
      layer_community_image: null,
      access_rights: 'Public',
      user_informs: [],
    }
    Swal.fire({
      icon: 'success',
      title: 'Success',
      text: `Layer shared successfully!`,
    })
  } catch (error) {
    console.error('Error sharing layer:', error)
    alert('Failed to share layer')
  }
}
const submitFeatureCommunity = async () => {
console.log(shareFeatureFormData.value)
  try {
    const response = await axios.post('http://localhost:8000/feature_community', {
      feature_id: shareFeatureFormData.value.feature_id,
      feature_community_name: shareFeatureFormData.value.feature_community_name,
      feature_community_description: shareFeatureFormData.value.feature_community_description,
      access_rights: shareFeatureFormData.value.access_rights,
      feature_community_image: shareFeatureFormData.value.feature_community_image,
    }, {
    headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
    })
    console.log(response.data)
    if (shareFeatureFormData.value.access_rights == 'Restricted') {
      const access_control_response = await axios.post('http://localhost:8000/community_access_control/add-feature-access', {
        feature_community_id: response.data.feature_community_id,
        user_informs: shareFeatureFormData.value.user_informs,
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        },
      })
      console.log(access_control_response.data)
    }

    isShareFeatureDialogOpen.value = false
    shareFeatureFormData.value = {
      feature_id: null,
      feature_community_name: '',
      feature_community_description: '',
      feature_community_image: null,
      access_rights: 'Public',
      user_informs: [],
    }
     Swal.fire({
      icon: 'success',
      title: 'Success',
      text: `Feature shared successfully!`,
    })
  } catch (error) {
    console.error('Error sharing layer:', error)
    alert('Failed to share feature')
  }
}
const layerType = ref('empty')
const editDefaultLayer = ref(null);
const defaultLayers = computed(() => {
  if (!searchQuery.value.trim()) return layer_response.value
  return layer_response.value.filter(layer =>
    layer.layer_name.toLowerCase().includes(searchQuery.value.toLowerCase()))
})

const userLayers = computed(() => {
  if (!searchQuery.value.trim()) return user_layer.value
  return user_layer.value.filter(layer =>
    layer.layer_name.toLowerCase().includes(searchQuery.value.toLowerCase()))
})

const display_default_feature = computed(() => {
  const activeLayerIds = Object.entries(DefaultlayerStates.value)
    .filter(([_, value]) => value)
    .map(([key]) => parseInt(key))

  const result = []

  for (const layerId of activeLayerIds) {
    const features = list_default_feature.value.filter(f => f.layer_id == layerId)
    const feature_inform = features.map(({ geometry, ...rest }) => rest)
    const layerMeta = defaultLayers.value.find(l => l.default_layer_id == layerId)

    result.push({
      layer_inform: {
        layer_id: layerId,
        layer_name: layerMeta?.layer_name ?? '',
        fill: layerMeta?.fill ?? '',
        stroke: layerMeta?.stroke ?? ''
      },
      feature_inform: feature_inform
    })
  }
  return result
})

const display_user_feature = computed(() => {
  const activeLayerIds = Object.entries(UserlayerStates.value)
    .filter(([_, value]) => value)
    .map(([key]) => parseInt(key))

  const result = []

  for (const layerItem of user_layer_data.value) {
    const layerId = layerItem.layer?.id
    if (!activeLayerIds.includes(layerId)) continue

    const feature_inform = layerItem.features.map(({ geom, ...rest }) => rest)
    const layerMeta = userLayers.value.find(l => l.layer_id == layerId)

    result.push({
      layer_inform: {
        layer_id: layerId,
        layer_name: layerMeta?.layer_name ?? '',
        fill: layerMeta?.fill ?? '',
        stroke: layerMeta?.stroke ?? ''
      },
      feature_inform: feature_inform
    })
  }
  return result
})

const filteredFeatureData = computed(() => {
  return display_user_feature.value
    .flatMap(block => block.feature_inform)
    .map(({ geom, ...rest }) => rest) // Loại bỏ trường geom, giữ lại các trường khác
})

// Lấy danh sách title duy nhất từ feature_informs
const uniqueTitles = computed(() => {
  const titles = featureInforms.value.map(inform => inform.title)
  console.log(titles)
  return [...new Set(titles)] // Loại bỏ các title trùng lặp
})
const filterFeatureid = computed(() => {
  const result = featureInforms.value.map(inform => inform.feature_id)
  console.log(result)
  return result
})
// Lọc feature dựa trên title được chọn
const filteredFeatures = ref([])

// Hàm giải mã projectId
const decodeProjectId = () => {
  const encodedId = route.params.encodedId;
  try {
    const decodedId = atob(encodedId);
    const parsedId = parseInt(decodedId, 10);
    state.projectId = parsedId;
  } catch (error) {
    console.error('Lỗi giải mã project_id:', error);
    // Chuyển hướng về /home nếu lỗi
    router.push('/home');
  }
};

const fetchDefaultVectorLayer = async () => {
  let list_temp_default_feature = []
  const response = await axios.get(`http://localhost:8000/default-vector-layer-informs/${state.projectId}`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json',
    },
  })
  layer_response.value = response.data
  list_default_layer_id.value = layer_response.value.map(item => item.default_layer_id)
  try {
    const response = await axios.post(
      'http://localhost:8000/default-features/by-layer-ids',
      list_default_layer_id.value,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      }
    );
    list_temp_default_feature = response.data
    const get_feature_id_response = await axios.get(`http://localhost:8000/default-feature-settings/${state.projectId}`, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json',
      },
    })
    const array2 = get_feature_id_response.data
    const defaultFeatureIds = array2.map(item => item.default_feature_id);
    list_default_feature.value = list_temp_default_feature.filter(item => defaultFeatureIds.includes(item.id));
  } catch (error) {
    console.error('Lỗi khi gọi API:', error);
    if (error.response?.status == 404) {
      alert('Không tìm thấy feature cho các layer IDs này');
    } else {
      alert('Đã có lỗi xảy ra');
    }
  }
}
const fetchUserVectorLayer = async () => {
  let list_temp_default_feature = []
  const user_layer_response = await axios.get(`http://localhost:8000/layers/projects/${state.projectId}`, {
    headers: {
      Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json',
    },
  })
  user_layer.value = user_layer_response.data
  list_user_layer_id.value = user_layer.value.map(item => item.layer_id)
  const response = await axios.post(
    'http://localhost:8000/features/by-ids', list_user_layer_id.value,
    {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      },
    }
  );
  user_layer_data.value = response.data
  filteredFeatures.value = user_layer_data.value.flatMap(layerItem => layerItem.features)
  console.log(user_layer_data.value)

}
const fetchUserFeatureInforms = async () => {
  const list_user_feature_id = user_layer_data.value.flatMap(item =>
    item.features.map(f=> f.feature_id)
  )
  const fetch_feature_informs_response = await axios.post('http://localhost:8000/feature_informs/by_feature_ids', list_user_feature_id,{
    headers: {
      Authorization: `Bearer ${localStorage.getItem('access_token')}`,
      'Content-Type': 'application/json',
    },
  })
  if(fetch_feature_informs_response.status !=200 ) return;
  featureInforms.value = fetch_feature_informs_response.data
}
const fetchCommunityInforms = async () => {
  const layer_community_response = await axios.get('http://localhost:8000/layer_community', {
    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
  });
  layer_communities.value = layer_community_response.data.map(item => ({
    ...item,
    layer_community_image: item.layer_community_image || null,
  }));
  const feature_community_response = await axios.get('http://localhost:8000/feature_community', {
    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
  });
  feature_communities.value = feature_community_response.data.map(item => ({
    ...item,
    feature_community_image: item.feature_community_image || null,
  }));
  const friend_share_response = await axios.get('http://localhost:8000/community_access_control/get-access-controls', {
    headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
  });
  friend_share_data.value = friend_share_response.data
  console.log("Layer community: ", layer_communities.value)
  console.log("Feature community: ", feature_communities.value)
  console.log("Share community: ",friend_share_data.value)
}
const initMap = async () => {
  map.value = createMap('map', {
    center: [105.5056, 17.2625],
    zoom: 5.5,
  });
  baseIds.value = layer_response.value[0].base
    .split('-')
    .map(id => parseInt(id, 10))
    .filter(id => !isNaN(id))
  const tileLayers = createDefaultTileLayer(layer_response.value[0].base)
  tileLayers.forEach(layer => map.value.addLayer(layer))
  layer_response.value.forEach(item => {
    const features = list_default_feature.value.filter(feature => feature.layer_id == item.default_layer_id)
    const vectorLayer = createDefaultVectorLayer({
      list_features: features,
      fill: item.fill,
      stroke: item.stroke,
      stroke_width: item.stroke_width,
      z_index: item.z_index,
      layer_id: item.default_layer_id
    })
    map.value.addLayer(vectorLayer)
  })
  user_layer_data.value.forEach(layer => {
    const temp_vectorLayer = createUserVectorLayer(layer.layer, layer.features)
    map.value.addLayer(temp_vectorLayer)
  })
  isLoading.value = false
}
const displayData = async () => {
  display_layer.value = [...layer_response.value, ...user_layer.value]

  DefaultlayerStates.value = Object.fromEntries(layer_response.value.map(l => [l.default_layer_id, true]))
  UserlayerStates.value = Object.fromEntries(user_layer.value.map(l => [l.layer_id, false]))
  return true
}
const toggleDefaultLayerVisibility = (layerId) => {
  DefaultlayerStates.value[layerId] = !DefaultlayerStates.value[layerId]

  // Gửi dữ liệu xuống hàm xử lý layer trong map
  handleDefaultLayerToggle(layerId, DefaultlayerStates.value[layerId])
  console.log(display_default_feature.value)
}

const handleDefaultLayerToggle = (layerId, isVisible) => {
  // Giả sử bạn đã có map object ở global
  const layers = map.value.getLayers().getArray();
  const vector_layers = layers.filter(layer => layer instanceof VectorLayer)
  const targetLayer = vector_layers
    .find(layer => layer.getProperties().default_layer_id == layerId)

  if (targetLayer) {
    targetLayer.setVisible(isVisible)
  }
}

const toggleUserLayerVisibility = (layerId) => {
  UserlayerStates.value[layerId] = !UserlayerStates.value[layerId]

  // Gửi dữ liệu xuống hàm xử lý layer trong map
  handleUserLayerToggle(layerId, UserlayerStates.value[layerId])
  console.log(display_user_feature.value)
}

const handleUserLayerToggle = (layerId, isVisible) => {
  // Giả sử bạn đã có map object ở global
  const layers = map.value.getLayers().getArray();
  const vector_layers = layers.filter(layer => layer instanceof VectorLayer)
  const targetLayer = vector_layers
    .find(layer => layer.getProperties().id == layerId)
  if (targetLayer) {
    targetLayer.setVisible(isVisible)
  }
}

const formatRelativeTime = (date) => {
  if (!date) return 'N/A';
  try {
    return formatDistanceToNow(new Date(date), { addSuffix: true }); // e.g., "3 months ago"
  } catch (error) {
    console.error('Error formatting relative time:', error);
    return 'Invalid date';
  }
};
const restrictFileSize = (file) => {
  if (file && file.size > MAX_FILE_SIZE) {
    Swal.fire({
      icon: 'error',
      title: 'File Too Large',
      text: 'The uploaded file exceeds the 5GB limit.',
    })
    return false
  }
  return true
}
const uploadLayer = async () => {
  if (!addLayerForm.value.layerName) {
    Swal.fire({
      icon: 'error',
      title: 'Validation Error',
      text: 'Layer name is required.',
    })
    return
  }


  const formData = new FormData();
  const formObject = {
    project_id: state.projectId,
    name: addLayerForm.value.layerName,
    fill_color: addLayerForm.value.fillColor,
    stroke_color: addLayerForm.value.strokeColor,
    stroke_width: addLayerForm.value.strokeWidth,
    priority: max_z_index.value,
  };
  if (addLayerForm.value.file) {
    formData.append('file', addLayerForm.value.file)
  }
  else if(selectedLayerId.value){
    try {
      const layer_id_response = await axios.get(`http://localhost:8000/layer_community/${selectedLayerId.value}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
      });
      formObject.layer_community_id = layer_id_response.data;
      console.log('layer_community_id:', formObject.layer_community_id);
    } catch (error) {
      console.error('Lỗi khi lấy layer_community_id:', error);
      throw error; // Ném lỗi để xử lý ở catch bên dưới
    }
  } else if(selectedFeatureId.value){
    try {
      const feature_id_response = await axios.get(`http://localhost:8000/feature_community/${selectedFeatureId.value}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
      });
      formObject.feature_community_id = feature_id_response.data;
      console.log('feature_community_id:', formObject.feature_community_id);
    } catch (error) {
      console.error('Lỗi khi lấy feature_community_id:', error);
      throw error; // Ném lỗi để xử lý ở catch bên dưới
    }
  }
  formData.append('form', JSON.stringify(formObject));
  try {
    const response = await axios.post(
      'http://localhost:8000/layers/',
      formData,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    const NewUserVectorLayer = createUserVectorLayer(response.data.layer, response.data.features)
    map.value.addLayer(NewUserVectorLayer)
    const data = {
      project_id: state.projectId,
      layer_id: response.data.layer.id,
      feature_ids: response.data.features.map(feature => feature.feature_id)
    }
    await fetchUserVectorLayer()
    Swal.fire({
      icon: 'success',
      title: 'Success',
      text: `Layer created with ${response.data.feature_count} features.`,
    })

    // Reset form
    addLayerForm.value = {
      layerName: '',
      fillColor: '#1717CD',
      strokeColor: '#000000',
      layerType: 'empty',
      file: null,
      projectId: '',
      strokeWidth: 1,
      priority: 0,
    }
    createLayerDialog.value = false
  } catch (error) {
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: error.response?.data?.detail || 'Failed to create layer.',
    })
    console.log(error)
  }
}

// Cập nhật hàm xử lý file upload
const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file && restrictFileSize(file)) {
    addLayerForm.value.file = file
  } else {
    addLayerForm.value.file = null
    event.target.value = '' // Reset input file
  }
}
const handleAddFeatureFileUpload = (event) => {
  const file = event.target.files[0]
  if (file && restrictFileSize(file)) {
    addFeatureForm.value.file = file
  } else {
    addFeatureForm.value.file = null
    event.target.value = '' // Reset input file
  }
}
const openAddLayerDialog = () => {
  if (createLayerDialog) {
    createLayerDialog.value = true;
  } else {
    console.error('createLayerDialog is not defined');
  }
};
const openEditDialog = (layerID, isDefault) => {
  if (isDefault) {
    const edit_layer_inform = defaultLayers.value.find(layer => layer.default_layer_id == layerID)
    editLayerForm.value.layer_id = layerID
    editLayerForm.value.layer_name = edit_layer_inform.layer_name
    editLayerForm.value.fill = edit_layer_inform.fill
    editLayerForm.value.stroke = edit_layer_inform.stroke
    editLayerForm.value.stroke_width = edit_layer_inform.stroke_width
  } else {
    const edit_layer_inform = userLayers.value.find(layer => layer.layer_id == layerID)
    editLayerForm.value.layer_id = layerID
    editLayerForm.value.layer_name = edit_layer_inform.layer_name
    editLayerForm.value.fill = edit_layer_inform.fill
    editLayerForm.value.stroke = edit_layer_inform.stroke
    editLayerForm.value.stroke_width = edit_layer_inform.stroke_width
  }
  editDefaultLayer.value = isDefault
  editLayerDialog.value = true
}
const openAddFeatureDialog = (layerID) => {
  addFeatureDialog.value = true
  addFeatureForm.value.layer_id = layerID
}
const editLayer = async () => {
  if (editDefaultLayer.value) {
    try {
      const edit_layer_response = await axios.put(`http://localhost:8000/default-vector-layer-informs/informs/${state.projectId}/${editLayerForm.value.layer_id}`, {
        layer_name: editLayerForm.value.layer_name,
        fill: editLayerForm.value.fill,
        stroke: editLayerForm.value.stroke,
        stroke_width: editLayerForm.value.stroke_width
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      })
      updateColorDefaultVectorLayer(map.value, editLayerForm.value.fill, editLayerForm.value.stroke, editLayerForm.value.layer_id)
    } catch (error) {
      console.log("Bị lỗi: ", error)
    }
    await fetchDefaultVectorLayer()
  }
  else {
    try {
      const edit_layer_response = await axios.put(`http://localhost:8000/layers/${editLayerForm.value.layer_id}`, {
        layer_name: editLayerForm.value.layer_name,
        fill: editLayerForm.value.fill,
        stroke: editLayerForm.value.stroke,
        stroke_width: editLayerForm.value.stroke_width
      }, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`
        }
      })
      updateColorUserVectorLayer(map.value, editLayerForm.value.fill, editLayerForm.value.stroke, editLayerForm.value.layer_id)
      editDefaultLayer.value = null
    } catch (error) {
      console.log("Bị lỗi: ", error)
    }
    await fetchUserVectorLayer()
  }
  editDefaultLayer.value = null
  editLayerDialog.value = false
  Swal.fire({
    icon: 'success',
    title: 'Success',
    text: `Update your Vector Layer successful!`,
  })
}
const deleteLayer = async (layerID, isDefault) => {
  if (isDefault) {
    const delete_response = await axios.patch(`http://localhost:8000/default-vector-layer-informs/${state.projectId}/${layerID}`, {}, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    await fetchDefaultVectorLayer()
    deleteDefaultVectorLayer(map.value, layerID)
  } else {
    const delete_response = await axios.patch(`http://localhost:8000/layers/${layerID}`, {}, {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      }
    })
    await fetchUserVectorLayer()
    deleteUserVectorLayer(map.value, layerID)
  }
  Swal.fire({
    icon: 'success',
    title: 'Success',
    text: `Delete your Vector Layer successful!`,
  })

}
function toggleShowAllDefault(layerId) {
  showAllDefault.value[layerId] = !showAllDefault.value[layerId]
}
function toggleShowAllUser(layerId) {
  showAllUser.value[layerId] = !showAllUser.value[layerId]
}
function splitCamelCaseUnicode(str) {
  return str.replace(/(\p{Ll})(\p{Lu})/gu, '$1 $2')
}
async function deleteFeature(layerid, featureid){
  try{
    const delete_response = await axios.delete(`http://localhost:8000/features/${featureid}`,{
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      },
    })
    deleteUserFeature(map.value, layerid, featureid)
    removeFeatureFromLayerData(layerid, featureid)
    Swal.fire({
      icon: 'success',
      title: 'Success',
      text: `Delete your feature is succeessfull!`,
    })
  }
  catch(error){
    console.error(error)
  }
}
function removeFeatureFromLayerData(layerid,featureid) {
  const targetLayer = user_layer_data.value.find(item => item.layer?.id === layerid)
  if (targetLayer) {
    targetLayer.features = targetLayer.features.filter(f => f.feature_id !== featureid)
  }
}
const addFeature = async () => {
  const formData = new FormData()
  let formObject = {
    layer_id: addFeatureForm.value.layer_id
  }
  if (addFeatureForm.value.file && !restrictFileSize(addFeatureForm.value.file)) {
    return
  }
  if (addFeatureForm.value.file) {
    formData.append('file', addFeatureForm.value.file)
  }
  else {
    if (selectedLayerId.value) {
      try {
        const layer_id_response = await axios.get(`http://localhost:8000/layer_community/${selectedLayerId.value}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
        });
        formObject.layer_community_id = layer_id_response.data;
        console.log('layer_community_id:', formObject.layer_community_id);
      } catch (error) {
        console.error('Lỗi khi lấy layer_community_id:', error);
        throw error; // Ném lỗi để xử lý ở catch bên dưới
      }
    } else if (selectedFeatureId.value) {
      try {
        const feature_id_response = await axios.get(`http://localhost:8000/feature_community/${selectedFeatureId.value}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}` },
        });
        formObject.feature_community_id = feature_id_response.data;
        console.log('feature_community_id:', formObject.feature_community_id);
      } catch (error) {
        console.error('Lỗi khi lấy feature_community_id:', error);
        throw error; // Ném lỗi để xử lý ở catch bên dưới
      }
    }
  }
  formData.append('form', JSON.stringify(formObject));
  console.log(formData.get('form'))
  console.log(formData.get('file'))
  try {
    const response = await axios.post(
      'http://localhost:8000/features/feature-to-layers',
      formData,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    console.log(response)
    addFeaturetoUserLayer(map.value, response.data.layer_id, response.data.features)
    addFeatureToLayerData(response.data.layer_id, response.data.features)
    Swal.fire({
      icon: 'success',
      title: 'Success',
      text: `Layer created with ${response.data.feature_count} features.`,
    })

    addFeatureForm.value = {
      layer_id: 0
    }
    addFeatureDialog.value = false
  } catch (error) {
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: error.response?.data?.detail || 'Failed to create layer.',
    })
    console.log(error)
  }
}
function addFeatureToLayerData(layerId, newFeature) {
  const targetLayer = user_layer_data.value.find(item => item.layer?.id == layerId)

  if (targetLayer) {
    newFeature.forEach(feat => {
      targetLayer.features.push(feat)
    })
  } else {
    user_layer_data.value.push({
      layer: { id: layerId }, // hoặc layer đầy đủ
      features: [newFeature]
    })
  }
}
watchEffect(() => {
  if (!DefaultlayerStates.value || !UserlayerStates.value) return
  const defaultactiveLayerIds = Object.entries(DefaultlayerStates.value)
    .filter(([_, value]) => value)
    .map(([key]) => parseInt(key))

  for (const layerId of defaultactiveLayerIds) {
    if (showAllDefault.value[layerId] == undefined) {
      showAllDefault.value[layerId] = false
    }
  }
  const useractiveLayerIds = Object.entries(UserlayerStates.value)
    .filter(([_, value]) => value)
    .map(([key]) => parseInt(key))
  for (const layerId of useractiveLayerIds) {
    if (showAllUser.value[layerId] == undefined) {
      showAllUser.value[layerId] = false
    }
  }
})
const onDragEndDefault = () => {
  isDefaultOrderChanged.value = true;
  updatePrioritiesAndSaveToLocal();
};
const onDragEndUser = () => {
  isUserOrderChanged.value = true;
  updatePrioritiesAndSaveToLocal();
};
const updatePrioritiesAndSaveToLocal = () => {
  const totalDefault = draggableDefaultLayers.value.length;
  const defaultPriorities = draggableDefaultLayers.value.map((layer, index) => {
    layer.z_index = totalDefault - index; // Cập nhật z_index để hiển thị ngay
    return {
      isDefault: true,
      layer_id: layer.default_layer_id,
      priority: layer.z_index
    };
  });
  const originalZIndexes = draggableUserLayers.value
    .map(layer => layer.z_index)
    .sort((a, b) => b - a);
  draggableUserLayers.value.forEach((layer, index) => {
    layer.z_index = originalZIndexes[index]; // Gán lại z_index theo thứ tự
  });
  const userPriorities = draggableUserLayers.value.map((layer, index) => {
    return {
      isDefault: false,
      layer_id: layer.layer_id,
      priority: layer.z_index
    };
  });
const allNewPriorities = [...defaultPriorities, ...userPriorities];
  localStorage.setItem('tempLayerPriorities', JSON.stringify(allNewPriorities));
  console.log('Updated priorities and saved to localStorage:', allNewPriorities);
};
const saveNewOrder = async () => {
  const prioritiesToSave = JSON.parse(localStorage.getItem('tempLayerPriorities'));
  if (!prioritiesToSave) return;

  const requestBody = {
    updates: prioritiesToSave
  };

  try {
    const update_priority_response = await axios.patch(
      `http://localhost:8000/projects/${state.projectId}/update-layer-priorities`,
      requestBody,
      {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`
      }
      }
    );
    console.log(update_priority_response.data)
    update_priority(map.value, update_priority_response.data)
    // Sau khi thành công, reset trạng thái
    isDefaultOrderChanged.value = false;
    isUserOrderChanged.value = false;
    localStorage.removeItem('tempLayerPriorities');
    Swal.fire({
      icon: 'success',
      title: 'Success',
      text: `Priorities saved successfully!`,
    })

  } catch (error) {
    console.error("Failed to save priorities:", error.response?.data || error.message);
    Swal.fire({
      icon: 'error',
      title: 'Error',
      text: `Failed to save priorities. Please try again.`,
    })
  }
};
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const changeVersion = (layerId) => {
  contron_version_status.value = !contron_version_status.value
  const layers = map.value.getLayers().getArray()
  const vector_layers = layers.filter(layer => layer instanceof VectorLayer)
  const targetLayer = vector_layers
    .find(layer => layer.getProperties().default_layer_id == layerId)
  targetLayer.setVisible(false)
  const vectorSource = targetLayer.getSource()
  vectorSource.clear()
  if(contron_version_status.value){
    addFeaturetoDefaultVectorLayer({
        list_features: new_version_feature.value,
        target_source: vectorSource
      })
    targetLayer.setVisible(true)
  } else {
    const old_default_version_list_features = list_default_feature.value.filter(feature => feature.layer_id == 7)
    addFeaturetoDefaultVectorLayer({
        list_features: old_default_version_list_features,
        target_source: vectorSource
      })
    targetLayer.setVisible(true)
  }
  
}
const handleLayerChange = (checked, layerId) => {
  if (checked) {
    // Nếu trạng thái mới là "đã chọn" (true), thêm ID vào mảng
    Ltags.value.push(layerId);
  } else {
    // Nếu trạng thái mới là "bỏ chọn" (false), tìm và xóa ID khỏi mảng
    const index = Ltags.value.indexOf(layerId);
    if (index > -1) {
      Ltags.value.splice(index, 1);
    }
  }
};

const handleFeatureChange = (checked, layerId) => {
  if (checked) {
    // Nếu trạng thái mới là "đã chọn" (true), thêm ID vào mảng
    Ftags.value.push(layerId);
  } else {
    // Nếu trạng thái mới là "bỏ chọn" (false), tìm và xóa ID khỏi mảng
    const index = Ftags.value.indexOf(layerId);
    if (index > -1) {
      Ftags.value.splice(index, 1);
    }
  }
};
watch([defaultLayers, userLayers], ([newDefault, newUser]) => {
  // Sắp xếp và gán cho Default Layers
  draggableDefaultLayers.value = [...newDefault].sort((a, b) => b.z_index - a.z_index);
  console.log(draggableDefaultLayers.value)
  // Sắp xếp và gán cho User Layers
  draggableUserLayers.value = [...newUser].sort((a, b) => b.z_index - a.z_index);
  max_z_index.value = draggableUserLayers.value[0].z_index + 1

}, { deep: true });

watch(isSaving, (newValue) => {
  if (newValue) {
    const resetData = async() =>{
      await fetchUserVectorLayer()
    }
    resetData()
  } else {
    console.log("PARENT: Child component has finished saving.");
  }
});
watch(isUpdatePopup, (newVal) => {
  console.log(newVal)
  if(newVal){
    const resetData = async() => {
      await fetchUserFeatureInforms()
      isUpdatePopup.value = false
    }
  resetData()
  }
})
watch(selectedTitle, (newVal) => {
  if(newVal != 'All'){
    const featureIds = featureInforms.value
      .filter(inform => inform.title == newVal)
      .map(inform => inform.feature_id)
    const data = user_layer_data.value.flatMap(layerItem =>
      layerItem.features)
    filteredFeatures.value = data.filter(feature => featureIds.includes(feature.feature_id))
    console.log(filteredFeatures.value)
    filteredFeatures.value.forEach(item => {
      flashById(map.value, item.layer_id, item.feature_id)
    })
  }else{
    filteredFeatures.value = user_layer_data.value.flatMap(layerItem => layerItem.features)
    resetLayerStyles(map.value)
  }
  
})
watch(featureInforms, (newVal) => {
  console.log(newVal)
})
// Gọi hàm giải mã khi component được mounted
onMounted(async () => {
  decodeProjectId();
  await fetchDefaultVectorLayer();
  await fetchUserVectorLayer();
  await fetchUserFeatureInforms();
  await initMap();
  await displayData();
  const new_version_id = [8]
  const fetch_feature_for_new_version_response = await axios.post(
      'http://localhost:8000/default-features/by-layer-ids',
      new_version_id,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json',
        },
      }
  );
  console.log(fetch_feature_for_new_version_response.data)
  new_version_feature.value = fetch_feature_for_new_version_response.data    
  await fetchCommunityInforms();
});
</script>
<style>
.scrollbar-thin {
  scrollbar-width: thin;
}
.scrollbar-thin::-webkit-scrollbar {
  width: 8px;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background-color: #9ca3af;
  border-radius: 4px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background-color: #f3f4f6;
}
</style>