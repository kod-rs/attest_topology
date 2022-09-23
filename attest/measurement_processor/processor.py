from pathlib import Path
import click
import pandapower
import pandas
import sys


@click.command()
@click.option('--matpower-path', type=Path,
              help='MATPOWER case file (.mat) path')
@click.option('--readings-path', type=Path,
              help='Readings configuration file path')
def main(matpower_path, readings_path):
    """Based on given readings and network topology, attempts to approximate
    physical states of all topological nodes in the network. Writes to standard
    output a single table containing the following columns:

        * a - column is x
        * b - column represents y
        ..."""
    network = pandapower.converter.from_mpc(str(matpower_path))
    measurements = pandas.read_csv(readings_path)

    for _, measurement in measurements.iterrows():
        pandapower.create_measurement(network, **measurement)


if __name__ == '__main__':
    sys.exit(main())
