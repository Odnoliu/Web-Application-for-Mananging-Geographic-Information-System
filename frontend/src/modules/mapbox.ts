import mapboxgl from 'mapbox-gl';

mapboxgl.accessToken = 'pk.eyJ1IjoicHBodWNqcyIsImEiOiJjbTV5emdvNWUwbjhhMmpweXAybThmbmVhIn0.4PA9RDEf2HFu7jMuicJ1OQ';

export function createMap(container: HTMLElement, options: Partial<mapboxgl.MapboxOptions> = {}) {
  const map = new mapboxgl.Map({
    container: container,
    style: 'mapbox://styles/mapbox/streets-v12',
    ...options,
  });

  return map;
}

export function addMarker(
  map: mapboxgl.Map,
  lng: number,
  lat: number,
  layerName: string,
  popupText?: string,
) {
  const popup = popupText ? new mapboxgl.Popup().setText(popupText) : undefined;

  // Load icon image
  map.loadImage('icon/point.png', (error, image) => {
    if (error) throw error;
    if (image) {
      map.addImage(`${layerName}_icon`, image);
      
      // Add source
      map.addSource(layerName, {
        type: 'geojson',
        data: {
          type: 'FeatureCollection',
          features: [
            {
              type: 'Feature',
              geometry: {
                type: 'Point',
                coordinates: [lng, lat],
              },
              properties: {},
            },
          ],
        },
      });

      // Add layer
      map.addLayer({
        id: layerName,
        type: 'symbol',
        source: layerName,
        layout: {
          'icon-image': `${layerName}_icon`,
          'icon-size': 0.05,
          'icon-allow-overlap': true,
        },
      });

      // Add popup if exists
      if (popup) {
        new mapboxgl.Popup()
          .setLngLat([lng, lat])
          .setText(popupText!)
          .addTo(map);
      }
    }
  });
}

export async function addUserPosition(map: mapboxgl.Map, lng: number, lat: number) {
  const layerName = 'user_position';
  const popupContent = `<div class="rounded-lg max-w-xs text-gray-800 text-sm font-medium">You are here!</div>`;
  const popup = new mapboxgl.Popup({ closeButton: false, closeOnClick: true });

  // Load icon image
  map.on('load', async() => {
      await new Promise<void>((resolve, reject) => {
      map.loadImage('/icons/user.png', (error, image) => {
        if (error || !image) {
          console.error('Không thể load icon landscape.png:', error);
          reject(error);
          return;
        }
        if (!map.hasImage('user')) {
          map.addImage('user', image);
        }
        resolve();
      });
    });
      map.addSource(layerName, {
    type: 'geojson',
    data: {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          geometry: {
            type: 'Point',
            coordinates: [lng, lat],
          },
          properties: {},
        },
      ],
    },
  });

  // Add layer
  map.addLayer({
    id: layerName,
    type: 'symbol',
    source: layerName,
    layout: {
      'icon-image': `user`,
      'icon-size': 0.07,
      'icon-allow-overlap': true,
    },
  });

  // Add popup
  popup.setLngLat([lng, lat])
  .setHTML(popupContent)
  .addTo(map);
  })

}