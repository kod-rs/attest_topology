Processor implementation
========================

A library that provides functions and classes that allow users to connect to a
CIM record database and generate an admittance matrix of all connectivity nodes
in the system. This implementation follows the pseudocodes proposed in the
previous section, with a minor difference in the way the merge map is handled -
here in the admittance matrix calculation, the connectivity map is mostly used,
as it contains similar information in a more condensed structure. Functionally,
there should be no difference in the final admittance matrix.

A connectivity node is a group of network elements like buses. A topologically
processed network is a graph where vertices are the connectivity nodes and the
edges are admittances of the lines that connect them.

Requirements
------------

Topological processor is implemented as a Python package. It assumes there is a
live PostgreSQL database running that contains CIM records. It also assumes
that the database contains a function:

.. code-block:: sql

        recordat(lastbranchid integer,
                 lastcommitid integer,
                 lastvalidtime timestamp without time zone,
                 cimclassids int4[],
                 hmrids uuid[],
                 mrids uuid[],
                 pmrids uuid[],
                 rnamelikes text[])
        returns table(mrid uuid,
                      mridtext text,
                      rname text,
                      cimclassid integer,
                      cimclass text,
                      pmrid uuid,
                      fullobject jsonb)

How to use
----------

The topology package contains several modules that match the steps in topology
processing. These modules are:

  * ``db`` - handles database communication, provides a connection object that
    has methods for connecting and executing common queries
  * ``unprocessed`` - initializes data structures and different maps needed for
    the processing algorithm
  * ``node_breaker`` - implementation of the first algorithm segment, which
    detects connectivity nodes by analyzing switch positions
  * ``node_branch`` - implementation of the second algorithm segment, detects
    line admittances and generates an admittance matrix between the
    connectivity nodes

Every module has its interface that the other modules use, those are analyzed
in the following subsections.

.. automodule:: attest.topology

``db``
''''''

.. program-output:: python -m attest.topology.db --help

.. automodule:: attest.topology.db
   :members:

``unprocessed``
'''''''''''''''

.. automodule:: attest.topology.unprocessed
   :members:

``node_breaker``
''''''''''''''''

.. program-output:: python -m attest.topology.node_breaker --help

.. automodule:: attest.topology.node_breaker
   :members:

``node_branch``
'''''''''''''''

.. program-output:: python -m attest.topology.node_branch --help

.. automodule:: attest.topology.node_branch
   :members:
