from flask import Flask, jsonify, Response
from dotenv import load_dotenv
import os
import atexit

# Load environment variables adalah wajib
load_dotenv()

from config.db_config import connection_pool, get_db_connection
from routes.halte_routes import halte_bp
from routes.kerumunan_routes import kerumunan_bp
from routes.export_routes import export_bp
from crowd import HalteMonitor
from services.halte_service import HalteService

app = Flask(__name__)

# Inisialisasi Blueprints
app.register_blueprint(halte_bp)
app.register_blueprint(kerumunan_bp)
app.register_blueprint(export_bp)

active_monitors = {}

def start_all_monitors_on_startup():
    """Mengambil halte dari DB & memulai thread monitoring untuk setiap CCTV."""
    print("\n--- Memulai Otomatisasi Monitoring CCTV ---")
    with app.app_context():
        halte_service = HalteService()
        all_haltes, error = halte_service.get_all_halte()

        if error or not all_haltes:
            print("Tidak ada data halte atau terjadi error. Tidak ada yang dimonitor.")
            return

        for halte in all_haltes:
            id_h, cctv_url = halte.get('id_halte'), halte.get('cctv')
            if id_h and cctv_url and cctv_url.strip():
                if id_h in active_monitors and active_monitors[id_h].is_running: continue
                print(f"Menyiapkan monitoring untuk Halte ID: {id_h}...")
                monitor = HalteMonitor(id_halte=id_h, rtsp_url=cctv_url)
                if monitor.net:
                    monitor.start(); active_monitors[id_h] = monitor
                else:
                    print(f"Monitoring Halte ID {id_h} gagal: model tidak dimuat.")
            elif id_h:
                 print(f"Melewati Halte ID {id_h} karena tidak ada link CCTV.")
        print("--- Selesai Menyiapkan Monitoring CCTV ---\n")

def shutdown_all_monitors():
    """Fungsi cleanup untuk menghentikan semua thread saat aplikasi berhenti."""
    print("\n--- Aplikasi Berhenti: Menghentikan Semua Proses Monitoring ---")
    for monitor in active_monitors.values():
        if monitor.is_running: monitor.stop()
    print("--- Semua Sinyal Berhenti Telah Dikirim ---")

atexit.register(shutdown_all_monitors)

@app.route("/halte/rtsp/<int:id_halte>")
def rtsp_feed(id_halte):
    """Endpoint untuk menyajikan live stream MJPEG dari halte tertentu."""
    # Cari monitor yang aktif untuk id_halte ini
    monitor = active_monitors.get(id_halte)
    
    if monitor and monitor.is_running:
        # Kembalikan response streaming menggunakan generator frame dari monitor
        return Response(monitor.generate_frames(),
                        mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        # Jika monitor tidak ditemukan atau tidak berjalan
        return Response(f"Error: Monitoring untuk Halte ID {id_halte} tidak aktif atau tidak ditemukan.", status=404)

def create_tables_if_not_exist():
    """
    Membuat tabel 'halte' dan 'kerumunan' jika belum ada.
    Fungsi ini dipanggil setelah database dan koneksi dipastikan ada.
    """
    conn = None
    cursor = None
    try:
        # Dapatkan koneksi dari pool yang sudah pasti ada
        conn = get_db_connection()
        if conn and conn.is_connected():
            cursor = conn.cursor()
            print("Memeriksa dan membuat tabel jika diperlukan...")
            
            # Buat tabel halte
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS halte (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    nama_halte VARCHAR(255) NOT NULL,
                    cctv VARCHAR(255) DEFAULT NULL,
                    latitude FLOAT(10, 6) NULL,
                    longitude FLOAT(10, 6) NULL
                )
            """)
            print("- Tabel 'halte' diperiksa/dibuat.")

            # Buat tabel kerumunan
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kerumunan (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    id_halte INT NOT NULL,
                    waktu DATETIME NOT NULL,
                    jumlah_kerumunan INT NOT NULL,
                    FOREIGN KEY (id_halte) REFERENCES halte(id)
                )
            """)
            print("- Tabel 'kerumunan' diperiksa/dibuat.")
            conn.commit()
            print("Pemeriksaan tabel selesai.")
    except Exception as e:
        print(f"Error saat membuat tabel: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

@app.route('/')
def home():
    return jsonify({"meta": {"status": "success", "message": "Welcome to the API!"}}), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"meta": {"status": "error", "message": "Resource not found"}}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"meta": {"status": "error", "message": f"Internal server error: {str(error)}"}}), 500

@app.errorhandler(400)
def bad_request(error):
    message = "Bad request"
    if hasattr(error, 'description') and error.description:
        message = error.description
    return jsonify({"meta": {"status": "error", "message": message}}), 400

if __name__ == '__main__':
    if connection_pool:
        print("Attempting to create tables...")
        create_tables_if_not_exist()
        start_all_monitors_on_startup()
        app.run(debug=True, host='localhost', port=int(os.getenv('FLASK_RUN_PORT', 5000)))
    else:
        print("Failed to initialize database connection pool. Application will not start.")