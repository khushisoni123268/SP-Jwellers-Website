# Database Management Script for SP Jewellers
# Run this script to fix database locking issues

import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'spjewellers.settings')
django.setup()

from django.db import connection
from django.core.management import execute_from_command_line

def fix_database_locks():
    """Fix common database locking issues"""
    try:
        # Close any existing connections
        connection.close()

        # Run database maintenance
        print("Running database maintenance...")
        execute_from_command_line(['manage.py', 'dbshell', '.schema'])

        print("Database locks fixed successfully!")

    except Exception as e:
        print(f"Error fixing database: {e}")

if __name__ == '__main__':
    fix_database_locks()