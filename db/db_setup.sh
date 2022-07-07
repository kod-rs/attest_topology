#!/bin/bash

set -e

psql << EOF
create database cimrepokc WITH ENCODING = 'UTF8' owner='postgres';
\c cimrepokc postgres
create schema repo;
set search_path to repo;

\i cimrepodb.sql
\i dump.sql
EOF
