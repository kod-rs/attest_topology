class UnprocessedModel:

    def __init__(self):
        self._node_set = None
        self._asset_map = None
        self._switch_map = None
        self._terminal_map = None
        self._connectivity_map = None

    @property
    def node_set(self):
        return self._node_set

    @property
    def asset_map(self):
        return self._asset_map

    @property
    def switch_map(self):
        return self._switch_map

    @property
    def terminal_map(self):
        return self._terminal_map

    @property
    def connectivity_map(self):
        return self._connectivity_map

    def load_data_structures(self, connection, branch, commit, valid_time):
        classes = connection.get_classes()
        classes = {row['cimclass']: row['cimclassid'] for row in classes}
        class_ids = [classes[name] for name in
                     ('cim:Breaker', 'cim:Disconnector', 'cim:BusbarSection',
                      'cim:ACLineSegment', 'cim:EquivalentInjection',
                      'cim:EnergyConsumer', 'cim:ConnectivityNode',
                      'cim:Terminal')]
        records = connection.recordat(branch, commit, valid_time,
                                      cim_class_ids=class_ids)

        node_set = []
        asset_map = {}
        switch_map = {}
        terminal_map = {}
        connectivity_map = {}
        for record in records:
            record = dict(record, **record['fullobject'])
            del record['fullobject']

            mrid = record['mrid']
            asset_map[mrid] = record
            if record['cimclass'] == 'cim:ConnectivityNode':
                node_set.append(record)
            elif record['cimclass'] in ('cim:Breaker', 'cim:Disconnector'):
                switch_map[mrid] = True  # TODO inject real data
            elif record['cimclass'] == 'cim:Terminal':
                element_mrid = record['cim:Terminal.ConductingEquipment']
                terminal_map.setdefault(element_mrid, [])
                terminal_map[element_mrid].append(mrid)

                cn_mrid = record['cim:Terminal.ConnectivityNode']
                connectivity_map.setdefault(cn_mrid, [])
                connectivity_map[cn_mrid].append(mrid)

        self._node_set = node_set
        self._asset_map = asset_map
        self._switch_map = switch_map
        self._terminal_map = terminal_map
        self._connectivity_map = connectivity_map
