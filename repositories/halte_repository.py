from config.db_config import get_db_connection
from entities.halte_entity import Halte
import mysql.connector

class HalteRepository:
    def get_all(self):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if conn is None:
                return None, "Failed to connect to database"
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id AS id_halte, nama_halte, cctv, latitude, longitude FROM halte")
            result = cursor.fetchall()
            return [Halte(**row) for row in result], None
        except mysql.connector.Error as err:
            return None, str(err)
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def get_by_id(self, id_halte: int):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if conn is None:
                return None, "Failed to connect to database"
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id AS id_halte, nama_halte, cctv, latitude, longitude FROM halte WHERE id = %s", (id_halte,))
            result = cursor.fetchone()
            if result:
                return Halte(**result), None
            return None, "Halte not found"
        except mysql.connector.Error as err:
            return None, str(err)
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def create(self, halte: Halte):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if conn is None:
                return None, "Failed to connect to database"
            cursor = conn.cursor()
            sql = "INSERT INTO halte (nama_halte, cctv, latitude, longitude) VALUES (%s, %s, %s, %s)"
            val = (halte.nama_halte, halte.cctv, halte.latitude, halte.longitude)
            cursor.execute(sql, val)
            conn.commit()
            halte.id_halte = cursor.lastrowid
            return halte, None
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            return None, str(err)
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def update(self, id_halte: int, halte_data: Halte):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if conn is None:
                return None, "Failed to connect to database"
            cursor = conn.cursor()
            sql = "UPDATE halte SET nama_halte = %s, cctv = %s, latitude = %s, longitude = %s WHERE id = %s"
            val = (halte_data.nama_halte, halte_data.cctv, halte_data.latitude, halte_data.longitude, id_halte)
            cursor.execute(sql, val)
            conn.commit()
            if cursor.rowcount == 0:
                return None, "Halte not found or no changes made"
            halte_data.id_halte = id_halte
            return halte_data, None
        except mysql.connector.Error as err:
            if conn:
                conn.rollback()
            return None, str(err)
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def delete(self, id_halte: int):
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if conn is None:
                return False, "Failed to connect to database"
            cursor = conn.cursor()
            # Periksa apakah ada kerumunan yang terkait dengan halte ini
            cursor.execute("SELECT COUNT(*) FROM kerumunan WHERE id_halte = %s", (id_halte,))
            if cursor.fetchone()[0] > 0:
                return False, "Cannot delete halte, it is referenced by kerumunan records."

            cursor.execute("DELETE FROM halte WHERE id = %s", (id_halte,))
            conn.commit()
            if cursor.rowcount == 0:
                return False, "Halte not found"
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