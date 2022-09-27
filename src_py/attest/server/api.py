import datetime
from flask import request

from attest import topology


def create(app, prefix):
    conn = topology.db.Connection(dbname=app.config['DB_NAME'],
                                  host=app.config['DB_HOST'],
                                  port=app.config['DB_PORT'],
                                  user=app.config['DB_USER'],
                                  password=app.config['DB_PASSWORD'])
    conn.connect()
    app.teardown_appcontext(lambda e: conn.disconnect)

    @app.route(prefix, methods=['GET'])
    def calculate_topology():
        branch_id = _querystring_optional_int('branch_id')
        commit_id = _querystring_optional_int('commit_id')
        timestamp = datetime.datetime.now(tz=datetime.timezone.utc)

        unprocessed = topology.unprocessed.UnprocessedModel(
            conn, branch_id, commit_id, timestamp)
        node_breaker = topology.node_breaker.NodeBreakerModel(unprocessed)
        node_branch = topology.node_branch.NodeBranchModel(node_breaker)

        admittance_sparse = []
        for i, row in enumerate(node_branch.admittance_matrix):
            for j, value in enumerate(row):
                if value == 0:
                    continue
                admittance_sparse.append(_sparse_entry(i, j, value))

        return {'branch_id': branch_id,
                'commit_id': commit_id,
                'datetime': timestamp.timestamp(),
                'admittance_sparse_matrix': admittance_sparse,
                'topological_nodes': [
                    [node_mrid, list(elements)]
                    for node_mrid, elements
                    in node_branch.topological_nodes]
                }, 'json'


def _sparse_entry(i, j, value):
    return {'row': i, 'col': j, 'value': [value.real, value.imag]}


def _querystring_optional_int(key):
    args = request.args
    try:
        return int(args[key])
    except (ValueError, KeyError):
        return None
