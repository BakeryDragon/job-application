from flask import Flask

from app.database import init_db
from app.routes import routes


def create_app():
    app = Flask(__name__, template_folder="templates")
    app.register_blueprint(routes)
    return app
