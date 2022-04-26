

import enum
import os
import pdb
import json
import pprint
import requests
from requests import Response
from typing import List, Set, Dict, Any, Tuple

import tqdm
import shapely
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon, shape
from geopandas import GeoDataFrame
import matplotlib.pyplot as plt

from typing import Dict




def mock_get_aoi():
    """mock function

    Returns:
        GeoDataFrame: _description_
    """
    bb: Tuple[int] = (-7006677,-1024964, -6855473,-868057)
    epsg: int = 3857

    aoi: Polygon = Polygon([ [bb[0], bb[1]], [bb[0], bb[3]], [bb[2], bb[3]], [bb[2],bb[1]]])

    aoi_gdf: GeoDataFrame = gpd.GeoDataFrame([], geometry=[aoi], crs=epsg)
    aoi = aoi_gdf.to_crs(4326).to_json()
    
    return json.loads(aoi)['features'][0]['geometry']


def get_aoi(path):
    gdf = gpd.read_file(path)
    gdf = gdf.to_crs(4326).to_json()

    return json.loads(gdf)['features'][0]['geometry']


def mock_get_aoi2(id):
    gdf_mapb = gpd.read_file('/Users/janpisl/Documents/EPFL/workdir/sample_data/MapBiomas/dashboard_alerts-shapefilePolygon.shp')
    item = gdf_mapb.loc[gdf_mapb.IDAlerta == id]
    bb: Tuple[float] = item.total_bounds
    epsg = gdf_mapb.crs

    aoi: Polygon = Polygon([ [bb[0], bb[1]], [bb[0], bb[3]], [bb[2], bb[3]], [bb[2],bb[1]]])

    aoi_gdf: GeoDataFrame = gpd.GeoDataFrame([], geometry=[aoi], crs=epsg)
    aoi = aoi_gdf.to_crs(4326).to_json()
    
    return json.loads(aoi)['features'][0]['geometry']




def request_gfw_alerts(api_key, 
                         aoi, 
                         dataset_name, 
                         query,
                         version='latest'):
    """

    Args:
        api_key (str): _description_
        aoi (shapely.Polygon): _description_
        version (str, optional): _description_. Defaults to 'latest'.
    """


    body: Dict[str, str] = {'geometry' : aoi, 'sql' : query}
    body_encoded: str = json.dumps(body).encode('utf-8')
    headers: Dict[str, str] = {'Content-Type': 'application/json', 'x-api-key' : api_key}

    url_data_request: str = f'https://data-api.globalforestwatch.org/dataset/{dataset_name}/{version}/query'
    resp = requests.post(url_data_request, data=body_encoded, headers=headers, timeout=600)
    if resp.status_code >= 400:
        print(resp.text)
        raise Exception('Request failed.')
    alerts_data = json.loads(resp.text)
    df = pd.DataFrame(alerts_data['data'])

    return df



def get_query(dates, i, system):
    start_date = f'{dates[i].year}-{dates[i].month:02d}-{dates[i].day:02d}'
    end_date = f'{dates[i+1].year}-{dates[i+1].month:02d}-{dates[i+1].day:02d}'
    
    #print(start_date, end_date)
    if system == "RADD":
        query: str = f"SELECT longitude, latitude, wur_radd_alerts__date, wur_radd_alerts__confidence FROM results WHERE wur_radd_alerts__date >= '{start_date}'  AND wur_radd_alerts__date <= '{end_date}'"
    elif system == "GLAD":
        query: str = f"SELECT longitude, latitude, umd_glad_landsat_alerts__date, umd_glad_landsat_alerts__date_conf,umd_glad_landsat_alerts__confidence FROM results WHERE umd_glad_landsat_alerts__date >= '{start_date}' AND umd_glad_landsat_alerts__date <='{end_date}'"
    else:
        raise ValueError(f"Expected RADD or GLAD, got: {system}")
    
    return query


if __name__ == "__main__":

    path = 'data/aoi_1/vector/aoi_1.geojson'
    aoi = get_aoi(path)

    api_key: str = '4d824101-4456-441e-82c1-005ff1fd0e41'
    dataset_name = 'wur_radd_alerts'
    #dataset_name = 'umd_glad_landsat_alerts'

    alert_system = 'RADD'

    dates = pd.date_range('2018-12-26', periods=54, freq='w')

    series = []

    for i in tqdm.tqdm(range(len(dates)-1)):

        query = get_query(dates, i, alert_system)
        try:
            alerts_df = request_gfw_alerts(api_key, aoi, dataset_name, query)
            series.append(alerts_df)
        except:
            try:
                weekly_dates = pd.date_range(dates[i], periods=8, freq='d')
                for j in range(len(weekly_dates)-1):
                    query = get_query(weekly_dates, j, alert_system)

                    alerts_df = request_gfw_alerts(api_key, aoi, dataset_name, query)
                    pdb.set_trace()
                    series.append(alerts_df)
            except:
                pdb.set_trace()
                print()

        

    all = pd.concat(series)
    gdf = gpd.GeoDataFrame(all, geometry=gpd.points_from_xy(all.longitude, all.latitude))
    gdf = gdf.drop(['latitude', 'longitude'], axis=1)
    gdf.crs = 4326
    pdb.set_trace()
    print('Shape of resulting gdf: ', gdf.shape)
    gdf.to_file(f'data/aoi_1/vector/{alert_system}_alerts_for_aoi_1.shp')
    print()
    

