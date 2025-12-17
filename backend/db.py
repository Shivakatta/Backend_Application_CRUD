import mysql.connector
from mysql.connector import errorcode

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Shiva@366",
    "database": "users_data",
    # short connection timeout to avoid long blocking on startup when MySQL is unreachable
    "connection_timeout": 5,
}

def get_db():
    """Return a new MySQL connection using the configured credentials."""
    # Use explicit connection_timeout from config to avoid long hangs
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    """Ensure the database and `users` table exist.

    Tries to connect to the configured database; if it does not exist,
    creates it and then ensures the `users` table is present.
    """
    db_name = DB_CONFIG.get("database")
    cfg_no_db = DB_CONFIG.copy()
    cfg_no_db.pop("database", None)

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        # If the database does not exist, create it (connect without database)
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            try:
                cfg = cfg_no_db.copy()
                # include same timeout when creating the database
                if "connection_timeout" in DB_CONFIG:
                    cfg["connection_timeout"] = DB_CONFIG["connection_timeout"]
                conn = mysql.connector.connect(**cfg)
                cur = conn.cursor()
                cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
                conn.commit()
                cur.close()
                conn.close()
                conn = mysql.connector.connect(**DB_CONFIG)
            except Exception:
                # re-raise original error if we cannot create DB
                raise
        else:
            # re-raise other errors (e.g., cannot reach server)
            raise

    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100),
        email VARCHAR(100),
        password VARCHAR(255)
    )
    """)
    conn.commit()
    # Ensure password column exists for older schemas
    try:
        cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS password VARCHAR(255)")
        conn.commit()
    except Exception:
        # ALTER ... IF NOT EXISTS may not be supported; ignore if it fails
        pass
    cur.close()
    conn.close()
