from django.test import TestCase
from django.db import connection

class DatabaseConnectionTest(TestCase):
    def test_database_connection(self):
        """Check if database connection is working"""
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            self.assertEqual(cursor.fetchone()[0], 1)

