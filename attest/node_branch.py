import attest.db
import attest.node_breaker
import attest.unprocessed
import click
import datetime
import sys


class NodeBranchModel:

    def __init__(self, node_breaker, admittance_matrix):
        self._node_breaker = node_breaker
        self._admittance_matrix = admittance_matrix

    @property
    def admittance_matrix(self):
        return self._admittance_matrix

    @property
    def topological_nodes(self):
        return self._node_breaker.topological_nodes


def calculate_admittance_matrix(node_breaker):
    connectivity_inv = {}
    for k, terminals in node_breaker.connectivity_map.items():
        for terminal in terminals:
            connectivity_inv[terminal] = k

    node_count = len(node_breaker.topological_nodes)
    matrix = [[0] * node_count for _ in range(node_count)]
    nodes = list(node_breaker.topological_nodes.keys())
    processed_lines = set()
    for i, node_mrid in enumerate(nodes):
        for term_mrid in node_breaker.connectivity_map[node_mrid]:
            terminal = node_breaker.asset_map[term_mrid]

            line_seg_mrid = terminal['cim:Terminal.ConductingEquipment']
            line_seg = node_breaker.asset_map.get(line_seg_mrid)
            if not line_seg or line_seg['cimclass'] != 'cim:ACLineSegment':
                continue
            if line_seg_mrid in processed_lines:
                continue
            processed_lines.add(line_seg_mrid)

            x = (line_seg['cim:ACLineSegment.x']
                 or line_seg['cim:ACLineSegment.x0'])
            r = (line_seg['cim:ACLineSegment.r']
                 or line_seg['cim:ACLineSegment.r0'])
            gch = (line_seg['cim:ACLineSegment.gch']
                   or line_seg['cim:ACLineSegment.g0ch'])
            bch = (line_seg['cim:ACLineSegment.bch']
                   or line_seg['cim:ACLineSegment.b0ch'])
            denominator = r ** 2 + x ** 2
            if denominator == 0:
                continue
            admittance = (complex(r / denominator, - x / denominator)
                          + complex(gch / 2, bch / 2))

            other_term_mrid = [t for t
                               in node_breaker.terminal_map[line_seg_mrid]
                               if t != term_mrid][0]
            other_node = connectivity_inv[other_term_mrid]
            j = nodes.index(other_node)

            matrix[i][j] = admittance
            matrix[j][i] = -admittance
    return matrix


@click.command()
@click.option('--dbname', help='name of the cim database', required=True)
def main(dbname):
    unprocessed = attest.unprocessed.UnprocessedModel()
    with attest.db.connect(dbname) as c:
        unprocessed.load_data_structures(c, 4, 1, datetime.datetime.now())

    topological_nodes, connectivity_map = attest.node_breaker.merge_nodes(
        unprocessed)
    node_breaker = attest.node_breaker.NodeBreakerModel(
        unprocessed, topological_nodes, connectivity_map)

    print(calculate_admittance_matrix(node_breaker))


if __name__ == '__main__':
    sys.exit(main())
