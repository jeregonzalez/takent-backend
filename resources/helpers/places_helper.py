import logging
import os

import pandas as pd

ENDPOINT = 'https://apis.datos.gob.ar'
FILE_BASE_PATH = './temp_data'
COUNTRY = 'Argentina'

API_OPTIONS = {
    'provinces': {
        'api': '{}/georef/api/provincias'.format(ENDPOINT),
        'params': {
            'campos': 'id,nombre'
        },
        'file_path': '{}/provinces.csv'.format(FILE_BASE_PATH),
        'columns_map': {
            'provincia_id': 'code',
            'provincia_nombre': 'name'
        }
    },
    'cities': {
        'api': '{}/georef/api/localidades'.format(ENDPOINT),
        'params': {
            'campos': 'id,nombre,provincia.id'
        },
        'file_path': '{}/cities.csv'.format(FILE_BASE_PATH),
        'columns_map': {
            'localidad_id': 'code',
            'localidad_nombre': 'name',
            'provincia_id': 'province_id'
        }
    }
}


def _get(api):
    if not API_OPTIONS.get(api):
        logging.error('{} is not defined'.format(api))
        return
    api_options = API_OPTIONS.get(api)

    file_path = api_options.get('file_path')
    if os.path.exists(file_path):
        logging.info('{} already exists. Returning existing info.'.format(file_path))
        return pd.read_csv(file_path).to_dict(orient='records')

    api_path = api_options.get('api')
    params = api_options.get('params')
    params['formato'] = 'csv'
    params['max'] = '5000'

    url = api_path + '?{}'.format('&'.join(['{}={}'.format(key, value) for key, value in params.items()]))
    logging.info('GET {}'.format(url))
    dataframe = pd.read_csv(url)
    dataframe = dataframe.rename(columns=api_options.get('columns_map'))
    dataframe.to_csv(file_path, index=False)
    return dataframe.to_dict(orient='records')


def get_countries():
    return [{'code': 1, 'name': COUNTRY}]


def get_provinces():
    return _get('provinces')


def get_cities():
    return _get('cities')
