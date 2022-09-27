ATTEST server
=============

The server provides the topological processor functions as a web service.
Endpoints:

``/api``

Only supports GET requests with the following parameters:
    * `branch_id` - CIM branch ID of the requested state
    * `commit_id` - CIM commit ID of the requested state

Result is a JSON representation of the admittance matrix, whose structure
respects the following JSON schema:

.. code-block:: yaml

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

Example request and response:

Request:

``GET /api/branch_id=4&commit_id=1``

Response:

.. code-block:: json

    {
        "branch_id": 4,
        "commit_id": 1,
        "timestamp": 1664181352,
        "admittance_sparse_matrix": [
            {"row": 0, "col": 0, "value": [-1.1, -2.2]},
            {"row": 0, "col": 1, "value": [1.1, 2.2]},
            {"row": 1, "col": 1, "value": [-1.1, -2.2]},
            {"row": 1, "col": 0, "value": [1.1, 2.2]},
            {"row": 3, "col": 3, "value": [-5.3, -7.1]},
            {"row": 3, "col": 4, "value": [5.3, 7.1]},
            {"row": 4, "col": 3, "value": [5.3, 7.1]},
            {"row": 4, "col": 4, "value": [-5.3, -7.1]},
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

This could be interpreted as the following admittance matrix::

    -1.1 - 2.2j 1.1 + 2.2j  0          0           0
    1.1 + 2.2j  -1.1 - 2.2j 0          0           0
    0           0           0          0           0
    0           0           0          -5.3 - 7.1j 5.3 + 7.1j
    0           0           0          5.3 + 7.1j  -5.3 - 7.1j

Furhtermore, adding the ``topological_nodes`` interpretation we can see that
the node ``c134850a-3d76-11ed-b16f-201e88d11df2`` and
``f4d6681a-3d76-11ed-b16f-201e88d11df2`` are connected with admittance of ``1.1
+ 2.2j``, and ``16094d7c-3d77-11ed-b16f-201e88d11df2`` is connected with
``234b67ea-3d77-11ed-b16f-201e88d11df2`` with admittance of ``5.3 + 2.2j``.
Lastly, the values on the diagonal the represent shunt values of the individual
nodes.
