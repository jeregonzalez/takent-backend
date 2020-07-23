import os
from logging.config import dictConfig

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restful import Api

from database.db import init_db
from resources.helpers import yaml_helper
from resources.helpers.log_helper import log_request_info
from resources.routes import initialize_routes
from resources.utils.project_vars import ProjectVars
from resources.utils.representations import json_output

CONFIG_BASE_DIR = 'config/'
CONFIG_ENV_BASE_DIR = CONFIG_BASE_DIR + 'env/'
DEFAULT_ENV_CONFIG_FILE = 'develop.yaml'
DEFAULT_LOG_CONFIG_FILE = 'logging.yaml'

LOG_CONFIG_FILE = CONFIG_BASE_DIR + os.environ.get('LOG_CONFIG_FILE', DEFAULT_LOG_CONFIG_FILE)
API_CONFIG_FILE = CONFIG_ENV_BASE_DIR + os.environ.get('API_CONFIG_FILE', DEFAULT_ENV_CONFIG_FILE)

if not os.path.exists('logs'):
    os.makedirs('logs')

app = Flask(__name__)
api = Api(app)

api.representations.update({
    'application/json': json_output
})

bcrypt = Bcrypt(app)

dictConfig(yaml_helper.to_dict(LOG_CONFIG_FILE))
app.config.from_mapping(yaml_helper.to_dict(API_CONFIG_FILE))
ProjectVars.set_project_vars(app.config.items())

jwt = JWTManager(app)

init_db(app)

initialize_routes(api)

app.before_request(log_request_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
