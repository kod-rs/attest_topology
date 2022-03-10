"""Module containing the implementation for building the node-breaker model."""
import attest.db
import click
import datetime
import sys


def build(connection, branch, commit, valid_time):

    classes = connection.get_classes()
    classes = {row['cimclass']: row['cimclassid'] for row in classes}

    def recordat(*args, **kwargs):
        return connection.recordat(branch, commit, valid_time,
                                   *args, **kwargs)

    class_ids = [classes[name] for name in
                 ('cim:Breaker', 'cim:Disconnector', 'cim:BusbarSection',
                  'cim:ACLineSegment', 'cim:EquivalentInjection',
                  'cim:EnergyConsumer', 'cim:ConnectivityNode',
                  'cim:Terminal')]
    records = recordat(cim_class_ids=class_ids)

    node_set = []
    asset_map = {}
    switch_map = {}
    terminal_map = {}
    merge_map = {}
    connectivity_map = {}
    for record in records:
        record = dict(record, **record['fullobject'])
        del record['fullobject']

        mrid = record['mrid']
        asset_map[mrid] = record
        if record['cimclass'] == 'cim:ConnectivityNode':
            node_set.append(record)
            merge_map[mrid] = mrid
        elif record['cimclass'] in ('cim:Breaker', 'cim:Disconnector'):
            switch_map[mrid] = True  # TODO inject real data
        elif record['cimclass'] == 'cim:Terminal':
            element_mrid = record['cim:Terminal.ConductingEquipment']
            terminal_map.setdefault(element_mrid, [])
            terminal_map[element_mrid].append(mrid)

            cn_mrid = record['cim:Terminal.ConnectivityNode']
            connectivity_map.setdefault(cn_mrid, [])
            connectivity_map[cn_mrid].append(mrid)

    for node in sorted(node_set, key=lambda n: n['mrid']):
        connected_nodes = set([merge_map[node['mrid']]])
        for terminal_mrid in connectivity_map[node['mrid']]:
            terminal = asset_map[terminal_mrid]
            switch_mrid = terminal['cim:Terminal.ConductingEquipment']

            switch = asset_map.get(switch_mrid)
            if switch is None:
                continue

            if switch['cimclass'] not in ('cim:Breaker', 'cim:Disconnector'):
                continue

            if not switch_map[switch['mrid']]:
                continue

            other_term_mrid = [t for t in terminal_map[switch['mrid']]
                               if t != terminal_mrid][0]
            other_term = asset_map[other_term_mrid]
            other_node_mrid = other_term['cim:Terminal.ConductingEquipment']
            connected_nodes.add(other_node_mrid)

        max_mrid = max(connected_nodes)
        connectivity_map.setdefault(max_mrid, [])
        connected_nodes.remove(max_mrid)
        for mrid in connected_nodes:
            merge_map[mrid] = max_mrid
            connectivity_map[max_mrid].extend(connectivity_map.get(mrid, []))
            connectivity_map[mrid] = []

    for node in node_set[::-1]:
        if (node['mrid'] not in merge_map
                or merge_map[node['mrid']] not in merge_map):
            continue
        merge_map[node['mrid']] = merge_map[merge_map[node['mrid']]]

    topological_nodes = {}
    for node_mrid, final_node in merge_map.items():
        topological_nodes.setdefault(final_node, set())
        topological_nodes[final_node].add(node_mrid)

    return topological_nodes


@click.command()
@click.option('--dbname', help='name of the cim database', required=True)
def main(dbname):
    with attest.db.connect(dbname) as c:
        model = build(c, 4, 1, datetime.datetime.now())
        print(model)


if __name__ == '__main__':
    sys.exit(main())
