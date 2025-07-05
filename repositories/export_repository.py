from config.db_config import get_db_connection
import mysql.connector

class ExportRepository:
    def get_kerumunan_export_data(self):
        """
        Mengambil semua data kerumunan yang digabungkan dengan nama halte 
        untuk keperluan ekspor.
        """
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if conn is None:
                return None, "Gagal terhubung ke database"
            
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    k.id AS id_kerumunan,
                    h.nama_halte,
                    h.latitude,
                    h.longitude,
                    k.waktu,
                    k.jumlah_kerumunan
                FROM kerumunan k
                JOIN halte h ON k.id_halte = h.id
                ORDER BY k.waktu DESC
            """
            cursor.execute(query)
            result = cursor.fetchall()
            return result, None
        except mysql.connector.Error as err:
            return None, str(err)
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()