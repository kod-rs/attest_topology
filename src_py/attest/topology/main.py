import click
import attest.db
import attest.unprocessed
import attest.node_breaker
import attest.node_branch
import datetime
import sys


@click.command()
@click.option('--dbname', help='name of the cim database', required=True)
def main(dbname):
    unprocessed = attest.unprocessed.UnprocessedModel()
    with attest.db.connect(dbname) as c:
        unprocessed.load_data_structures(c, 4, 2, datetime.datetime.now())

    topological_nodes, connectivity_map = attest.node_breaker.merge_nodes(
        unprocessed)
    node_breaker = attest.node_breaker.NodeBreakerModel(unprocessed,
                                                        topological_nodes,
                                                        connectivity_map)

    matrix = attest.node_branch.calculate_admittance_matrix(node_breaker)
    node_branch = attest.node_branch.NodeBranchModel(node_breaker, matrix)
    print(node_branch)


if __name__ == '__main__':
    sys.exit(main())
