# add_admin.py
import mysql.connector
import sys

# This is a helper script to create the very first admin user from the command line.

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="306m.z.5",
        database="maintenance_db"
    )

def add_admin_user(username, password, department=None):
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT id FROM roles WHERE role_name = 'admin'")
        role = cur.fetchone()
        if not role:
            print("Error: 'admin' role not found in roles table.")
            return False
        role_id = role[0]

        cur.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            print(f"Error: Username '{username}' already exists.")
            return False

        cur.execute(
            "INSERT INTO users (username, password_hash, role_id, department) VALUES (%s, %s, %s, %s)",
            (username, password, role_id, department)
        )
        conn.commit()
        print(f"Successfully added admin user '{username}'.")
        return True
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return False
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python add_admin.py <username> <password> [department]")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]
    department = sys.argv[3] if len(sys.argv) > 3 else None

    add_admin_user(username, password, department)