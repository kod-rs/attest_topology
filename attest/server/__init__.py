from attest import topology

from flask import Flask
import datetime
import os


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py')

    conn = topology.db.Connection(dbname=app.config['DB_NAME'],
                                  host=app.config['DB_HOST'],
                                  port=app.config['DB_PORT'],
                                  user=app.config['DB_USER'],
                                  password=app.config['DB_PASSWORD'])
    conn.connect()

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def calculate_topology():
        unprocessed = topology.unprocessed.UnprocessedModel(
            conn, 4, 2, datetime.datetime.now())
        node_breaker = topology.node_breaker.NodeBreakerModel(unprocessed)
        node_branch = topology.node_branch.NodeBranchModel(node_breaker)

        admittance_sparse = []
        for i, row in enumerate(node_branch.admittance_matrix):
            for j, value in enumerate(row):
                if value == 0:
                    continue
                admittance_sparse.append(_sparse_entry(i, j, value))

        return {
            'admittance_sparse_matrix': admittance_sparse,
            'topological_nodes': [
                [node_mrid, list(elements)]
                for node_mrid, elements
                in node_branch.topological_nodes]
        }, 'json'

    return app


def _sparse_entry(i, j, value):
    value = complex(value)
    return {'row': i,
            'col': j,
            'value': [value.real, value.imag]}
