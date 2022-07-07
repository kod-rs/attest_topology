"""Module in charge of database interactions"""
from typing import Optional
import click
import contextlib
import datetime
import getpass
import psycopg2
import psycopg2.extras
import sys


psycopg2.extras.register_uuid()


class Connection:

    """Represents a connection to the database

    Args:
        dbname: database name"""

    def __init__(self,
                 dbname: str,
                 host: str = '127.0.0.1',
                 port: int = 5432,
                 user: Optional[str] = 'postgres',
                 password: Optional[str] = None):
        if password is None:
            password = getpass.getpass(f'Password for Postgres user {user}: ')
        conn_string = (f"host={host} "
                       f"port={port} "
                       f"password={password} "
                       f"user={user} "
                       f"dbname={dbname}")
        self._conn_string = conn_string
        self._connection = None

    def connect(self):
        """Connect to the database"""
        if self._connection is not None:
            return
        self._connection = psycopg2.connect(self._conn_string)
        self._cursor = self._connection.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor)
        self._cursor.execute("SET search_path TO repo;")

    def disconnect(self):
        """Disconnect from the database"""
        self._cursor.close()
        self._connection.close()
        self._connection = None
        self._cursor = None

    def recordat(self,
                 last_branch_id: Optional[int] = None,
                 last_commit_id: Optional[int] = None,
                 last_valid_time: Optional[datetime.datetime] = None,
                 cim_class_ids: Optional[list[int]] = None,
                 hmrids: Optional[list[str]] = None,
                 mrids: Optional[list[str]] = None,
                 pmrids: Optional[list[str]] = None,
                 rnamelikes: Optional[str] = None
                 ) -> list:
        """Searches CIM records using given arguments

        Args:
            last_branch_id: last branch id
            last_commit_id: last commit id
            last_valid_time: last valid time - if not already, converted to UTC
            cim_class_ids: cim class ids
            hmrids: hmrids
            mrids: mrids
            pmrids: pmrids
            rnamelikes: rnamelikes

        Returns:
            List of rows
        """
        if not self._connection:
            raise Exception('not connected to the database')

        if last_valid_time is not None:
            last_valid_time = last_valid_time.astimezone(datetime.timezone.utc)
            last_valid_time = last_valid_time.replace(tzinfo=None)

        self._cursor.execute(
            "SELECT mrid, rname, cimclassid, cimclass, pmrid, fullobject "
            "FROM repo.recordat(%s, %s, %s, %s, %s, %s, %s, %s);",
            (last_branch_id, last_commit_id, last_valid_time,
             cim_class_ids, hmrids, mrids, pmrids, rnamelikes))
        return self._cursor.fetchall()

    def snapshot(self, branch_id: int, commit_id: int) -> dict[str, int]:
        """Retrieves a CIM snapshot

        Args:
            branch_id: branch id
            commit_id: commit id

        Returns:
            Mapping MRID -> state
        """

        self._cursor.execute(
            "SELECT mrids, intvalues FROM repo.snapshot_t "
            "WHERE branchid=%s AND commitid=%s",
            (branch_id, commit_id))
        data = self._cursor.fetchall()
        if not data:
            return {}
        snapshot = {}
        for mrid, value in zip(data[0]['mrids'], data[0]['intvalues']):
            snapshot[str(mrid)] = value
        return snapshot

    def get_classes(self) -> list:
        """Fetch all classes in the database

        Returns:
            List of database rows containing all the classes"""

        if not self._connection:
            raise Exception('not connected to the database')

        self._cursor.execute("SELECT cimclassid, cimclass "
                             "FROM repo.cimclass_t")
        return self._cursor.fetchall()


@contextlib.contextmanager
def connect(dbname: str):
    """Context manager for a database connection

    Args:
        dbname: database name"""
    connection = Connection(dbname)
    connection.connect()
    yield connection
    connection.disconnect()


@click.command()
@click.option('--dbname', help='name of the cim database', required=True)
def main(dbname):
    with connect(dbname) as c:
        print(c.recordat(4, 1, datetime.datetime.now(datetime.timezone.utc),
                         [519]))


if __name__ == '__main__':
    sys.exit(main())
