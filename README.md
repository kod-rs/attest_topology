# ATTEST tools

Repository containing varios tools useful in the ATTEST project. To set
everything up, python requirements need to be installed:

```bash
pip install -r requirements.txt
```

## Topological processor

A library that provides functions and classes that allow users to connect to a
CIM record database and generate an admittance matrix of all connectivity nodes
in the system. A connectivity node is a group of network elements like buses. A
topologically processed network is a graph where vertices are the connectivity
nodes and the edges are admittances of the lines that connect them.

### Requirements

Topological processor is implemented as a Python package. It assumes there is a
live PostgreSQL database running that contains CIM records. It also assumes
that the database contains a function:

```sql
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
```

### How to use

The topology package contains several modules that can be called as entry
points over a terminal. Use the following command:

```bash
python -m attest.topology.<module_name> --help
```

This will print out the help prompt with further information.

## ATTEST server

The server provides the topological processor functions as a web service.
Endpoints:

`/api`

Only supports GET requests with the following parameters:
    * `branch_id` - CIM branch ID of the requested state
    * `commit_id` - CIM commit ID of the requested state

Result is a JSON representation of the admittance matrix, whose structure
respects the following JSON schema:

```yaml
---
type: object
required:
    - branch_id
    - commit_id
    - datetime
    - admittance_sparse_matrix
    - topological_nodes
properties:
    branch_id:
        type: int
        description: CIM repo branch id
    commit_id:
        type: int
        description: CIM repo commit id
    datetime:
        type: int
        description: UNIX timestamp of the time when the snapshot was taken
    admittance_sparse_matrix:
        type: array
        items:
            type: object
            description: |
                Sparse matrix, represents connection between the topological
                node at row and col, with the admittance value. Rows and cols
                are indices of topological nodes under the topologlical_nodes
                property.
            required:
                - row
                - col
                - value
            properties:
                row:
                    type: int
                col:
                    type: int
                value:
                    type: array
                    maxContains: 2
                    description: |
                        complex number, first value is the real and second is
                        the imaginary segment
                    items:
                    type: float
    topological_nodes:
        type: array
        items:
            type: array
            maxContains: 2
            description: |
                pair of topological node UUID (first UUID in the group by
                lexicographic order) and all element UUIDs belonging to that
                node
            prefixItems:
              - type: string
                description: UUID, topological node id
              - type: array
                description: |
                    ids of all elements belonging to the topological node
                items:
                    type: string
                    description: UUID
...
```

Example request and response:

Request:

`GET /api/branch_id=4&commit_id=1`

Response:

```json
{
	"branch_id": 4,
	"commit_id": 1,
	"timestamp": 1664181352,
	"admittance_sparse_matrix": [
		{"row": 0, "col": 1, "value": [1.1, 2.2]},
		{"row": 3, "col": 4, "value": [5.3, 7.1]},
	],
	"topological_nodes": [
		["c134850a-3d76-11ed-b16f-201e88d11df2", [
			"c134850a-3d76-11ed-b16f-201e88d11df2",
			"d05c1944-3d76-11ed-b16f-201e88d11df2"]],
		["f4d6681a-3d76-11ed-b16f-201e88d11df2", [
			"f4d6681a-3d76-11ed-b16f-201e88d11df2"]],
		["0bf53f62-3d77-11ed-b16f-201e88d11df2", [
			"0bf53f62-3d77-11ed-b16f-201e88d11df2"]],
		["16094d7c-3d77-11ed-b16f-201e88d11df2", [
			"16094d7c-3d77-11ed-b16f-201e88d11df2"]],
		["234b67ea-3d77-11ed-b16f-201e88d11df2", [
			"234b67ea-3d77-11ed-b16f-201e88d11df2"]]
	]
}
```

This could be interpreted as the following admittance matrix:

```
0          1.1 + 2.2j 0          0          0
1.1 + 2.2j 0          0          0          0
0          0          0          0          0
0          0          0          0          5.3 + 7.1j
0          0          0          5.3 + 7.1j 0
```

Furhtermore, adding the `topological_nodes` interpretation we can see that the
node `c134850a-3d76-11ed-b16f-201e88d11df2` and
`f4d6681a-3d76-11ed-b16f-201e88d11df2` are connected with admittance of `1.1 +
2.2j`, and `16094d7c-3d77-11ed-b16f-201e88d11df2` is connected with
`234b67ea-3d77-11ed-b16f-201e88d11df2` with admittance of `5.3 + 2.2j`.
Admittance matrix is always symmetrical so there is no need to list the node
pairings under the diagonal.

## State estimator

ATTEST state estimator is a tool for approximating global system physical state
based on a subset of available measurements. It attempts different kinds of
approximation in order to successfully generate a result. The estimation method
used is weighted least squares with Gauss-Newton optimization. Since this
method has a requirement for a minimal amount of measurements that need to be
provided in order for the system to be observable, a pseudomeasurement
generator is introduced, which attempts to add additional measurements based on
day of week, time when estimation is assessed, etc.

### How to use

Estimator is implemented as a command line program. It has the following
interface:

`call pyhton -m attest.estimator --help`

For more information on measurement input CSV, consult the [estimator
documentation](https://pandapower.readthedocs.io/en/v2.6.0/elements/measurement.html#pandapower.create_measurement),
as the table rows are mostly passed as-is to the tool.

An example is given in the repo, directory examples. Estimator can be ran with
the following command:

```bash
python -m attest.estimator \\
	--matpower-path examples/network.mat \\
	--readings-path examples/measurements.csv \\
	--output-path examples/output.csv
```

This will write the estimates into `examples/output.csv`.
