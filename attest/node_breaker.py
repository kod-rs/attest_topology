"""Module containing the implementation for building the node-breaker model."""
import attest.db
import attest.unprocessed
import click
import datetime
import sys


class NodeBreakerModel:

    def __init__(self, unprocessed, topological_nodes, connectivity_map):
        self._unprocessed = unprocessed
        self._topological_nodes = topological_nodes
        self._connectivity_map = connectivity_map

    @property
    def topological_nodes(self):
        return self._topological_nodes

    @property
    def connectivity_map(self):
        return self._connectivity_map

    @property
    def terminal_map(self):
        return self._unprocessed.terminal_map

    @property
    def asset_map(self):
        return self._unprocessed.asset_map

    @property
    def switch_map(self):
        return self._unprocessed.switch_map


def merge_nodes(unprocessed):
    connectivity_map = {mrid: list(terminals) for mrid, terminals
                        in unprocessed.connectivity_map.items()}
    merge_map = {node['mrid']: node['mrid'] for node in unprocessed.node_set}
    topological_nodes = {}

    for node in sorted(unprocessed.node_set, key=lambda n: n['mrid']):
        connected_nodes = set([merge_map[node['mrid']]])
        for terminal_mrid in connectivity_map[node['mrid']]:
            terminal = unprocessed.asset_map[terminal_mrid]
            switch_mrid = terminal['cim:Terminal.ConductingEquipment']

            switch = unprocessed.asset_map.get(switch_mrid)
            if switch is None:
                continue

            if switch['cimclass'] not in ('cim:Breaker', 'cim:Disconnector'):
                continue

            if not unprocessed.switch_map[switch['mrid']]:
                continue

            other_term_mrid = [t for t
                               in unprocessed.terminal_map[switch['mrid']]
                               if t != terminal_mrid][0]
            other_term = unprocessed.asset_map[other_term_mrid]
            other_node_mrid = other_term['cim:Terminal.ConnectivityNode']
            connected_nodes.add(other_node_mrid)

        max_mrid = max(connected_nodes)
        connectivity_map.setdefault(max_mrid, [])
        connected_nodes.remove(max_mrid)
        for mrid in connected_nodes:
            merge_map[mrid] = max_mrid
            connectivity_map[max_mrid].extend(connectivity_map.get(mrid, []))
            connectivity_map[mrid] = []

    for node in unprocessed.node_set[::-1]:
        if (node['mrid'] not in merge_map
                or merge_map[node['mrid']] not in merge_map):
            continue
        merge_map[node['mrid']] = merge_map[merge_map[node['mrid']]]

    for node_mrid, final_node in merge_map.items():
        topological_nodes.setdefault(final_node, set())
        topological_nodes[final_node].add(node_mrid)

    return topological_nodes, connectivity_map


@click.command()
@click.option('--dbname', help='name of the cim database', required=True)
def main(dbname):
    model = attest.unprocessed.UnprocessedModel()
    with attest.db.connect(dbname) as c:
        model.load_data_structures(c, 4, 1, datetime.datetime.now())
    topological_nodes, connectivity_map = merge_nodes(model)
    print(topological_nodes)


if __name__ == '__main__':
    sys.exit(main())
