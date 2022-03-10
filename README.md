# ATTEST topology
Topological processor for the ATTEST project

## Requirements

Topological processor is implemented as a Python package. It assumes there is a
live PostgreSQL database running that contains CIM records. It also assumes
that the database contains a function

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

Additionally, the topological processor has some Python dependencies, which can
be installed by calling:

```bash
pip install -r requirements.txt
```

## How to use

The topology package contains several modules that can be called as entry
points over a terminal. Use the following command:

```bash
python -m attest.<module_name> --help
```

This will print out the help prompt with further information.
