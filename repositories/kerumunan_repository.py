from config.db_config import get_db_connection
from entities.kerumunan_entity import Kerumunan
from datetime import datetime
import mysql.connector

class KerumunanRepository:
    def get_all(self):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if conn is None:
                return None, "Failed to connect to database"
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id AS id_kerumunan, id_halte, waktu, jumlah_kerumunan FROM kerumunan")
            result = cursor.fetchall()
            return [Kerumunan(**row) for row in result], None
        except mysql.connector.Error as err:
            return None, str(err)
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def get_by_id(self, id_kerumunan: int):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if conn is None:
                return None, "Failed to connect to database"
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id AS id_kerumunan, id_halte, waktu, jumlah_kerumunan FROM kerumunan WHERE id = %s", (id_kerumunan,))
            result = cursor.fetchone()
            if result:
                return Kerumunan(**result), None
            return None, "Kerumunan not found"
        except mysql.connector.Error as err:
            return None, str(err)
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def get_by_id_halte(self, id_halte: int):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if conn is None:
                return None, "Failed to connect to database"
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id AS id_kerumunan, id_halte, waktu, jumlah_kerumunan FROM kerumunan WHERE id_halte = %s", (id_halte,))
            result = cursor.fetchall()
            return [Kerumunan(**row) for row in result], None
        except mysql.connector.Error as err:
            return None, str(err)
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def create(self, kerumunan: Kerumunan):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if conn is None:
                return None, "Failed to connect to database"

            # Periksa apakah id_halte ada di tabel halte
            cursor_check = conn.cursor()
            cursor_check.execute("SELECT id FROM halte WHERE id = %s", (kerumunan.id_halte,))
            if cursor_check.fetchone() is None:
                cursor_check.close()
                return None, f"Halte with id {kerumunan.id_halte} does not exist."
            cursor_check.close()

            cursor = conn.cursor()
            sql = "INSERT INTO kerumunan (id_halte, waktu, jumlah_kerumunan) VALUES (%s, %s, %s)"
            val = (kerumunan.id_halte, kerumunan.waktu, kerumunan.jumlah_kerumunan)
            cursor.execute(sql, val)
            conn.commit()
            kerumunan.id_kerumunan = cursor.lastrowid
            return kerumunan, None
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            return None, str(err)
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def update(self, id_kerumunan: int, kerumunan_data: Kerumunan):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if conn is None:
                return None, "Failed to connect to database"

            # Periksa apakah id_halte ada di tabel halte jika sedang diperbarui
            if kerumunan_data.id_halte is not None:
                cursor_check = conn.cursor()
                cursor_check.execute("SELECT id FROM halte WHERE id = %s", (kerumunan_data.id_halte,))
                if cursor_check.fetchone() is None:
                    cursor_check.close()
                    return None, f"Halte with id {kerumunan_data.id_halte} does not exist."
                cursor_check.close()

            cursor = conn.cursor()
            sql = "UPDATE kerumunan SET id_halte = %s, waktu = %s, jumlah_kerumunan = %s WHERE id = %s"
            val = (kerumunan_data.id_halte, kerumunan_data.waktu, kerumunan_data.jumlah_kerumunan, id_kerumunan)
            cursor.execute(sql, val)
            conn.commit()
            if cursor.rowcount == 0:
                return None, "Kerumunan not found or no changes made"
            kerumunan_data.id_kerumunan = id_kerumunan
            return kerumunan_data, None
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            return None, str(err)
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def delete(self, id_kerumunan: int):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if conn is None:
                return False, "Failed to connect to database"
            cursor = conn.cursor()
            cursor.execute("DELETE FROM kerumunan WHERE id = %s", (id_kerumunan,))
            conn.commit()
            if cursor.rowcount == 0:
                return False, "Kerumunan not found"
            return True, None
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            return False, str(err)
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()