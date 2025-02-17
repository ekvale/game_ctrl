import time
import psycopg2
from django.db import connections
from django.db.utils import OperationalError

print("Waiting for database...")

while True:
    try:
        connections['default'].cursor()
        print("Database is ready!")
        break
    except OperationalError:
        print("Database unavailable, waiting 2 seconds...")
        time.sleep(2)

