State estimator
===============

ATTEST state estimator is a tool for approximating global system physical state
based on a subset of available measurements. It attempts different kinds of
approximation in order to successfully generate a result. The estimation method
used is weighted least squares with Gauss-Newton optimization. Since this
method has a requirement for a minimal amount of measurements that need to be
provided in order for the system to be observable, a pseudomeasurement
generator is introduced, which attempts to add additional measurements based on
day of week, time when estimation is assessed, etc.

How to use
----------

Estimator is implemented as a command line program. It has the following
interface:

.. program-output:: python -m attest.estimator --help

For more information on measurement input CSV, consult the `estimator
documentation_`, as the table rows are mostly passed as-is to the tool.

.. _estimator documentation: https://pandapower.readthedocs.io/en/v2.6.0/elements/measurement.html#pandapower.create_measurement

An example is given in the repo, directory examples. Estimator can be ran with
the following command:

.. code-block:: bash

    python -m attest.estimator \\
            --matpower-path examples/network.mat \\
            --readings-path examples/measurements.csv \\
            --output-path examples/output.csv

This will write the estimates into `examples/output.csv`.
