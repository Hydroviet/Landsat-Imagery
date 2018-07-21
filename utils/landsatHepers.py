import rasterio
import numpy as np

from rasterio.warp import transform_geom

import rasterio.mask

from shapely.geometry import shape, mapping
from queue import Queue

from skimage.segmentation import find_boundaries


def getMaskFromShape(geopandasData, rasterData, eps=4000):
    """
    Get mask in Rectangle Size and transforming Information
    :type geopandasData: geopandas.geodataframe.GeoDataFrame
    :type rasterData: rasterio._io.RasterReader
    :type eps: int

    :param geopandasData: geopandasData from Shapefile
    :param rasterData: rasterIO reader from geotiff File
    :param eps: How much it would be stretch to outside

    :return: Raster Data Masked, Transforming informations
    """

    # Transform to rasterCRS
    shape = geopandasData.geometry.values[0]
    geom = mapping(shape)
    shape = [transform_geom(geopandasData.crs, rasterData.crs, geom)]

    # Find boundaries of rectangle
    inf = int(1234567890)
    x0, y0, x1, y1 = [inf, -inf, -inf, inf]  # top-left, bottom-right
    for x, y in shape[0]['coordinates'][0]:
        x0 = min(x0, x)
        x1 = max(x1, x)
        y0 = max(y0, y)
        y1 = min(y1, y)
    newCoordinates = [{'type': 'Polygon', 'coordinates': [[(x0 - eps, y0 + eps), (x1 + eps, y0 + eps),
                                                            (x1 + eps, y1 - eps), (x0 - eps, y1 - eps)]]}]
    newRasterData, original_transform = rasterio.mask.mask(rasterData, newCoordinates, crop=True)
    return newRasterData.squeeze(), original_transform


def insideMatrix(x, y, m, n):
    """
    Check if (x, y) is in[0,0 .. m,n]
    :param x: x-coordinate
    :param y: y-coordinate
    :param m: m-size
    :param n: n-size
    :return: True if (x, y) in range, else False
    """
    if x < 0 or x >= m or y < 0 or y >= n:
        return False
    return True


def checkExpansion(val, typeOfMap):
    """
    Check Expansion conditions. Currently supported: NDVI ( < 0); NDWI (> 0.15) ; NDWI2 (> 0.3)
    :param val: value of pixel
    :param typeOfMap: type of Geotiff Data
    :return: True if it could be expanded
    """
    if (typeOfMap == 'NDVI'):
        if (val < 0):
            return True;
        return False;
    if (typeOfMap == 'NDWI'):
        if (val > 0):
            return True;
        return False;
    if (typeOfMap == 'NDWI2'):
        if (val > 0.3):
            return True;
        return False;
    if (typeOfMap == 'NDWI3'):
        if (val > 0.32):
            return True;
        return False;
    return False;


def findWaterBody(obj, typeOfMap, startingPoint, visited, iWaterBody):
    """
    BFS from :startingPoint: that belongs to object to be masked.
    :param obj: Numpy Array of Data
    :param typeOfMap: type of Geotiff Data
    :param startingPoint: Central of Object to be masked
    :return: Number of pixels belong to object, Object masked
    """
    dx = [0,1,0,-1]
    dy = [1,0,-1,0]

    final_obj= np.zeros((obj.shape[0], obj.shape[1])).astype(np.uint8)
    u0, v0 = startingPoint[0], startingPoint[1]

    q = Queue()
    q.put((u0, v0))
    countPixel = 0

    while not q.empty():
        u, v = q.get()
        final_obj[u, v] = 1
        countPixel += 1
        for k in range(4):
            _u, _v = u + dx[k], v + dy[k]
            if not insideMatrix(_u, _v, obj.shape[0], obj.shape[1]):
                continue
            if (visited[_u, _v]):
                continue
            if checkExpansion(obj[_u, _v], typeOfMap):
                visited[_u, _v] = True
                q.put((_u, _v))
    return countPixel, final_obj


def getWaterBody(ar, typeOfMap):
    """
    Get the most largest water body over an array with related type of map
    :type array: np.array
    :param ar: Numpy Array of Data
    :param typeOfMap: type of Geotiff Data
    :return: Number of pixels belongs to the largest water body (assuming as reservoir), largest water body masked
    """
    lWaterBodyMask = []
    lWaterBodyArea = []
    iWaterBody = 0

    visited = np.zeros((ar.shape[0], ar.shape[1])).astype(np.uint8)

    for i in range(ar.shape[0]):
        for j in range(ar.shape[1]):
            if (visited[i,j] == 0) and (checkExpansion(ar[i,j], typeOfMap)):
                iWaterBody += 1
                area, mask = findWaterBody(ar, typeOfMap, [i, j], visited, iWaterBody)
                lWaterBodyArea.append(area)
                lWaterBodyMask.append([i, j])
    
    if (len(lWaterBodyArea) > 0):
        index = np.argmax(lWaterBodyArea)
        visited = np.zeros((ar.shape[0], ar.shape[1])).astype(np.uint8)
        area, mask = findWaterBody(ar, typeOfMap, lWaterBodyMask[index], visited, index - 1)
        return area, mask
    else:
        return 0, []


def normalizePixelOnBoundaries(array, eps=5):
    """
    Delete all Pixel that could be make Shaping wrongs (Set to 0)
    :type array: np.array
    :param array: array of masked data
    :param eps: how long to be delete from boundaries
    :return: normalized array
    """

    array[:eps][:] = 0
    array[array.shape[0] - eps:][:] = 0
    array[:][:eps] = 0
    array[:][array.shape[1] - eps:] = 0
    return array


def findBoundariesFromSegmentedArray(segmentedArray):
    """
    Returns Boundaries contains boundaries from segmented Array
    :param segmentedArray: np.array
    :return: Boundaries Array
    """
    boundariesArray = find_boundaries(segmentedArray, connectivity=1, mode='outer', background=100).astype(np.int16)
    return boundariesArray.astype(np.int16)


def getMostSimilarShape(boundariesArray, originalTransform, geopandasData):
    """
    Returns the most similar Shape to orginal geom, after using features.shape from RasterIO
    Assumes that our boundariesArray always not as well as smooth-geom from original shapefile
    :param boundariesArray: np.array
    :param originalTransform: orignalTransform from masked
    :param geopandasData: geopandasData from Shapefile
    :return: Shape that most similar to original (shapely.geometry.polygon.Polygon)
    """
    originalArea = geopandasData.area.tolist()[0]
    lShape = []
    lAreaDifference = []

    for _, __ in rasterio.features.shapes(boundariesArray, transform=originalTransform):
        newShape = shape(_)
        diff = abs(newShape.area - originalArea)
        lShape.append(newShape)
        lAreaDifference.append(diff)

    return lShape[np.argmin(lAreaDifference)], lShape


