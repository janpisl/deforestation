'''
For each raster found in specified directory, clip it to only the valid part
and also set nan to pixel values that are clouds based on the scl band.

Example of use:

python source/process_rasters.py data/aoi_1/raster/2019_2021/ data/aoi_1/raster/2019_2021_processed
'''


import sys
import os
import pdb
import json
import glob
import logging
from pathlib import Path
#import matplotlib.pyplot as plt

from tqdm import tqdm
from shapely.geometry import box
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import get_data_window, transform, shape
import geopandas as gpd


s2_scl_table = {
    1 : "satured or defective",
    2 : "dark area pixels",
    3 : "cloud shadows",
    4 : "vegetation",
    5 : "bare soils",
    6 : "water",
    7 : "clouds low probability/unclassified",
    8 : "clouds medium probability",
    9 : "clouds high probability",
    10 : "cirrus",
    11 : "snow/ice"
}


def clip_raster_to_valid(in_path: str, out_path: str) -> None:

    with rasterio.open(in_path) as src:
        profile = src.profile.copy()
        image_read = src.read()
        
        image_read_masked = np.ma.masked_array(image_read, mask=np.isnan(image_read))
        data_window = get_data_window(image_read_masked)
        data_transform = transform(data_window, src.transform)
        height, width = shape(data_window, profile['height'], profile['width'])
        profile.update(
            transform=data_transform,
            height=height,
            width=width)
        
        data = src.read(window=data_window)

    with rasterio.open(out_path, 'w', **profile) as sink:
        sink.write(data)


def mask_clouds(in_path: str, out_path: str, mask: list=[1,3,7,8,9]) -> None:

    with rasterio.open(in_path) as src:

        data = src.read()
        profile = src.profile
        channels = data.shape[0]

    # The last band is the scl layer; the rest is regular data bands we want to use
    image = data[:-1]
    
    assert image.shape[0] == 4, f'expected 4 data channels, got {image.shape[0]}'
    image_valid = np.ma.array(image, mask=np.isnan(image))

    mask_2d = ~np.isin(data[-1], mask)
    mask_3d = np.broadcast_to(mask_2d, image_valid.shape)

    image_valid[~mask_3d] = np.nan

    # We remove the classification band
    profile.update(count=channels-1)
    
    with rasterio.open(out_path, "w", **profile) as sink:
        sink.write(image_valid)


def main(input_dir: str, output_dir: str) -> None:
    #rasters = glob.glob(os.path.join(input_path, "*.tif"))
    rasters = [file for file in os.listdir(input_dir) if file.endswith(".tif")]
    logging.info(f"Found {len(rasters)} raster files.")

    # For debugging
    for raster in tqdm(rasters):
        
        in_path = os.path.join(input_dir, raster)
        out_path = os.path.join(output_dir, raster)
        clip_raster_to_valid(in_path, out_path)
        mask_clouds(out_path, out_path)




if __name__ == "__main__":

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]


    #TODO: convert all raster names to dates and sort them by time

    main(input_dir, output_dir)