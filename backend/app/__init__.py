from flask import Flask
from flask_restful import Api

from backend.app.endpoints import bp as bp_api

app = Flask(__name__)
api = Api(bp_api)

app.register_blueprint(bp_api)
