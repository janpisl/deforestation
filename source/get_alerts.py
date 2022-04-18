

import os
import pdb
import json
import pprint
import requests
from requests import Response
from typing import List, Set, Dict, Any, Tuple

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


def mock_get_aoi2(id):
    gdf_mapb = gpd.read_file('/Users/janpisl/Documents/EPFL/workdir/sample_data/MapBiomas/dashboard_alerts-shapefilePolygon.shp')
    item = gdf_mapb.loc[gdf_mapb.IDAlerta == id]
    bb: Tuple[float] = item.total_bounds
    epsg = gdf_mapb.crs

    #bb: Tuple[float]= [-61.81936291,   3.85968348, -61.81422454,   3.86315098]
    #bb: Tuple[float]= [-59.44958922,   1.11774676, -59.43363514,   1.13765343]
    #epsg: int = 4674

    aoi: Polygon = Polygon([ [bb[0], bb[1]], [bb[0], bb[3]], [bb[2], bb[3]], [bb[2],bb[1]]])

    aoi_gdf: GeoDataFrame = gpd.GeoDataFrame([], geometry=[aoi], crs=epsg)
    aoi = aoi_gdf.to_crs(4326).to_json()
    
    return json.loads(aoi)['features'][0]['geometry']

def get_radd_alerts(api_key, 
                         aoi, 
                         start_date=None, 
                         end_date=None, 
                         dataset_name='wur_radd_alerts', 
                         version='latest', 
                         query=None):
    """

    Args:
        api_key (str): _description_
        aoi (shapely.Polygon): _description_
        version (str, optional): _description_. Defaults to 'latest'.
    """


    if not query:
        if not (start_date and end_date):
            raise ValueError("Either start and end dates or query must be provided.")
        query: str = f"SELECT longitude, latitude, wur_radd_alerts__date, wur_radd_alerts__confidence FROM results WHERE wur_radd_alerts__date >= '{start_date}'  AND wur_radd_alerts__date <= '{end_date}'"
    
    body: Dict[str, str] = {'geometry' : aoi, 'sql' : query}
    body_encoded: str = json.dumps(body).encode('utf-8')
    headers: Dict[str, str] = {'Content-Type': 'application/json', 'x-api-key' : api_key}

    url_data_request: str = f'https://data-api.globalforestwatch.org/dataset/{dataset_name}/{version}/query'
    resp = requests.post(url_data_request, data=body_encoded, headers=headers)
    if resp.status_code >= 400:
        print(resp.text)
        raise Exception('Request failed.')
    alerts_data = json.loads(resp.text)
    df = pd.DataFrame(alerts_data['data'])

    return df


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
    resp = requests.post(url_data_request, data=body_encoded, headers=headers)
    if resp.status_code >= 400:
        print(resp.text)
        raise Exception('Request failed.')
    alerts_data = json.loads(resp.text)
    df = pd.DataFrame(alerts_data['data'])

    return df





if __name__ == "__main__":


    # these should go to config
    IDAlerta = 305393
    aoi = mock_get_aoi2(IDAlerta)
    start_date: str = '2020-01-01'
    end_date: str = '2022-02-28'
    api_key: str = '4d824101-4456-441e-82c1-005ff1fd0e41'
    #query: str = f"SELECT longitude, latitude, wur_radd_alerts__date, wur_radd_alerts__confidence FROM results WHERE wur_radd_alerts__date >= '{start_date}'  AND wur_radd_alerts__date <= '{end_date}'"
    #dataset_name = 'wur_radd_alerts'
    #alert_system = 'RADD'

    query: str = "SELECT longitude, latitude, umd_glad_landsat_alerts__date, umd_glad_landsat_alerts__date_conf,umd_glad_landsat_alerts__confidence FROM results WHERE umd_glad_landsat_alerts__date >= '2021-01-01' AND umd_glad_landsat_alerts__date <='2021-03-31'"
    dataset_name = 'umd_glad_landsat_alerts'
    alert_system = 'GLAD'
    
    alerts_df = request_gfw_alerts(api_key, aoi, dataset_name, query)

    gdf = gpd.GeoDataFrame(alerts_df, geometry=gpd.points_from_xy(alerts_df.longitude, alerts_df.latitude))
    gdf = gdf.drop(['latitude', 'longitude'], axis=1)
    gdf.crs = 4326
    pdb.set_trace()
    print('Shape of resulting gdf: ', gdf.shape)
    gdf.to_file(f'{alert_system}_alerts_for_id_{IDAlerta}.shp')
    print()
    

