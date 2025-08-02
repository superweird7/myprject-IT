# db_ops.py

"""
This module serves as a single, convenient entry point for the UI to access
all database operations. It aggregates functions from the specialized modules
in the 'database' package, providing a simplified facade.

This prevents circular dependencies and keeps the project structure clean.
The UI layer should only need to import this file to get access to any
database-related function it needs.
"""

# Import all functions from the specialized query modules so they are
# available to the rest of the application from a single namespace.
from database.connection import *
from database.user_queries import *
from database.record_queries import *
from database.utility_queries import *