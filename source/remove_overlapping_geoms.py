import geopandas as gpd
import itertools

# load data
path = ''
gdf1 = gpd.read_file(path)

# get list of geometries
geoms = gdf1['geometry'].tolist()

# iterate over all combinations of polygons and get the intersections (overlaps)
overlaps = gpd.GeoSeries([poly[0].intersection(poly[1]) for poly in itertools.combinations(geoms, 2) if poly[0].intersects(poly[1])])

overlaps_gdf = gpd.GeoDataFrame(overlaps, columns=['geometry'])

# set the crs
overlaps_gdf.crs = gdf1.crs

# erase the overlaps from the original geodataframe
gdf2 = gdf1.overlay(overlaps_gdf, how='difference')