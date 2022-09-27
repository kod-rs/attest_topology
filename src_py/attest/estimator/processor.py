from collections import deque
from pathlib import Path
import click
import logging
import pandapower.estimation
import pandas
import sys

import attest.estimator.generator


logging.basicConfig(stream=sys.stdout, level='INFO')

mlog = logging.getLogger('attest.estimator.processor')


@click.command()
@click.option('--matpower-path', type=Path,
              help='MATPOWER case file (.mat) path')
@click.option('--readings-path', type=Path,
              help="""Readings configuration file path. Requires CSV with
columns:

* meas_type - v (voltage), p (active power), q (reactive
power), i (current), va (voltage angle), or ia (current
angle)\n
* element_type - bus, line, trafo, or trafo3w (three-way
trafo)\n
* value - measurement amount - MW for p, MVar for q, 0 to 1 for
voltage (percentage of bus' voltage level), kA for i, and
radians for angles\n
* std_dev - measuring device standard deviation\n
* element - element ID in the given casefile (0-based index of
bus, line or trafo)\n
* side - if element is line, from or to, if trafo hv, mv, or lv
- represents the element segment to which the measurement
refers to. For other types of elements can be set to null\n
""")
@click.option('--output-path', type=Path,
              help='Output CSV file path')
@click.option('--models-path', type=Path, default=None,
              help=('Path to persisted pseudomeasurement generation models. '
                    'Point to a directory with files `p.pickle` and '
                    '`q.pickle`. Optional, if unset, internal models are '
                    'used.'))
def main(matpower_path, readings_path, output_path, models_path):
    """Based on given readings and network topology, attempts to approximate
    physical states of all topological nodes in the network. Writes to the
    output path a CSV table containing the following columns:

        * vm_pu - voltage amount, expressed as a percentage of bus' voltage
        level\n
        * va_degree - voltage angle in radians\n
        * p_mw - active power on the bus\n
        * q_mvar - reactive power on the bus\n

    Table rows represent a single bus, ordered in the same way buses are
    ordered in the case file.
    """
    network = pandapower.converter.from_mpc(str(matpower_path))
    measurements = pandas.read_csv(readings_path)

    missing = set()
    for bus_id in network.bus.name:
        missing.add((bus_id, 'p'))
        missing.add((bus_id, 'q'))

    for _, measurement in measurements.iterrows():
        if measurement['element_type'] == 'bus':
            bus_id = measurement['element']
            meas_type = measurement['meas_type']
            if (bus_id, meas_type) in missing:
                missing.remove((bus_id, meas_type))
        pandapower.create_measurement(network, **measurement)
    missing = deque(sorted(missing))

    slacks = set()
    for bus_id in network.ext_grid.bus:
        if bus_id not in slacks:
            pandapower.create_measurement(network, 'v', 'bus', 1, 0.01, bus_id)
            slacks.add(bus_id)

    generator = attest.estimator.generator.Generator(network, models_path)
    while len(network.measurement) <= 2 * len(network.bus) - len(slacks):
        network = _network_reset(network)
        bus_id, meas_type = missing.popleft()
        value = generator.generate(bus_id, meas_type)
        mlog.info('bus %s - generated %s pseudomeasurement of value %s',
                  bus_id, meas_type, value)
        pandapower.create_measurement(network, meas_type, 'bus', value, 0.1,
                                      bus_id)

    if _estimation_attempt(network, output_path):
        return

    while missing:
        network = _network_reset(network)
        bus_id, meas_type = missing.popleft()
        value = generator.generate(bus_id, meas_type)
        mlog.info('bus %s - generated %s pseudomeasurement of value %s',
                  bus_id, meas_type, value)
        pandapower.create_measurement(network, meas_type, 'bus', value, 0.1,
                                      bus_id)
        if _estimation_attempt(network, output_path):
            return
    return -1


def _network_reset(network):
    network_old = network
    network = pandapower.create_empty_network()
    network.bus = network_old.bus
    network.line = network_old.line
    network.trafo = network_old.trafo
    network.ext_grid = network_old.ext_grid
    network.sgen = network_old.sgen
    network.load = network_old.load
    network.measurement = network_old.measurement
    return network


def _estimation_attempt(network, output_path):
    mlog.info('attempting estimation with %s measurements',
              len(network.measurement))
    try:
        if pandapower.estimation.estimate(network):
            mlog.info('estimation successful, writing output')
            network.res_bus_est.to_csv(output_path, index=False)
            return True
    except Exception as e:
        mlog.info('estimation failed %s', e)
    return False


if __name__ == '__main__':
    sys.exit(main())
