# /database/utility_queries.py

import subprocess
import os
from datetime import datetime
import mysql.connector
from .connection import get_cursor, get_db_config

# --- ACTIVITY LOG ---
def log_activity(user_id, action, record_type, record_id=None, description=None):
    """Logs a user's action to the activity_log table."""
    sql = "INSERT INTO activity_log (user_id, action, record_type, record_id, description) VALUES (%s, %s, %s, %s, %s)"
    with get_cursor() as cur:
        cur.execute(sql, (user_id, action, record_type, record_id, description or ""))

def fetch_activity_log(limit=100):
    """Fetches the latest activity logs."""
    sql = """
        SELECT al.id, u.username, al.action, al.record_type, al.record_id, al.description, al.timestamp
        FROM activity_log al LEFT JOIN users u ON al.user_id = u.id
        ORDER BY al.timestamp DESC LIMIT %s
    """
    with get_cursor() as cur:
        cur.execute(sql, (limit,))
        return cur.fetchall()

# --- BACKUP & RESTORE ---
def backup_database(output_path):
    """Creates a backup of the database using mysqldump."""
    try:
        db_config = get_db_config()
        cmd = [
            "mysqldump", f"--host={db_config['host']}", f"--user={db_config['user']}",
            f"--password={db_config['password']}", "--single-transaction",
            "--routines", "--triggers", db_config['database']
        ]
        with open(output_path, 'w', encoding='utf-8') as f:
            result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True, check=False)
        if result.returncode == 0:
            return True, f"تم إنشاء النسخة الاحتياطية بنجاح في:\n{output_path}"
        else:
            return False, f"فشل النسخ الاحتياطي:\n{result.stderr.strip()}"
    except Exception as e:
        return False, f"حدث استثناء أثناء النسخ الاحتياطي:\n{str(e)}"

def restore_database(input_path):
    """Restores the database from a backup file."""
    try:
        if not os.path.exists(input_path):
            return False, f"ملف النسخة الاحتياطية غير موجود: {input_path}"
        db_config = get_db_config()
        cmd = [
            "mysql", f"--host={db_config['host']}", f"--user={db_config['user']}",
            f"--password={db_config['password']}", db_config['database']
        ]
        with open(input_path, 'r', encoding='utf-8') as f:
            result = subprocess.run(cmd, stdin=f, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
        if result.returncode == 0:
            return True, "تمت استعادة النسخة الاحتياطية بنجاح."
        else:
            return False, f"فشل استعادة النسخة الاحتياطية:\n{result.stderr.strip()}"
    except Exception as e:
        return False, f"حدث استثناء أثناء استعادة النسخة الاحتياطية:\n{str(e)}"

# --- DEPARTMENT MANAGEMENT ---
def get_all_departments():
    """Retrieves a list of all department names."""
    with get_cursor() as cur:
        cur.execute("SELECT name FROM departments ORDER BY name")
        return [row['name'] for row in cur.fetchall()]

def add_department(name, user_id):
    """Adds a new department."""
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
    """Updates the name of a department."""
    try:
        with get_cursor() as cur:
            cur.execute("UPDATE departments SET name = %s WHERE id = %s", (new_name, department_id))
            log_activity(user_id, 'UPDATE', 'department', department_id, f"Renamed department to: {new_name}")
            return True, "تم تحديث القسم بنجاح."
    except mysql.connector.Error as err:
        if err.errno == 1062: return False, "اسم القسم هذا مستخدم بالفعل."
        return False, str(err)

def delete_department(department_id, user_id):
    """Deletes a department if it's not in use."""
    try:
        with get_cursor() as cur:
            cur.execute("SELECT name FROM departments WHERE id = %s", (department_id,))
            dept_name_row = cur.fetchone()
            if not dept_name_row: return False, "Department not found."
            dept_name = dept_name_row['name']
            
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
    """Finds a department's ID by its name."""
    with get_cursor() as cur:
        cur.execute("SELECT id FROM departments WHERE name = %s", (name,))
        result = cur.fetchone()
        return result['id'] if result else None

# --- RECORD HISTORY ---
def get_history_for_record(record_id):
    """Fetches the activity log history for a specific maintenance record."""
    sql = """
        SELECT u.username, al.action, al.description, al.timestamp
        FROM activity_log al LEFT JOIN users u ON al.user_id = u.id
        WHERE al.record_type = 'maintenance' AND al.record_id = %s
        ORDER BY al.timestamp DESC
    """
    with get_cursor() as cur:
        cur.execute(sql, (record_id,))
        return cur.fetchall()
        
# --- ADMIN & REPORTING HELPERS ---
def get_total_record_count():
    """Gets the count of total active records."""
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS count FROM maintenance WHERE is_deleted = 0")
        result = cur.fetchone()
        return result['count'] if result else 0

def get_total_user_count():
    """Gets the count of total active users."""
    with get_cursor() as cur:
        cur.execute("SELECT COUNT(*) AS count FROM users WHERE is_deleted = 0")
        result = cur.fetchone()
        return result['count'] if result else 0

def get_user_role_count(role_name):
    """Gets the count of users with a specific role."""
    sql = "SELECT COUNT(*) AS count FROM users u JOIN roles r ON u.role_id = r.id WHERE r.role_name = %s AND u.is_deleted = 0"
    with get_cursor() as cur:
        cur.execute(sql, (role_name,))
        result = cur.fetchone()
        return result['count'] if result else 0

def search_records_advanced(filters):
    """Performs an advanced search for maintenance records."""
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

def get_records_count_in_period(date_from, date_to, department=None):
    """Gets the count of records within a specific date range."""
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
    """Calculates the average number of records per day."""
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
    """Gets the count of records grouped by department."""
    sql = "SELECT department, COUNT(*) AS count FROM maintenance WHERE is_deleted = 0 AND date BETWEEN %s AND %s GROUP BY department ORDER BY count DESC"
    with get_cursor() as cur:
        cur.execute(sql, (date_from, date_to))
        return cur.fetchall()

def get_device_type_counts(date_from, date_to, department=None):
    """Gets the count of records grouped by device type."""
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
    """Gets the count of records grouped by technician."""
    sql = "SELECT technician, COUNT(*) AS count FROM maintenance WHERE is_deleted = 0 AND date BETWEEN %s AND %s"
    params = [date_from, date_to]
    if department:
        sql += " AND department = %s "
        params.append(department)
    sql += " GROUP BY technician ORDER BY count DESC"
    with get_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()