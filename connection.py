# /database/connection.py

import mysql.connector
from mysql.connector import pooling
from contextlib import contextmanager
import configparser
import os
import sys

def get_base_path():
    """ Get the correct base path whether running as a script or a frozen exe."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        # For a script, we need to go up one level from /database
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Configuration Setup ---
base_path = get_base_path()
config_path = os.path.join(base_path, 'config.ini')

# Read configuration file
config = configparser.ConfigParser()
config.read(config_path, encoding='utf-8')

# --- Database Connection Pool ---
_pool = None

def init_connection_pool():
    """Initializes the database connection pool."""
    global _pool
    if _pool is None:
        try:
            db_config = dict(
                host=config.get('database', 'host'),
                user=config.get('database', 'user'),
                password=config.get('database', 'password'),
                database=config.get('database', 'database'),
                charset=config.get('database', 'charset'),
                collation=config.get('database', 'collation'),
                use_pure=True
            )
            _pool = pooling.MySQLConnectionPool(pool_name="mypool",
                                                  pool_size=5,
                                                  **db_config)
            print("Database connection pool initialized successfully.")
        except mysql.connector.Error as err:
            print(f"Error creating connection pool: {err}")
            _pool = None
        except Exception as e:
            print(f"An unexpected error occurred during pool initialization: {e}")
            _pool = None

def get_db_config():
    """Returns the database configuration dictionary."""
    return dict(config.items('database'))


@contextmanager
def get_cursor():
    """
    Provides a database cursor from the connection pool.
    Handles connection acquisition, commit, rollback, and release.
    """
    if _pool is None:
        init_connection_pool() # Initialize the pool if it's not ready

    if not _pool:
        raise Exception("Database connection pool is not available. Check configuration.")

    conn = _pool.get_connection()
    cur = conn.cursor(dictionary=True)
    try:
        yield cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

# Initialize the pool when the module is loaded
init_connection_pool()