import geopandas as gpd
import itertools
import pdb
from generate_image_chips import filter_gdf_by_geometry

# load data
path = 'data/sample_data/DETER/deter_public.shp'
gdf1 = gpd.read_file(path)
aoi1 = gpd.read_file('data/aoi_1/vector/aoi_1.geojson').to_crs(gdf1.crs.to_epsg())

#subset DETER to the AOI
deter_spatial_subset = filter_gdf_by_geometry(gdf1, aoi1.geometry.values[0])

#I think this is necessary
deter_spatial_subset = deter_spatial_subset.explode().reset_index()

# get list of geometries
geoms = deter_spatial_subset['geometry'].tolist()

# iterate over all combinations of polygons and get the intersections (overlaps)
overlaps = gpd.GeoSeries([poly[0].intersection(poly[1]) for poly in itertools.combinations(geoms, 2) if poly[0].intersects(poly[1])])

overlaps_gdf = gpd.GeoDataFrame(overlaps, columns=['geometry'])

#explode
overlaps_gdf = overlaps_gdf.explode()

#Only select rows with area > 0, ie. polygons
polygons = overlaps_gdf[overlaps_gdf.geometry.area > 0]
polygons = polygons.drop(['level_0', 'level_1'], axis=1)

pdb.set_trace()

polygons.to_file("data/aoi_1/vector/workdir/deter_subset_overlaps_2019_07_16___2020_07_15.shp", index=False)

# set the crs
overlaps_gdf.crs = gdf1.crs

# erase the overlaps from the original geodataframe
gdf2 = gdf1.overlay(overlaps_gdf, how='difference')