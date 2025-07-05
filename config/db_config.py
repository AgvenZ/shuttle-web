import mysql.connector
import mysql.connector.pooling
from mysql.connector import errorcode
import os
from dotenv import load_dotenv

load_dotenv()

def initialize_connection_pool():
    """
    Menginisialisasi connection pool. Jika database tidak ada,
    fungsi ini akan mencoba membuatnya terlebih dahulu.
    """
    db_name = os.getenv('MYSQL_DB')
    
    config_no_db = {
        'host': os.getenv('MYSQL_HOST'),
        'user': os.getenv('MYSQL_USER'),
        'password': os.getenv('MYSQL_PASSWORD'),
    }
    
    config_with_db = {
        **config_no_db,
        'database': db_name,
    }

    try:
        print(f"Mencoba terhubung ke database '{db_name}'...")
        pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name=os.getenv('MYSQL_POOL_NAME', 'mypool'),
            pool_size=int(os.getenv('MYSQL_POOL_SIZE', 5)),
            **config_with_db
        )
        print("Koneksi ke database berhasil, connection pool dibuat.")
        return pool

    except mysql.connector.Error as err:
        # Periksa apakah error disebabkan karena database tidak ada
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            print(f"Database '{db_name}' tidak ditemukan. Mencoba membuatnya...")
            try:
                conn = mysql.connector.connect(**config_no_db)
                cursor = conn.cursor()
                
                cursor.execute(f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
                cursor.close()
                conn.close()
                print(f"Database '{db_name}' berhasil dibuat.")

                print("Mencoba kembali membuat connection pool...")
                pool = mysql.connector.pooling.MySQLConnectionPool(
                    pool_name=os.getenv('MYSQL_POOL_NAME', 'mypool'),
                    pool_size=int(os.getenv('MYSQL_POOL_SIZE', 5)),
                    **config_with_db
                )
                print("Connection pool berhasil dibuat setelah pembuatan database.")
                return pool

            except mysql.connector.Error as creation_err:
                print(f"FATAL: Gagal membuat database '{db_name}': {creation_err}")
                return None
        else:
            print(f"FATAL: Terjadi error koneksi database yang tidak terduga: {err}")
            return None

connection_pool = initialize_connection_pool()

def get_db_connection():
    if connection_pool:
        try:
            return connection_pool.get_connection()
        except mysql.connector.Error as err:
            print(f"Error getting connection from pool: {err}")
            return None
    else:
        print("Connection pool is not available.")
        return None