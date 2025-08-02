# /database/user_queries.py

# We need the get_cursor function from our connection module
from .connection import get_cursor

# For now, we will import log_activity from the main db_ops.
# We will clean this up in a later step.
# Change this line in /database/user_queries.py
from .utility_queries import log_activity

# --- AUTH & USER MANAGEMENT ---
def verify_user(username, password):
    """Verifies a user's credentials against the database."""
    with get_cursor() as cur:
        cur.execute("SELECT id, role_id, department FROM users WHERE username=%s AND password_hash=%s AND is_deleted = 0", (username, password))
        return cur.fetchone()

def get_role_name_by_id(role_id):
    """Retrieves the name of a role by its ID."""
    with get_cursor() as cur:
        cur.execute("SELECT role_name FROM roles WHERE id=%s", (role_id,))
        row = cur.fetchone()
        return row['role_name'] if row else None

def add_user(username, password, role_name, department, current_user_id):
    """Adds a new user to the database."""
    try:
        with get_cursor() as cur:
            cur.execute("SELECT id FROM roles WHERE role_name = %s", (role_name,))
            role = cur.fetchone()
            if not role: return False, "دور المستخدم غير موجود"
            
            role_id = role['id']
            cur.execute("SELECT id FROM users WHERE username=%s AND is_deleted = 0", (username,))
            if cur.fetchone(): return False, "اسم المستخدم موجود بالفعل"
            
            cur.execute("INSERT INTO users (username, password_hash, role_id, department) VALUES (%s, %s, %s, %s)", (username, password, role_id, department))
            new_user_id = cur.lastrowid
            log_activity(current_user_id, 'INSERT', 'user', new_user_id, f"Added user: {username} with role: {role_name}")
            return True, "تمت الإضافة بنجاح"
    except Exception as e:
        return False, str(e)

def update_user(user_id, role_name, department, new_password, current_user_id):
    """Updates a user's details."""
    try:
        with get_cursor() as cur:
            cur.execute("SELECT id FROM roles WHERE role_name = %s", (role_name,))
            role = cur.fetchone()
            if not role: return False, "الدور المحدد غير صالح."
            role_id = role['id']

            if new_password:
                sql = "UPDATE users SET role_id=%s, department=%s, password_hash=%s WHERE id=%s"
                params = (role_id, department, new_password, user_id)
                log_description = f"Updated user ID {user_id} (department, role, password)"
            else:
                sql = "UPDATE users SET role_id=%s, department=%s WHERE id=%s"
                params = (role_id, department, user_id)
                log_description = f"Updated user ID {user_id} (department, role)"
            
            cur.execute(sql, params)
            log_activity(current_user_id, 'UPDATE', 'user', user_id, log_description)
            return True, "تم تحديث المستخدم بنجاح."
    except Exception as e:
        return False, f"فشل تحديث المستخدم: {str(e)}"

def delete_user(user_id_to_delete, current_user_id):
    """Soft-deletes a user."""
    if user_id_to_delete == current_user_id:
        return False, "لا يمكنك حذف حسابك الخاص."
    try:
        with get_cursor() as cur:
            cur.execute("UPDATE users SET is_deleted = 1 WHERE id = %s", (user_id_to_delete,))
            if cur.rowcount > 0:
                log_activity(current_user_id, 'TRASH', 'user', user_id_to_delete, f"Moved user to trash ID: {user_id_to_delete}")
                return True, "تم نقل المستخدم إلى سلة المحذوفات."
            else:
                return False, "لم يتم العثور على المستخدم."
    except Exception as e:
        return False, f"فشل حذف المستخدم: {str(e)}"

# --- TRASH MANAGEMENT (Users) ---
def fetch_deleted_users():
    """Fetches all soft-deleted users."""
    sql = "SELECT u.id, u.username, r.role_name, u.department FROM users u JOIN roles r ON u.role_id = r.id WHERE u.is_deleted = 1 ORDER BY u.id"
    with get_cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()

def restore_user(user_id, admin_id):
    """Restores a soft-deleted user."""
    with get_cursor() as cur:
        cur.execute("UPDATE users SET is_deleted = 0 WHERE id = %s", (user_id,))
        if cur.rowcount > 0:
            log_activity(admin_id, 'RESTORE', 'user', user_id, f"Restored user from trash ID: {user_id}")

def permanently_delete_user(user_id, admin_id):
    """Permanently deletes a user from the database."""
    with get_cursor() as cur:
        cur.execute("DELETE FROM users WHERE id = %s AND is_deleted = 1", (user_id,))
        if cur.rowcount > 0:
            log_activity(admin_id, 'DELETE', 'user', user_id, f"Permanently deleted user ID: {user_id}")


# --- ADMIN DASHBOARD HELPERS (User-related) ---
def fetch_all_users():
    """Fetches all active users."""
    sql = "SELECT u.id, u.username, r.role_name, u.department FROM users u JOIN roles r ON u.role_id = r.id WHERE u.is_deleted = 0 ORDER BY u.id"
    with get_cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()