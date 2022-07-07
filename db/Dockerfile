FROM postgres:14.1

USER postgres

COPY cimrepodb.sql .
COPY dump.sql .
COPY db_setup.sh /docker-entrypoint-initdb.d/
