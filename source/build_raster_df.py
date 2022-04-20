
import sys
import os
import pdb
import json
import glob
import logging
from pathlib import Path

from shapely.geometry import box
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import get_data_window, transform, shape
import geopandas as gpd


def get_row(path):

    dataset = rasterio.open(path)
    geom = box(*dataset.bounds)
    
    #date = dataset.date <- to implement

    return dataset, geom


def main(input_dir):

    rasters = [file for file in os.listdir(input_dir) if file.endswith(".tif")]
    logging.info(f"Found {len(rasters)} raster files.")

    #columns = ['path', 'date', 'extent']
    rows = []
    for raster in rasters:
        in_path = os.path.join(input_dir, raster)
        rows.append(get_row(in_path))

    df = pd.DataFrame(rows, columns=columns)
    gdf = gpd.GeoDataFrame(df, geometry='geom')

    gdf.to_file('')



if __name__ == "__main__":

    input_dir = sys.argv[1]


    main(input_dir)