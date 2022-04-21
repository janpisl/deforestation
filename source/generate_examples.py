
import glob
import os
from pathlib import Path
import matplotlib.pyplot as plt
import sys
import argparse
import logging
from typing import List

from shapely.geometry import box, Polygon
import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import get_data_window, transform, shape
import geopandas as gpd
import pandas as pd
from pandas import Timestamp
from rasterio.mask import mask


def get_raster_intersection(rasters: List) -> Polygon:
    """Return the intersection of two rasters

    Args:
        rasters (List): paths to the rasters

    Returns:
        Polygon: geometry of their intersection
    """

    assert len(rasters) == 2, f"Expected two rasters, got {len(rasters)}"
    bounds_1 = get_raster_bounds(rasters[0])
    bounds_2 = get_raster_bounds(rasters[1])

    return bounds_1.intersection(bounds_2)


def get_raster_bounds(path: str) -> Polygon:
    """Open raster and return its extent/bounds

    Args:
        path (str): path to tif file

    Returns:
        Polygon: extent of the raster as a shapely Polygon
    """
    with rasterio.open(path) as src:
        geom = box(*src.bounds)
    
    return geom


def get_raster_date(path: str) -> Timestamp:
    """Extract date from file name

    Args:
        path (str): path to raster file; expects certain naming conventions

    Returns:
        pandas Timestamp: date of acquisition of this raster
    """

    filename = Path(path).stem
    date = pd.to_datetime(filename.replace("_", "-"))

    return date


def get_epsg(path: str) -> int:
    """Get EPSG code of a raster

    Args:
        path (str): path to raster file

    Returns:
        int: EPSG code
    """
    with rasterio.open(path) as src:
        return src.crs.to_epsg()


def filter_gdf_by_time(gdf: gpd.GeoDataFrame, date_column: str,
                      start_date: str, end_date: str,
                      margin_before: str, margin_after: str) -> gpd.GeoDataFrame:
    """Return

    Args:
        gdf (gpd.GeoDataFrame): gdf to be filtered
        date_column (str): name of column that contains date
        start_date (str): starting date
        end_date (str): end date
        margin_before (str): to add after start date
        margin_after (str): to subtract from end date

    Returns:
        gpd.GeoDataFrame: filtered gdf
    """
    assert len(gdf) > 0, "Attempting to filter an empty GeoDataFrame"
    
    try:
        gdf['date'] = pd.to_datetime(gdf[date_column])
    except:
        raise ValueError(f"Couldn't find or convert column {date_column} to date.")

    temporal_subset = gdf.loc[
        (gdf['date'] > (start_date + margin_before).strftime('%Y-%m-%d')) 
        & (gdf['date'] < (end_date - margin_after).strftime('%Y-%m-%d'))]

    assert len(temporal_subset) > 0, "No features left after filtering by geometry"

    return temporal_subset


def filter_gdf_by_geometry(gdf: gpd.GeoDataFrame, 
                           geometry: Polygon) -> gpd.GeoDataFrame:
    """Return a filtered GeoDataFrame that contains features intersecting with geometry

    Args:
        gdf (gpd.GeoDataFrame): any gdf
        geometry (Polygon): Shapely Polygon intersecting with gdf

    Returns:
        gpd.GeoDataFrame: Filtered gdf 
    """
    assert len(gdf) > 0, "Attempting to filter an empty GeoDataFrame"
    assert (gdf.intersects(geometry)).any().values[0], "Geometry and GeoDataFrame don't intersect"
    subset_gdf = gdf.loc[gdf.intersects(geometry)].copy()
    assert len(subset_gdf) > 0, "No features left after filtering by geometry"

    return subset_gdf
    

def write_image_chip(geometry: Polygon, image_path: str, id: str, out_dir: str) -> None:
    """Write to disk an image based on provided raster, cropped by provided geometry.

    Args:
        geometry (Polygon): extent of the image chip
        image_path (str): raster from which the chip is extracted
        id (str): identifier for naming
        out_dir (str): directory where files will be written
    """

    out_name = str(id) + "_" + Path(image_path).name
    out_path = os.path.join(out_dir, out_name)

    with rasterio.open(image_path) as src:
        out_image, out_transform = mask(src, [geometry], crop=True)
        out_meta = src.meta

    out_meta.update({"driver": "GTiff",
                    "height": out_image.shape[1],
                    "width": out_image.shape[2],
                    "transform": out_transform})


    with rasterio.open(out_path, "w", **out_meta) as dest:
        dest.write(out_image)


def filter_reference_data(image_before_path: str, 
         image_after_path: str, 
         margin_before: int, 
         margin_after: int,
         reference_data_path: str, 
         date_column: str) -> gpd.GeoDataFrame:
    """Given a path to a GeoDataFrame, filter it based
    on location and time and return filtered gdf.

    Args:
        image_before_path (str): Path to first raster
        image_after_path (str): Path to second raster 
        margin_before (str): to add after start date
        margin_after (str): to subtract from end date
        reference_data_path (str): Path to reference data gdf
        date_column (str): column in reference data containing date

    Returns:
        gpd.GeoDataFrame: filtere gdf
    """

    start_date = get_raster_date(image_before_path)
    end_date = get_raster_date(image_before_path)

    margin_before = pd.to_timedelta(margin_before, unit='d')
    margin_after = pd.to_timedelta(margin_after, unit='d')

    crs_1, crs_2 = get_epsg(image_before_path), get_epsg(image_after_path)
    assert crs_1 == crs_2, f"Rasters don't have the same CRS: '{crs_1}' and '{crs_2}' "

    intersection = get_raster_intersection(image_before_path, image_after_path)

    reference_data_gdf = gpd.read_file(reference_data_path).to_crs(crs_1)


    filtered_reference_data = filter_gdf_by_geometry(reference_data_gdf, intersection)
    filtered_reference_data = filter_gdf_by_time(filtered_reference_data, start_date, end_date,
        date_column, margin_before, margin_after,)


    logging.info(f"Number of applicable polygons found: {filtered_reference_data.shape[0]}")

    return filter_reference_data



def main(image_before_path: str, 
         image_after_path: str, 
         margin_before: int, 
         margin_after: int,
         reference_data_path: str, 
         buffer: int,
         date_column: str,
         out_directory: str
         ) -> None:


    reference_data = filter_reference_data(image_before_path, image_after_path, 
                                           margin_before, margin_after,
                                           reference_data_path, date_column)

    # The envelope of a geometry is the bounding rectangle. 
    # That is, the point or smallest rectangular polygon 
    # (with sides parallel to the coordinate axes) that contains the geometry.
    reference_data['bbox'] = reference_data.envelope.buffer(buffer)


    for idx, row in reference_data.iterrows():
        write_image_chip(row.bbox, image_before_path, idx, out_directory)
        write_image_chip(row.bbox, image_after_path, idx, out_directory)




if __name__ == "__main__":


    parser = argparse.ArgumentParser()
 
    parser.add_argument("--image_1", "-img_1", type=str, help="Path to the 'before' image", required=True)
    parser.add_argument("--image_2", "-img_2", type=str, help="Path to the 'after' image", required=True)
    parser.add_argument("--labels", "-l", type=str, help="Path to reference data", required=True)

    parser.add_argument("--margin_1", "-m_1", type=int, default=31, help="How many days after image_1 acquisition before reference data are considered.\
                                                                                Corresponds to the expected delay of the reference data monitoring system.")
    parser.add_argument("--margin_2", "-m_2", type=int, default=0, help="Until how many days before image_2 acquisition reference data are considered.\
                                                                                Corresponds to the reference data system assigning earlier dates than reality.")

    parser.add_argument("--buffer", "-b", type=int, default=100, help="Buffer around deforestation polygons in meters")
    parser.add_argument("--out_directory", "-out", type=str, help="Destination where examples will be written", required=True)
    parser.add_argument("--date_column", "-d", type=str, default='VIEW_DATE', help="Buffer around deforestation polygons in meters")


    args = parser.parse_args()


    main(args.image_1, 
         args.image_2, 
         args.margin_1, 
         args.margin_2,
         args.labels, 
         args.buffer,
         args.date_column,
         args.out_directory)








