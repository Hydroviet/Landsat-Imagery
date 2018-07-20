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

vn_reservoirs_path = 'vnreservoirs/VN_Reservoirs.shp'
df = gpd.read_file(vn_reservoirs_path)
plt.rcParams['figure.figsize'] = 7, 7
ho_tri_an = df[df.AREA_SKM == 277.4]

import json

def removeCloudFromQABand(rawData, qaData):
    returnValue = np.asarray(rawData)
    returnValue[np.asarray(qaData) != 0] = -1
    return returnValue

for root, dir, filenames in os.walk('Landsat8/'):
    break

c = 0
for folder in dir:
    geotiffPath = os.path.join('Landsat8', folder)
    c += 1
    print('[{1}/{2}] Working on {0}... '.format(geotiffPath, c, len(dir)), end='')

    try:
        NDWI = rasterio.open(os.path.join(geotiffPath, 'TriAn_' + folder.split('_')[3] + '.TIF'))
                
        ndwi = NDWI.read(1)
        original_transform = NDWI.transform
        
        # qaBand = rasterio.open(os.path.join(geotiffPath, 'TriAn_' + folder.split('_')[3] + '_BQA.TIF'))
        # ndwi = removeCloudFromQABand(ndwi, qaBand.read(1))     
        
        area, water_body = getWaterBody(ndwi, 'NDWI')

        if (area > 0):
            water_body = normalizePixelOnBoundaries(water_body)
            water_body_boundaries = find_boundaries(water_body, mode='outer', background=100).astype(np.int16)

            __shape, lShape = getMostSimilarShape(water_body_boundaries, original_transform, 
                                                  ho_tri_an.to_crs(NDWI.crs))

            new_shape_in_original_coordinates = [transform_geom(NDWI.crs, df.crs, mapping(__shape))]
            new_shape = shape(new_shape_in_original_coordinates[0])

            from shapely.wkt import dump as DumpPolygon, load as LoadPolygon

            wkt_path = os.path.join(geotiffPath, 'TriAn_' + folder.split('_')[3] + '_shape.wkt')
            DumpPolygon(new_shape, open(wkt_path, 'w'))
        
        _area = area * 900 / (1e6)
        data = json.dumps({
            'date': folder,
            'area': str(_area)
        })
        print(' --> OK. Area: {0}'.format(_area))

        NDWI.close()
        del ndwi
        del water_body
        
    except Exception as e:
        print(' --> ERROR: ' + str(e))