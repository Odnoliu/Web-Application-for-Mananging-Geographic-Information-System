import geopandas as gpd
from zipfile import ZipFile
from io import BytesIO
from pykml import parser as kml_parser
from shapely.geometry import Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon, shape
import json
import os
import tempfile
import shutil
from geojson import loads as geojson_loads

def process_json(file_like):
    geojson_data = geojson_loads(file_like.read().decode('utf-8'))
    features = []
    if 'features' in geojson_data:
        for feature in geojson_data['features']:
            geom = shape(feature['geometry'])
            properties = feature.get('properties', {})
            features.append({
                'geometry': geom,
                'properties': properties
            })
    return features

def process_kmz(file_like):
    with ZipFile(BytesIO(file_like.read())) as kmz:
        kml_file = [f for f in kmz.namelist() if f.endswith('.kml')][0]
        with kmz.open(kml_file) as kml:
            kml_content = kml.read()
            root = kml_parser.fromstring(kml_content)
            features = []
            if hasattr(root, 'Document'):
                for element in root.Document.getchildren():
                    if element.tag.endswith('Placemark'):
                        feature = process_placemark(element)
                        if feature['geometry']:
                            features.append(feature)
                    elif element.tag.endswith('Folder'):
                        process_folder(element, features)
            else:
                for element in root.getchildren():
                    if element.tag.endswith('Placemark'):
                        feature = process_placemark(element)
                        if feature['geometry']:
                            features.append(feature)
                    elif element.tag.endswith('Folder'):
                        process_folder(element, features)
            return features

def process_placemark(placemark):
    properties = {'name': str(placemark.name)} if hasattr(placemark, 'name') else {}
    geometry = None
    if hasattr(placemark, 'Point'):
        coords = parse_coordinates(placemark.Point.coordinates.text)
        geometry = Point(coords[0])
    elif hasattr(placemark, 'LineString'):
        coords = parse_coordinates(placemark.LineString.coordinates.text)
        geometry = LineString(coords)
    elif hasattr(placemark, 'Polygon'):
        if hasattr(placemark.Polygon, 'outerBoundaryIs') and hasattr(placemark.Polygon.outerBoundaryIs, 'LinearRing'):
            outer_coords = parse_coordinates(placemark.Polygon.outerBoundaryIs.LinearRing.coordinates.text)
            geometry = Polygon(outer_coords)
    elif hasattr(placemark, 'MultiGeometry'):
        geometries = []
        for geom in placemark.MultiGeometry.getchildren():
            geom_tag = geom.tag.split('}')[-1]
            if geom_tag == 'Point':
                coords = parse_coordinates(geom.coordinates.text)
                geometries.append(Point(coords[0]))
            elif geom_tag == 'LineString':
                coords = parse_coordinates(geom.coordinates.text)
                geometries.append(LineString(coords))
            elif geom_tag == 'Polygon':
                if hasattr(geom, 'outerBoundaryIs') and hasattr(geom.outerBoundaryIs, 'LinearRing'):
                    outer_coords = parse_coordinates(geom.outerBoundaryIs.LinearRing.coordinates.text)
                    geometries.append(Polygon(outer_coords))
        if geometries:
            if all(isinstance(g, Point) for g in geometries):
                geometry = MultiPoint(geometries)
            elif all(isinstance(g, LineString) for g in geometries):
                geometry = MultiLineString(geometries)
            elif all(isinstance(g, Polygon) for g in geometries):
                geometry = MultiPolygon(geometries)
    return {'geometry': geometry, 'properties': properties}

def parse_coordinates(coord_str):
    coords = []
    for coord in coord_str.strip().split():
        lon, lat = map(float, coord.split(',')[:2])
        coords.append((lon, lat))
    return coords

def process_folder(folder, features):
    for element in folder.getchildren():
        if element.tag.endswith('Placemark'):
            feature = process_placemark(element)
            if feature['geometry']:
                features.append(feature)
        elif element.tag.endswith('Folder'):
            process_folder(element, features)

def process_gpkg(file_like):
    gdf = gpd.read_file(BytesIO(file_like.read()), driver='GPKG')
    features = []
    for _, row in gdf.iterrows():
        feature = {
            'geometry': row['geometry'],
            'properties': row.drop('geometry').to_dict()
        }
        features.append(feature)
    return features

def process_zip(file_like):
    with ZipFile(BytesIO(file_like.read())) as zip_ref:
        shp_file = [f for f in zip_ref.namelist() if f.endswith('.shp')][0]
        temp_dir = tempfile.mkdtemp()
        try:
            zip_ref.extractall(temp_dir)
            shp_path = os.path.join(temp_dir, shp_file)
            gdf = gpd.read_file(shp_path, driver='ESRI Shapefile')
            features = []
            for _, row in gdf.iterrows():
                feature = {
                    'geometry': row['geometry'],
                    'properties': row.drop('geometry').to_dict()
                }
                features.append(feature)
            return features
        finally:
            shutil.rmtree(temp_dir)