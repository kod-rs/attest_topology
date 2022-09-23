from collections import deque
from pathlib import Path
import click
import pandapower.estimation
import pandas
import sys

import attest.estimator.generator


pandapower.logger.disabled = True


@click.command()
@click.option('--matpower-path', type=Path,
              help='MATPOWER case file (.mat) path')
@click.option('--readings-path', type=Path,
              help='Readings configuration file path')
@click.option('--output-path', type=Path,
              help='Output CSV file path')
@click.option('--models-path', type=Path, default=None,
              help=('Path to persisted pseudomeasurement generation models. '
                    'Point to a directory with files `p.model` and `q.model`. '
                    'Optional, if unset, internal models are used.'))
def main(matpower_path, readings_path, output_path, models_path):
    """Based on given readings and network topology, attempts to approximate
    physical states of all topological nodes in the network. Writes to the
    output path a CSV table containing the following columns:

        * a - column is x
        * b - column represents y
        ..."""
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

    if _estimation_attempt(network, output_path):
        return

    generator = attest.estimator.generator.Generator(network, models_path)
    while missing:
        network = _network_reset(network)
        bus_id, meas_type = missing.popleft()
        value = generator.generate(bus_id, meas_type)
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
    try:
        if pandapower.estimation.estimate(network):
            network.res_bus_est.to_csv(output_path, index=False)
            return True
    except Exception:
        pass
    return False


if __name__ == '__main__':
    sys.exit(main())
