# db_ops.py
import mysql.connector
from mysql.connector import pooling
from contextlib import contextmanager
import subprocess
import os
from datetime import datetime
import configparser
import sys

def get_base_path():
    """ Get the correct base path whether running as a script or a frozen exe."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

# --- FINAL DIAGNOSTIC BLOCK ---
base_path = get_base_path()
config_path = os.path.join(base_path, 'config.ini')

print("--- MAINTENANCE APP DIAGNOSTIC ---")
print(f"Executable is running from: {base_path}")

try:
    # List all files and folders in the directory
    print("\nFiles/Folders found in this directory:")
    for item in os.listdir(base_path):
        print(f"  - {item}")

    print(f"\nAttempting to read config file from: {config_path}")
    if os.path.exists(config_path):
        print("SUCCESS: config.ini was found!")
    else:
        print("FATAL ERROR: config.ini was NOT found in the directory.")

except Exception as e:
    print(f"An error occurred during diagnostics: {e}")

print("\n--- ATTEMPTING TO START APP ---")
# --- END OF DIAGNOSTIC BLOCK ---

config = configparser.ConfigParser()
config.read(config_path, encoding='utf-8')

DB_CONFIG = dict(
    host=config.get('database', 'host'),
    user=config.get('database', 'user'),
    password=config.get('database', 'password'),
    database=config.get('database', 'database'),
    charset=config.get('database', 'charset'),
    collation=config.get('database', 'collation'),
    use_pure=True # This tells the connector to use the pure Python version
)

# --- Create a Connection Pool for Stability ---
try:
    pool = pooling.MySQLConnectionPool(pool_name="mypool",
                                       pool_size=5,
                                       **DB_CONFIG)
except mysql.connector.Error as err:
    print(f"Error creating connection pool: {err}")
    pool = None

@contextmanager
def get_cursor():
    if not pool:
        raise Exception("Database connection pool is not available.")
    conn = pool.get_connection()
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

# --- BACKUP & RESTORE ---
def backup_database(output_path):
    try:
        cmd = ["mysqldump", f"--host={DB_CONFIG['host']}", f"--user={DB_CONFIG['user']}", f"--password={DB_CONFIG['password']}", "--single-transaction", "--routines", "--triggers", DB_CONFIG['database']]
        with open(output_path, 'w', encoding='utf-8') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return True, f"تم إنشاء النسخة الاحتياطية بنجاح في:\n{output_path}"
        else:
            return False, f"فشل النسخ الاحتياطي:\n{result.stderr.strip()}"
    except Exception as e:
        return False, f"حدث استثناء أثناء النسخ الاحتياطي:\n{str(e)}"

def restore_database(input_path):
    try:
        if not os.path.exists(input_path):
            return False, f"ملف النسخة الاحتياطية غير موجود: {input_path}"
        cmd = ["mysql", f"--host={DB_CONFIG['host']}", f"--user={DB_CONFIG['user']}", f"--password={DB_CONFIG['password']}", DB_CONFIG['database']]
        with open(input_path, 'r', encoding='utf-8') as f:
            result = subprocess.run(cmd, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return True, "تمت استعادة النسخة الاحتياطية بنجاح."
        else:
            return False, f"فشل استعادة النسخة الاحتياطية:\n{result.stderr.strip()}"
    except Exception as e:
        return False, f"حدث استثناء أثناء استعادة النسخة الاحتياطية:\n{str(e)}"

# --- ACTIVITY LOG ---
def log_activity(user_id, action, record_type, record_id=None, description=None):
    sql = "INSERT INTO activity_log (user_id, action, record_type, record_id, description) VALUES (%s, %s, %s, %s, %s)"
    with get_cursor() as cur:
        cur.execute(sql, (user_id, action, record_type, record_id, description or ""))

def fetch_activity_log(limit=100):
    sql = "SELECT al.id, u.username, al.action, al.record_type, al.record_id, al.description, al.timestamp FROM activity_log al LEFT JOIN users u ON al.user_id = u.id ORDER BY al.timestamp DESC LIMIT %s"
    with get_cursor() as cur:
        cur.execute(sql, (limit,))
        return cur.fetchall()

# --- CRUD maintenance ---
def insert_record(data, user_id):
    sql = "INSERT INTO maintenance (date, type, device, technician, procedures, materials, notes, warnings, department) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    with get_cursor() as cur:
        cur.execute(sql, data)
        new_record_id = cur.lastrowid
        log_activity(user_id, 'INSERT', 'maintenance', new_record_id, f"Added record for device: {data[2]}")
        return new_record_id

def fetch_records(department=None):
    with get_cursor() as cur:
        sql = "SELECT * FROM maintenance WHERE is_deleted = 0"
        params = []
        if department:
            sql += " AND department = %s"
            params.append(department)
        sql += " ORDER BY id DESC"
        cur.execute(sql, params)
        return cur.fetchall()

def update_record(rec_id, data, user_id):
    sql = "UPDATE maintenance SET date=%s, type=%s, device=%s, technician=%s, procedures=%s, materials=%s, notes=%s, warnings=%s, department=%s WHERE id=%s"
    with get_cursor() as cur:
        cur.execute(sql, (*data, rec_id))
        if cur.rowcount > 0:
            log_activity(user_id, 'UPDATE', 'maintenance', rec_id, f"Updated record for device: {data[2]}")

def delete_record(rec_id, user_id):
    with get_cursor() as cur:
        sql = "UPDATE maintenance SET is_deleted = 1 WHERE id = %s"
        cur.execute(sql, (rec_id,))
        if cur.rowcount > 0:
            log_activity(user_id, 'TRASH', 'maintenance', rec_id, f"Moved record to trash ID: {rec_id}")

# --- TRASH MANAGEMENT (Maintenance Records) ---
def fetch_deleted_records():
    with get_cursor() as cur:
        sql = "SELECT * FROM maintenance WHERE is_deleted = 1 ORDER BY id DESC"
        cur.execute(sql)
        return cur.fetchall()

def restore_record(rec_id, user_id):
    with get_cursor() as cur:
        sql = "UPDATE maintenance SET is_deleted = 0 WHERE id = %s"
        cur.execute(sql, (rec_id,))
        if cur.rowcount > 0:
            log_activity(user_id, 'RESTORE', 'maintenance', rec_id, f"Restored record from trash ID: {rec_id}")

def permanently_delete_record(rec_id, user_id):
    with get_cursor() as cur:
        cur.execute("DELETE FROM maintenance WHERE id=%s AND is_deleted = 1", (rec_id,))
        if cur.rowcount > 0:
            log_activity(user_id, 'DELETE', 'maintenance', rec_id, f"Permanently deleted record ID: {rec_id}")

# --- AUTH & USER MANAGEMENT ---
def verify_user(username, password):
    with get_cursor() as cur:
        cur.execute("SELECT id, role_id, department FROM users WHERE username=%s AND password_hash=%s AND is_deleted = 0", (username, password))
        return cur.fetchone()

def get_role_name_by_id(role_id):
    with get_cursor() as cur:
        cur.execute("SELECT role_name FROM roles WHERE id=%s", (role_id,))
        row = cur.fetchone()
        return row['role_name'] if row else None

def add_user(username, password, role_name, department, current_user_id):
    try:
        with get_cursor() as cur:
            cur.execute("SELECT id FROM roles WHERE role_name = %s", (role_name,))
            role = cur.fetchone()
            if not role: return False, "دور المستخدم غير موجود"
            role_id = role['id']
            cur.execute("SELECT id FROM users WHERE username=%s", (username,))
            if cur.fetchone(): return False, "اسم المستخدم موجود بالفعل"
            cur.execute("INSERT INTO users (username, password_hash, role_id, department) VALUES (%s, %s, %s, %s)", (username, password, role_id, department))
            new_user_id = cur.lastrowid
            log_activity(current_user_id, 'INSERT', 'user', new_user_id, f"Added user: {username} with role: {role_name}")
        return True, "تمت الإضافة بنجاح"
    except Exception as e:
        return False, str(e)

def update_user(user_id, role_name, department, new_password, current_user_id):
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
    sql = "SELECT u.id, u.username, r.role_name, u.department FROM users u JOIN roles r ON u.role_id = r.id WHERE u.is_deleted = 1 ORDER BY u.id"
    with get_cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()

def restore_user(user_id, admin_id):
    with get_cursor() as cur:
        cur.execute("UPDATE users SET is_deleted = 0 WHERE id = %s", (user_id,))
        if cur.rowcount > 0:
            log_activity(admin_id, 'RESTORE', 'user', user_id, f"Restored user from trash ID: {user_id}")

def permanently_delete_user(user_id, admin_id):
    with get_cursor() as cur:
        cur.execute("DELETE FROM users WHERE id = %s AND is_deleted = 1", (user_id,))
        if cur.rowcount > 0:
            log_activity(admin_id, 'DELETE', 'user', user_id, f"Permanently deleted user ID: {user_id}")

# --- ADMIN DASHBOARD HELPERS ---
def fetch_all_users():
    sql = "SELECT u.id, u.username, r.role_name, u.department FROM users u JOIN roles r ON u.role_id = r.id WHERE u.is_deleted = 0 ORDER BY u.id"
    with get_cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()

def get_total_record_count():
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS count FROM maintenance WHERE is_deleted = 0")
        result = cur.fetchone()
        return result['count'] if result else 0

def get_total_user_count():
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS count FROM users WHERE is_deleted = 0")
        result = cur.fetchone()
        return result['count'] if result else 0

def get_user_role_count(role_name):
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS count FROM users u JOIN roles r ON u.role_id = r.id WHERE r.role_name = %s AND u.is_deleted = 0", (role_name,))
        result = cur.fetchone()
        return result['count'] if result else 0

# --- DEPARTMENT MANAGEMENT ---
def get_all_departments():
    with get_cursor() as cur:
        cur.execute("SELECT name FROM departments ORDER BY name")
        return [row['name'] for row in cur.fetchall()]

def add_department(name, user_id):
    try:
        with get_cursor() as cur:
            cur.execute("INSERT INTO departments (name) VALUES (%s)", (name,))
            new_dept_id = cur.lastrowid
            log_activity(user_id, 'INSERT', 'department', new_dept_id, f"Added department: {name}")
            return True, "تمت إضافة القسم بنجاح."
    except mysql.connector.Error as err:
        if err.errno == 1062: return False, "هذا القسم موجود بالفعل."
        return False, str(err)

def update_department(department_id, new_name, user_id):
    try:
        with get_cursor() as cur:
            cur.execute("UPDATE departments SET name = %s WHERE id = %s", (new_name, department_id))
            log_activity(user_id, 'UPDATE', 'department', department_id, f"Renamed department to: {new_name}")
            return True, "تم تحديث القسم بنجاح."
    except mysql.connector.Error as err:
        if err.errno == 1062: return False, "اسم القسم هذا مستخدم بالفعل."
        return False, str(err)

def delete_department(department_id, user_id):
    try:
        with get_cursor() as cur:
            cur.execute("SELECT name FROM departments WHERE id = %s", (department_id,))
            dept_name = cur.fetchone()['name']
            cur.execute("SELECT COUNT(*) as count FROM users WHERE department = %s AND is_deleted = 0", (dept_name,))
            if cur.fetchone()['count'] > 0: return False, "لا يمكن حذف القسم لأنه معين لمستخدمين حاليين."
            cur.execute("SELECT COUNT(*) as count FROM maintenance WHERE department = %s AND is_deleted = 0", (dept_name,))
            if cur.fetchone()['count'] > 0: return False, "لا يمكن حذف القسم لأنه مستخدم في سجلات الصيانة."
            cur.execute("DELETE FROM departments WHERE id = %s", (department_id,))
            log_activity(user_id, 'DELETE', 'department', department_id, f"Deleted department: {dept_name}")
            return True, "تم حذف القسم بنجاح."
    except Exception as e:
        return False, str(e)

def get_department_id_by_name(name):
    with get_cursor() as cur:
        cur.execute("SELECT id FROM departments WHERE name = %s", (name,))
        result = cur.fetchone()
        return result['id'] if result else None

# --- ATTACHMENT MANAGEMENT ---
def add_attachment(maintenance_id, original_filename, stored_filepath, user_id):
    with get_cursor() as cur:
        sql = "INSERT INTO attachments (maintenance_id, original_filename, stored_filepath) VALUES (%s, %s, %s)"
        cur.execute(sql, (maintenance_id, original_filename, stored_filepath))
        new_attachment_id = cur.lastrowid
        log_activity(user_id, 'INSERT', 'attachment', new_attachment_id, f"Added attachment '{original_filename}' to maintenance record {maintenance_id}")
        return new_attachment_id

def get_attachments_for_record(maintenance_id):
    with get_cursor() as cur:
        sql = "SELECT id, original_filename, stored_filepath FROM attachments WHERE maintenance_id = %s ORDER BY id"
        cur.execute(sql, (maintenance_id,))
        return cur.fetchall()

def delete_attachment(attachment_id, user_id):
    try:
        with get_cursor() as cur:
            cur.execute("SELECT stored_filepath, original_filename, maintenance_id FROM attachments WHERE id = %s", (attachment_id,))
            attachment = cur.fetchone()
            if not attachment: return False, "Attachment not found."
            if os.path.exists(attachment['stored_filepath']):
                os.remove(attachment['stored_filepath'])
            cur.execute("DELETE FROM attachments WHERE id = %s", (attachment_id,))
            if cur.rowcount > 0:
                log_activity(user_id, 'DELETE', 'attachment', attachment_id, f"Removed attachment '{attachment['original_filename']}' from maintenance record {attachment['maintenance_id']}")
                return True, "Attachment deleted successfully."
            else:
                return False, "Failed to delete attachment record from database."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"

# --- RECORD HISTORY ---
def get_history_for_record(record_id):
    sql = "SELECT u.username, al.action, al.description, al.timestamp FROM activity_log al LEFT JOIN users u ON al.user_id = u.id WHERE al.record_type = 'maintenance' AND al.record_id = %s ORDER BY al.timestamp DESC"
    with get_cursor() as cur:
        cur.execute(sql, (record_id,))
        return cur.fetchall()

# --- ADVANCED SEARCH ---
def search_records_advanced(filters):
    base_sql = "SELECT * FROM maintenance WHERE is_deleted = 0"
    params = []
    
    if filters.get('date_from') and filters.get('date_to'):
        base_sql += " AND date BETWEEN %s AND %s"
        params.extend([filters['date_from'], filters['date_to']])

    if filters.get('department'):
        base_sql += " AND department = %s"
        params.append(filters['department'])

    if filters.get('keyword'):
        kw = f"%{filters['keyword']}%"
        base_sql += " AND (device LIKE %s OR procedures LIKE %s OR materials LIKE %s OR notes LIKE %s OR warnings LIKE %s)"
        params.extend([kw] * 5)

    base_sql += " ORDER BY id DESC"
    
    with get_cursor() as cur:
        cur.execute(base_sql, params)
        return cur.fetchall()

# --- REPORTS/DASHBOARD ---
def get_records_count_in_period(date_from, date_to, department=None):
    sql = "SELECT COUNT(*) AS count FROM maintenance WHERE is_deleted = 0 AND date BETWEEN %s AND %s"
    params = [date_from, date_to]
    if department:
        sql += " AND department = %s "
        params.append(department)
    with get_cursor() as cur:
        cur.execute(sql, params)
        result = cur.fetchone()
        return result['count'] if result else 0

def get_avg_records_per_day(date_from, date_to, department=None):
    try:
        dt_from = datetime.strptime(date_from, "%Y-%m-%d")
        dt_to = datetime.strptime(date_to, "%Y-%m-%d")
        delta_days = (dt_to - dt_from).days + 1
        if delta_days <= 0: return 0
    except ValueError:
        return 0
    total_count = get_records_count_in_period(date_from, date_to, department)
    return total_count / delta_days if total_count > 0 else 0

def get_records_per_department(date_from, date_to):
    sql = "SELECT department, COUNT(*) AS count FROM maintenance WHERE is_deleted = 0 AND date BETWEEN %s AND %s GROUP BY department ORDER BY count DESC"
    with get_cursor() as cur:
        cur.execute(sql, (date_from, date_to))
        return cur.fetchall()

def get_device_type_counts(date_from, date_to, department=None):
    sql = "SELECT type AS device_type, COUNT(*) AS count FROM maintenance WHERE is_deleted = 0 AND date BETWEEN %s AND %s"
    params = [date_from, date_to]
    if department:
        sql += " AND department = %s "
        params.append(department)
    sql += " GROUP BY type ORDER BY count DESC"
    with get_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()

def get_technician_counts(date_from, date_to, department=None):
    sql = "SELECT technician, COUNT(*) AS count FROM maintenance WHERE is_deleted = 0 AND date BETWEEN %s AND %s"
    params = [date_from, date_to]
    if department:
        sql += " AND department = %s "
        params.append(department)
    sql += " GROUP BY technician ORDER BY count DESC"
    with get_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()