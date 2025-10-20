import Map from 'ol/Map';
import View from 'ol/View';
import VectorLayer from 'ol/layer/Vector';
import VectorSource from 'ol/source/Vector';
import Feature from 'ol/Feature';
import { Style, Fill, Stroke } from 'ol/style';
import XYZ from 'ol/source/XYZ';
import { fromLonLat } from 'ol/proj';
import TileLayer from 'ol/layer/Tile';
import GeoJSON from 'ol/format/GeoJSON';
import { Geometry } from 'ol/geom'
import { PawPrint } from 'lucide-vue-next';
import { getCenter } from 'ol/extent'
import Circle from 'ol/style/Circle';
// Hàm tạo một map rỗng (không có layer)
export function createMap(targetElement: string, options: {
  center?: [number, number]; // Kinh độ, vĩ độ
  zoom?: number;
} = {}) {
  // Thiết lập giá trị mặc định
  const defaultCenter = options.center ? fromLonLat(options.center) : fromLonLat([0, 0]);
  const defaultZoom = options.zoom ?? 2;

  // Tạo map rỗng
  const map = new Map({
    target: targetElement,
    layers: [], // Không có layer
    view: new View({
      center: defaultCenter,
      zoom: defaultZoom,
    }),
    controls: []
  });

  return map;
}

// Hàm tạo vector layer
export function createDefaultVectorLayer(options: {
  list_features: Feature[];
  fill: string; // Màu nền (hex, rgb, v.v.)
  stroke: string; // Màu viền
  stroke_width: number; // Độ dày viền
  z_index: number; // Thứ tự hiển thị
  layer_id: number;
}) {
  const geojsonFeatures = options.list_features.map(feature => ({
    type: 'Feature',
    geometry: JSON.parse(feature.geometry), // Parse chuỗi geometry thành object
    properties: {
      type: 'default_feature',
      id: feature.id,
      layer_id: feature.layer_id,
      CC_1: feature.CC_1,
      COUNTRY: feature.COUNTRY,
      ENGTYPE_1: feature.ENGTYPE_1,
      GID_0: feature.GID_0,
      GID_1: feature.GID_1,
      HASC_1: feature.HASC_1,
      ISO_1: feature.ISO_1,
      NAME_1: feature.NAME_1,
      NL_NAME_1: feature.NL_NAME_1,
      TYPE_1: feature.TYPE_1,
      VARNAME_1: feature.VARNAME_1,
    },
  }));
  const geojson = {
    type: 'FeatureCollection',
    features: geojsonFeatures,
  };

  // Đọc features từ GeoJSON
  const olFeatures = new GeoJSON().readFeatures(geojson, {
    dataProjection: 'EPSG:4326',
    featureProjection: 'EPSG:3857',
  });
  // Tạo vector source từ danh sách features
  const vectorSource = new VectorSource({
    features: olFeatures,
  });
  // Tạo style cho layer
  const layerStyle = new Style({
    fill: options.fill ? new Fill({ color: options.fill }) : undefined,
    stroke: options.stroke ? new Stroke({ color: options.stroke, width: options.stroke_width ?? 1 }) : undefined,
  });

  // Tạo vector layer
  const vectorLayer = new VectorLayer({
    source: vectorSource,
    style: layerStyle,
    visible: true,
    properties: {
      default_layer_id: options.layer_id
    }
  });

  // Thiết lập z-index nếu có
  if (options.z_index !== undefined) {
    vectorLayer.setZIndex(options.z_index);
  }
  return vectorLayer;
}
export const createUserVectorLayer = (layerData: any, featuresData: any[]) => {
  const layerStyle = new Style({
    fill: new Fill({
      color: layerData.fill
    }),
    stroke: new Stroke({
      color: layerData.stroke,
      width: layerData.stroke_width || 1.0, // Mặc định nếu không có
    }),
  });
  if (featuresData.length == 0) {
    const vectorSource = new VectorSource({
      features: [],
    });
    const vectorLayer = new VectorLayer({
      source: vectorSource,
      style: layerStyle,
      visible: true,
      properties: {
        name: layerData.name,
        id: layerData.id,
      },
    });
    vectorLayer.setZIndex(layerData.z_index)
    return vectorLayer;
  }
  const geojsonFeatures = Array.isArray(featuresData)
    ? featuresData.map((feature, index) => {
      // Kiểm tra tính hợp lệ của feature
      if (!feature || !feature.geom || !feature.geom.type || !feature.geom.coordinates) {
        console.warn(`Invalid feature at index ${index}:`, feature);
        return null;
      }
      return {
        type: 'Feature',
        properties: {
          id: feature.feature_id,
          name: feature.name || 'Unnamed', // Mặc định nếu không có
          properties: feature.properties || {}, // Lưu properties nếu có
          layer_id: feature.layer_id
        },
        geometry: {
          type: feature.geom.type,
          coordinates: feature.geom.coordinates,
        },
      };
    }).filter(feature => feature !== null) // Loại bỏ feature không hợp lệ
    : [];
  const geojson = {
    type: 'FeatureCollection',
    features: geojsonFeatures,
  };
  // Đọc features từ GeoJSON
  const olFeatures = new GeoJSON().readFeatures(geojson, {
    dataProjection: 'EPSG:4326',
    featureProjection: 'EPSG:3857',
  });
    olFeatures.forEach(feat =>{
    if(feat.getGeometry()?.getType() == 'Point'){
      feat.setStyle(
        new Style({
          image: new Circle({
            radius: 6,
            fill: new Fill({
              color: '#FF0000',
            }),
            stroke: new Stroke({
              color: '#1F2937',
              width: 1,
            }),
          }),
        })
      )
    }
  })
  const vectorSource = new VectorSource({
    features: olFeatures,
  });

  // Tạo vector layer
  const vectorLayer = new VectorLayer({
    source: vectorSource,
    style: layerStyle,
    visible: false,
    properties: {
      name: layerData.name,
      id: layerData.id,
    },
  });
  vectorLayer.setZIndex(layerData.priority)
  return vectorLayer;
};
const default_base_layer = [
  { "id": 1, "src": "https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}&key=AIzaSyAA8Nlt2SS2UwcEa4IAGYWlujC4C34mMf0", "label": "Google Map" },
  { "id": 2, "src": "https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoicHBodWNqcyIsImEiOiJjbTV5emdvNWUwbjhhMmpweXAybThmbmVhIn0.4PA9RDEf2HFu7jMuicJ1OQ", "label": "Mapbox" },
  { "id": 3, "src": "https://{a-d}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png", "label": "CartoDB" },
  { "id": 4, "src": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", "label": "Esri" },
  { "id": 5, "src": "https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.jpg", "label": "Stamen" }
]

export function createDefaultTileLayer(base_layer: string): TileLayer[] {
  // Cắt chuỗi và chuyển thành mảng số
  const layerIds = base_layer
    .split('-')
    .map(id => parseInt(id, 10))
    .filter(id => !isNaN(id)); // Lọc bỏ các giá trị không phải số

  // Tạo danh sách tile layer dựa trên layerIds
  const tileLayers: TileLayer[] = layerIds
    .map(id => {
      // Tìm base layer tương ứng trong default_base_layer
      const baseLayer = default_base_layer.find(layer => layer.id == id);
      if (!baseLayer) {
        console.warn(`Không tìm thấy base layer với id ${id}`);
        return null;
      }

      // Tạo tile layer với nguồn XYZ
      return new TileLayer({
        source: new XYZ({
          url: baseLayer.src,
          attributions: baseLayer.label, // Gán label làm attribution
        }),
        visible: false,
        properties: {
          label: baseLayer.label,
          layer_id: baseLayer.id
        }, // Lưu label vào properties
      });
    })
    .filter((layer): layer is TileLayer => layer !== null); // Lọc bỏ các layer null
  return tileLayers;
}

export function updateColorDefaultVectorLayer(map:any , fill:string, stroke:string, layer_id:any){
  const layers = map.getLayers().getArray();
  const vector_layers = layers.filter( layer => layer instanceof VectorLayer )
  const targetLayer = vector_layers
    .find(layer => layer.getProperties().default_layer_id == layer_id)
  map.removeLayer(targetLayer)
  const layerStyle = new Style({
    fill: fill ? new Fill({ color: fill }) : undefined,
    stroke: stroke ? new Stroke({ color: stroke, width: 1 }) : undefined,
  });
  targetLayer.setStyle(layerStyle)
  map.addLayer(targetLayer)
}

export function updateColorUserVectorLayer(map:any , fill:string, stroke:string, layer_id:any){
  const layers = map.getLayers().getArray();
  const vector_layers = layers.filter( layer => layer instanceof VectorLayer )
  const targetLayer = vector_layers
    .find(layer => layer.getProperties().id == layer_id)
  map.removeLayer(targetLayer)
  const layerStyle = new Style({
    fill: fill ? new Fill({ color: fill }) : undefined,
    stroke: stroke ? new Stroke({ color: stroke, width: 1 }) : undefined,
  });
  targetLayer.setStyle(layerStyle)
  map.addLayer(targetLayer)
}

export function deleteDefaultVectorLayer(map: any, layer_id:any){
  const layers = map.getLayers().getArray();
  const vector_layers = layers.filter( layer => layer instanceof VectorLayer )
  const targetLayer = vector_layers
    .find(layer => layer.getProperties().default_layer_id == layer_id)
  map.removeLayer(targetLayer)
}

export function deleteUserVectorLayer(map: any, layer_id:any){
  const layers = map.getLayers().getArray();
  const vector_layers = layers.filter( layer => layer instanceof VectorLayer )
  const targetLayer = vector_layers
    .find(layer => layer.getProperties().id == layer_id)
  map.removeLayer(targetLayer)
}

export function addFeaturetoUserLayer(map:any, layer_id:any, featuresData: Feature[]){
  console.log(featuresData)
    const geojsonFeatures = Array.isArray(featuresData)
    ? featuresData.map((feature, index) => {
      // Kiểm tra tính hợp lệ của feature
      if (!feature || !feature.geom || !feature.geom.type || !feature.geom.coordinates) {
        console.warn(`Invalid feature at index ${index}:`, feature);
        return null;
      }
      return {
        type: 'Feature',
        properties: {
          id: feature.feature_id,
          name: feature.name || 'Unnamed', // Mặc định nếu không có
          properties: feature.properties || {}, // Lưu properties nếu có
          layer_id: feature.layer_id
        },
        geometry: {
          type: feature.geom.type,
          coordinates: feature.geom.coordinates,
        },
      };
    }).filter(feature => feature !== null) // Loại bỏ feature không hợp lệ
    : [];
  const geojson = {
    type: 'FeatureCollection',
    features: geojsonFeatures,
  };
  // Đọc features từ GeoJSON
  const olFeatures = new GeoJSON().readFeatures(geojson, {
    dataProjection: 'EPSG:4326',
    featureProjection: 'EPSG:3857',
  });
  olFeatures.forEach(feat =>{
    if(feat.getGeometry()?.getType() == 'Point'){
      feat.setStyle(
        new Style({
          image: new Circle({
            radius: 6,
            fill: new Fill({
              color: '#FF0000',
            }),
            stroke: new Stroke({
              color: '#1F2937',
              width: 1,
            }),
          }),
        })
      )
    }
  })
  const layers = map.getLayers().getArray();
  const vector_layers = layers.filter( layer => layer instanceof VectorLayer )
  const targetLayer = vector_layers
    .find(layer => layer.getProperties().id == layer_id)
  console.log(layer_id)
  vector_layers.forEach(layer =>{
    console.log(layer.getProperties().id)
  })
  const targetSource = targetLayer.getSource()
  targetSource.addFeatures(olFeatures)
}
export function addFeaturetoDefaultVectorLayer(options: {
  list_features: Feature[];
  target_source: any;
}) {
  const geojsonFeatures = options.list_features.map(feature => ({
    type: 'Feature',
    geometry: JSON.parse(feature.geometry), // Parse chuỗi geometry thành object
    properties: {
      type: 'default_feature',
      id: feature.id,
      layer_id: feature.layer_id,
      CC_1: feature.CC_1,
      COUNTRY: feature.COUNTRY,
      ENGTYPE_1: feature.ENGTYPE_1,
      GID_0: feature.GID_0,
      GID_1: feature.GID_1,
      HASC_1: feature.HASC_1,
      ISO_1: feature.ISO_1,
      NAME_1: feature.NAME_1,
      NL_NAME_1: feature.NL_NAME_1,
      TYPE_1: feature.TYPE_1,
      VARNAME_1: feature.VARNAME_1,
    },
  }));
  const geojson = {
    type: 'FeatureCollection',
    features: geojsonFeatures,
  };

  // Đọc features từ GeoJSON
  const olFeatures = new GeoJSON().readFeatures(geojson, {
    dataProjection: 'EPSG:4326',
    featureProjection: 'EPSG:3857',
  });
  // Tạo vector source từ danh sách features
  options.target_source.addFeatures(olFeatures)
}
export function deleteUserFeature(map:any, layer_id:any, feature_id:any){
  const layers = map.getLayers().getArray();
  const vector_layers = layers.filter( layer => layer instanceof VectorLayer )
  const targetLayer = vector_layers
    .find(layer => layer.getProperties().id == layer_id)
  const targetSource = targetLayer.getSource()
  const features = targetSource.getFeatures()
  const featureToRemove = features.find(f => f.getProperties().id == feature_id)
  targetSource.removeFeature(featureToRemove)
}

export function update_priority(map:any, data:any){
  const layers = map.getLayers().getArray();
  const vector_layers = layers.filter( layer => layer instanceof VectorLayer )
  data.forEach(element => {
    if(element.isDefault){
      const targetLayer = vector_layers.find(layer => layer.getProperties().default_layer_id == element.layer_id)
      targetLayer.setZIndex(element.z_index)
    } else {
      const targetLayer = vector_layers.find(layer => layer.getProperties().id == element.layer_id)
      targetLayer.setZIndex(element.z_index)
    }
  });
}

export function zoom_to_Feature(map:any, Feature:any){
  const geometry = Feature.getGeometry()
  const extent = geometry.getExtent()
  const center = getCenter(extent)

  // Thiết lập center bản đồ
  map.getView().setCenter(center)
}