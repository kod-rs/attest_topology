from flask import Flask, send_from_directory
import os

from attest.server import api


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('dev_config.py')

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/', methods=['GET'])
    def root():
        return send_from_directory('.', 'index.html')

    api.create(app, '/api')

    return app
