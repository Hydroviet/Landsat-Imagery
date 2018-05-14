import rasterio
import numpy as np
import matplotlib as mpl
import subprocess
from matplotlib import pyplot as plt
from rasterio.merge import merge
import geopandas as gpd
import os, math

import gdal, gdalconst, gdalnumeric
from gdal import FillNodata as FillWithMask


folder_ts = 'L7_Data/'
for root, dirs, _ in os.walk(folder_ts):
    break

c = 0
for dir in dirs:
    c += 1
    print('Processing {0}/{1}'.format(c, len(dirs)))
    
    folder = os.path.join(folder_ts, dir)
    if (not os.path.exists(os.path.join(folder, 'gap_mask'))):
        continue
    for _, __, files in os.walk(folder):
        break
    
    for file in files:
        raw_data = os.path.join(folder, file)
        mask_data = os.path.join(folder, 'gap_mask', file)
        
        print(' -> Fill {0} with {1}'.format(raw_data, mask_data), end='')
        
        try:
            raw_data = gdal.Open(raw_data, gdal.GA_Update)
            mask_data = gdal.Open(mask_data)

            source = raw_data.GetRasterBand(1)
            mask = mask_data.GetRasterBand(1)
            
            FillWithMask(source, mask, 100, 0)
            print (' --- DONE!')
        except:
            print (' --- ERROR!')
            pass
        
        raw_data = None
        mask_data = None
        source = None
        mask = None
