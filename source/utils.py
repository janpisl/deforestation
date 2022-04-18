"""
Utility functions for deforestation mapping.

Author: Jan Pisl

Created: 16/2/2022

"""

from typing import Dict

import json
import shapely
import requests
from requests import Response

from shapely.geometry import Polygon


def request_gfw_dataset(api_key: str,
                        dataset_name: str,
                        version: str,
                        aoi: Polygon,
                        query: str
                        ) -> Response:
    """Request a dataset from Global Forest Watch.
    For more information and details on how to get the input parameters, visit:
    https://www.globalforestwatch.org/help/developers/guides/query-data-for-a-custom-geometry/

    Args:
        api_key (str):
            Global Forest Watch API key
        dataset_name (str):
            name of dataset to be requested
        version (str):
            version of the dataset
        aoi (shapely.geometry.Polygon):
            area of interest
        query (str):
            SQL query to select desired data

    Returns:
        requests.Response:
            The object returned by the request
    """

    geometry: str = shapely.geometry.mapping(aoi)

    body: Dict[str, str] = {'geometry' : geometry, 'sql' : query}
    body_encoded: str = json.dumps(body).encode('utf-8')
    headers: Dict[str, str] = {'Content-Type': 'application/json', 'x-api-key' : api_key}

    url_data_request: str = f'https://data-api.globalforestwatch.org/dataset/{dataset_name}/{version}/query'

    resp = requests.post(url_data_request, data=body_encoded, headers=headers)

    resp.raise_for_status()

    return resp


def get_gfw_dataset_meta(dataset_name: str) -> Dict:
    """Give a dataset name, get its metadata from Global Forest Watch.

    Args:
        dataset_name (str)

    Returns:
        Dict:
            Metadata of the dataset
    """
    url = f"https://data-api.globalforestwatch.org/dataset/{dataset_name}"
    resp = requests.get(url)
    resp.raise_for_status()
    metadata: Dict[str, Dict] = json.loads(resp.text)

    return metadata
