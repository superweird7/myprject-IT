# /database/record_queries.py

import os
from .connection import get_cursor
from .utility_queries import log_activity # Import from our new utility module

# --- CRUD maintenance ---
def insert_record(data, user_id):
    """Inserts a new maintenance record."""
    sql = "INSERT INTO maintenance (date, type, device, technician, procedures, materials, notes, warnings, department) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    with get_cursor() as cur:
        cur.execute(sql, data)
        new_record_id = cur.lastrowid
        log_activity(user_id, 'INSERT', 'maintenance', new_record_id, f"Added record for device: {data[2]}")
        return new_record_id

def fetch_records(department=None):
    """Fetches active maintenance records, optionally filtered by department."""
    sql = "SELECT * FROM maintenance WHERE is_deleted = 0"
    params = []
    if department:
        sql += " AND department = %s"
        params.append(department)
    sql += " ORDER BY id DESC"
    with get_cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()

def update_record(rec_id, data, user_id):
    """Updates an existing maintenance record."""
    sql = "UPDATE maintenance SET date=%s, type=%s, device=%s, technician=%s, procedures=%s, materials=%s, notes=%s, warnings=%s, department=%s WHERE id=%s"
    with get_cursor() as cur:
        cur.execute(sql, (*data, rec_id))
        if cur.rowcount > 0:
            log_activity(user_id, 'UPDATE', 'maintenance', rec_id, f"Updated record for device: {data[2]}")

def delete_record(rec_id, user_id):
    """Soft-deletes a maintenance record by setting is_deleted = 1."""
    sql = "UPDATE maintenance SET is_deleted = 1 WHERE id = %s"
    with get_cursor() as cur:
        cur.execute(sql, (rec_id,))
        if cur.rowcount > 0:
            log_activity(user_id, 'TRASH', 'maintenance', rec_id, f"Moved record to trash ID: {rec_id}")

# --- TRASH MANAGEMENT (Maintenance Records) ---
def fetch_deleted_records():
    """Fetches all soft-deleted maintenance records."""
    sql = "SELECT * FROM maintenance WHERE is_deleted = 1 ORDER BY id DESC"
    with get_cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()

def restore_record(rec_id, user_id):
    """Restores a soft-deleted maintenance record."""
    sql = "UPDATE maintenance SET is_deleted = 0 WHERE id = %s"
    with get_cursor() as cur:
        cur.execute(sql, (rec_id,))
        if cur.rowcount > 0:
            log_activity(user_id, 'RESTORE', 'maintenance', rec_id, f"Restored record from trash ID: {rec_id}")

def permanently_delete_record(rec_id, user_id):
    """Permanently deletes a maintenance record and its attachments."""
    with get_cursor() as cur:
        # First, delete associated attachments to prevent orphaned files
        cur.execute("DELETE FROM attachments WHERE maintenance_id=%s", (rec_id,))
        # Then, delete the record itself
        cur.execute("DELETE FROM maintenance WHERE id=%s AND is_deleted = 1", (rec_id,))
        if cur.rowcount > 0:
            log_activity(user_id, 'DELETE', 'maintenance', rec_id, f"Permanently deleted record ID: {rec_id}")


# --- ATTACHMENT MANAGEMENT ---
def add_attachment(maintenance_id, original_filename, stored_filepath, user_id):
    """Adds an attachment record to the database."""
    sql = "INSERT INTO attachments (maintenance_id, original_filename, stored_filepath) VALUES (%s, %s, %s)"
    with get_cursor() as cur:
        cur.execute(sql, (maintenance_id, original_filename, stored_filepath))
        new_attachment_id = cur.lastrowid
        log_activity(user_id, 'INSERT', 'attachment', new_attachment_id, f"Added attachment '{original_filename}' to record {maintenance_id}")
        return new_attachment_id

def get_attachments_for_record(maintenance_id):
    """Fetches all attachments for a specific maintenance record."""
    sql = "SELECT id, original_filename, stored_filepath FROM attachments WHERE maintenance_id = %s ORDER BY id"
    with get_cursor() as cur:
        cur.execute(sql, (maintenance_id,))
        return cur.fetchall()

def delete_attachment(attachment_id, user_id):
    """Deletes an attachment from the filesystem and database."""
    try:
        with get_cursor() as cur:
            cur.execute("SELECT stored_filepath, original_filename, maintenance_id FROM attachments WHERE id = %s", (attachment_id,))
            attachment = cur.fetchone()
            if not attachment: return False, "Attachment not found."

            if os.path.exists(attachment['stored_filepath']):
                os.remove(attachment['stored_filepath'])

            cur.execute("DELETE FROM attachments WHERE id = %s", (attachment_id,))
            if cur.rowcount > 0:
                log_activity(user_id, 'DELETE', 'attachment', attachment_id, f"Removed attachment '{attachment['original_filename']}' from record {attachment['maintenance_id']}")
                return True, "Attachment deleted successfully."
            else:
                return False, "Failed to delete attachment record from database."
    except Exception as e:
        return False, f"An error occurred: {str(e)}"