import rasterio
import numpy as np
import matplotlib as mpl
import subprocess
from matplotlib import pyplot
import geopandas as gpd
import os, math
from matplotlib import pyplot as plt
from utils.landsatHepers import *
from shapely.wkt import dump as DumpPolygon, load as LoadPolygon

vn_reservoirs_path = 'VN_Reservoirs.shp'
df = gpd.read_file(vn_reservoirs_path)
plt.rcParams['figure.figsize'] = 5, 5
ho_tri_an = df[df.AREA_SKM == 277.4]

import json

for root, dir, filenames in os.walk('L7_Data/'):
  break

print('Creating WKT for each data point...')


c = 0
for folder in dir:
  geotiffPath = os.path.join('L7_Data', folder)
  c += 1
  print('[{1}/{2}] Working on {0}... '.format(geotiffPath, c, len(dir)), end='')

  try:
    NDWI = rasterio.open(geotiffPath + '/NDWI3.TIF')

    ndwi, original_transform = getMaskFromShape(ho_tri_an, NDWI, eps=2000)
    area, segment_array = countPixel(ndwi, 'NDWI3', [600, 600])


    segment_array = normalizePixelOnBoundaries(segment_array)
    boundaries_array = findBoundariesFromSegmentedArray(segment_array)

    __shape = getMostSimilarShape(boundaries_array, original_transform, ho_tri_an)

    new_shape_in_original_coordinates = [transform_geom(NDWI.crs, df.crs, mapping(__shape))]
    new_shape = shape(new_shape_in_original_coordinates[0])

    from shapely.wkt import dump as DumpPolygon, load as LoadPolygon

    wkt_path = os.path.join(geotiffPath, 'shape.wkt')
    DumpPolygon(new_shape, open(wkt_path, 'w'))

    _area = area * 900 / 1000000

    data = json.dumps({
        'date': folder,
        'area': str(_area)
    })
    json_path = os.path.join(geotiffPath, 'info.json')
    json.dump(json.loads(data), open(json_path, 'w'), ensure_ascii=False, indent=4)
    print(' --> OK')
    
  except Exception as e:
    print(' --> ERROR: ' + str(e))


