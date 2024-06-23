from flask import Blueprint

bp = Blueprint("api", __name__)

from backend.app.endpoints import jobs, indicators
