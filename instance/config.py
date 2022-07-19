import os


DB_HOST = os.environ.get('DB_HOST') or 'localhost'
DB_PORT = os.environ.get('DB_PORT') or 5432
DB_USER = os.environ.get('DB_USER') or 'postgres'
DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'pass'
DB_NAME = os.environ.get('DB_NAME') or 'cimrepokc'
