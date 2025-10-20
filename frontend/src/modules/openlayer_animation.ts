import { easeOut } from 'ol/easing'
import { unByKey } from 'ol/Observable'
import Style from 'ol/style/Style'
import CircleStyle from 'ol/style/Circle'
import Fill from 'ol/style/Fill'
import Stroke from 'ol/style/Stroke'
import VectorLayer from 'ol/layer/Vector'
import { getVectorContext } from 'ol/render';
import type { Feature } from 'ol'

export function flashById(map: any, layerId: number, featureId: number) {
  // Tìm layer có id tương ứng
  const layers = map.getLayers().getArray()
  const vector_layers = layers.filter( layer => layer instanceof VectorLayer )
  const targetLayer = vector_layers
    .find(layer => layer.getProperties().id == layerId)

  if (!targetLayer) {
    console.warn(`Layer với id ${layerId} không tìm thấy.`)
    return
  }

  // Tìm feature trong layer đó
  const source = targetLayer.getSource()
  if (!source || !source.getFeatures) {
    console.warn(`Layer với id ${layerId} không có nguồn hợp lệ.`)
    return
  }

  const features = source.getFeatures()
  features.forEach(f => f.setStyle(null))
  const targetFeature = features.find(f => f.getProperties().id == featureId)

  if (!targetFeature) {
    console.warn(`Feature với id ${featureId} không tìm thấy trong layer ${layerId}.`)
    return
  }
  if(targetFeature.getGeometry()?.getType() == 'Point'){
    targetFeature.setStyle(
      new Style({
        image: new CircleStyle({
          radius: 10,
          fill: new Fill({ color: 'yellow' }),
          stroke: new Stroke({ color: 'red', width: 2 }),
        }),
      })
    )
  } else{
    targetFeature.setStyle(
      new Style({
        fill: new Fill({ color: 'rgba(255, 0, 0, 0.3)' }),
        stroke: new Stroke({ color: 'red', width: 3 }),
      })
    )
  }
}

export function resetLayerStyles(map: any) {
  // Tìm layer có id tương ứng
  const layers = map.getLayers().getArray();
  const vector_layers = layers.filter(layer => layer instanceof VectorLayer);

  vector_layers.forEach(layer =>{
    const vectorSource = layer.getSource()
    const features = vectorSource.getFeatures();
    features.forEach(feature => feature.setStyle(null));
  })
  // Đặt style của tất cả features về null
  console.log(`Đã đặt style của tất cả features trong layer về null.`);
}