from flask import Flask
import os

from attest.server import api


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    api.create(app, '/api')

    return app
