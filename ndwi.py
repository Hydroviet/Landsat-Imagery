import rasterio
import numpy as np
import matplotlib as mpl
import subprocess
from matplotlib import pyplot
import geopandas as gpd

import os, math

for root, dir, filenames in os.walk('L7_Data/'):
	break


print('Processing NDWI... ')
for folder in dir:
  path = os.path.join('L7_Data', folder)
  listFile = [path + '/B5.TIF',
             path + '/B3.TIF']
  
  try:
  	bandNIR, bandGreen = (rasterio.open(f) for f in listFile)
  	meta = bandNIR.meta
  	meta['dtype'] = 'float32'
  	bandNIR = bandNIR.read(1)
  	bandGreen = bandGreen.read(1)
  	NDWI = np.zeros(rasterio.open(listFile[0]).shape, dtype=rasterio.float32)
  	for i in range(NDWI.shape[0]):
  		for j in range(NDWI.shape[1]):
  			nir = bandNIR[i,j].astype(float)
  			green = bandGreen[i,j].astype(float)
  			if (green + nir != 0):
  				NDWI[i,j] = (green - nir) / (green + nir)
  			else:
  				NDWI[i,j] = -1
  	with rasterio.open(path + '/NDWI.TIF', 'w', **meta) as dst:
  		dst.write(NDWI, 1)
  	print("[NDWI] Processing %s - DONE" % path)
  except:
  	print("[NDWI] Processing %s - ERROR" % path)


print('Processing NDWI2... ')


for root, dir, filenames in os.walk('L7_Data/'):
	break
for folder in dir:
  path = os.path.join('L7_Data', folder)
  listFile = [path + '/B6_VCID_2.TIF',
             path + '/B3.TIF']
  
  try:
  	bandSWIR, bandGreen = (rasterio.open(f) for f in listFile)
  	meta = bandSWIR.meta
  	meta['dtype'] = 'float32'
  	bandSWIR = bandSWIR.read(1)
  	bandGreen = bandGreen.read(1)
  	NDWI2 = np.zeros(rasterio.open(listFile[0]).shape, dtype=rasterio.float32)
  	for i in range(NDWI2.shape[0]):
  		for j in range(NDWI2.shape[1]):
  			swir = bandSWIR[i,j].astype(float)
  			green = bandGreen[i,j].astype(float)
  			if (green + swir != 0):
  				NDWI2[i,j] = (green - swir) / (green + swir)
  			else:
  				NDWI2[i,j] = -1
  	with rasterio.open(path + '/NDWI2.TIF', 'w', **meta) as dst:
  		dst.write(NDWI2, 1)
  	print("[NDWI2] Processing %s - DONE" % path)
  except:
  	print("[NDWI2] Processing %s - ERROR" % path)

print('Processing NDWI3... ')

for root, dir, filenames in os.walk('L7_Data/'):
	break
for folder in dir:
  path = os.path.join('L7_Data', folder)
  listFile = [path + '/B7.TIF',
             path + '/B3.TIF']
  try:
    bandSWIR, bandGreen = (rasterio.open(f) for f in listFile)
    
    meta = bandSWIR.meta
    meta['dtype'] = 'float32'
    
    bandSWIR = bandSWIR.read(1)
    bandGreen = bandGreen.read(1)

    NDWI3 = np.zeros(rasterio.open(listFile[0]).shape, dtype=rasterio.float32)
    for i in range(NDWI3.shape[0]):
    	for j in range(NDWI3.shape[1]):
    		swir = bandSWIR[i,j].astype(float)
    		green = bandGreen[i,j].astype(float)
    		if (green + swir != 0):
    			NDWI3[i,j] = (green - swir) / (green + swir)
    		else:
    			NDWI3[i,j] = -1
    with rasterio.open(path + '/NDWI3.TIF', 'w', **meta) as dst:
    	dst.write(NDWI3, 1)
    print("[NDWI3] Processing %s - DONE" % path)
  except:
  	print("[NDWI3] Processing %s - ERROR" % path)