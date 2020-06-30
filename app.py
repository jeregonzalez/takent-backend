import os
from logging.config import dictConfig
import yaml
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_restful import Api

from database.db import init_db
from resources.errors import errors
from resources.routes import initialize_routes

with open('config/logging.yaml', 'rt') as f:
    try:
        config = yaml.safe_load(f.read())
        dictConfig(config)
    except Exception as e:
        print(e)

app = Flask(__name__)
api = Api(app, errors=errors)
bcrypt = Bcrypt(app)

cfg = 'config/{}'.format(os.environ.get('AUTHENTICATION_API_CONFIG_FILE', 'default.cfg'))
app.config.from_pyfile(cfg)

jwt = JWTManager(app)

init_db(app)

initialize_routes(api)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
