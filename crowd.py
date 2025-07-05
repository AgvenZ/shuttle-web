# Library
import numpy as np
import cv2
import time
import os
import threading
from datetime import datetime
import pytz

# Import Flask 
try:
    from repositories.kerumunan_repository import KerumunanRepository
    from entities.kerumunan_entity import Kerumunan
except ImportError as e:
    print(f"CRITICAL ERROR [background_processor.py]: Gagal mengimpor modul proyek: {e}")
    # Fallback
    class KerumunanRepository:
        def create(self, entry): return None, "Dummy Mode"
    class Kerumunan:
        def __init__(self, **kwargs): pass

class HalteMonitor:
    """
    Kelas untuk memonitor satu stream CCTV, melakukan deteksi, menyimpan data,
    dan menyediakan frame untuk live streaming.
    """
    def __init__(self, id_halte: int, rtsp_url: str):
        self.id_halte = id_halte
        self.rtsp_url = rtsp_url

        self.net = self._load_model()
        self.kerumunan_repo = KerumunanRepository()
        
        # Pengaturan Penjadwalan & Direktori
        self.capture_dir = f"captured_images/halte_{self.id_halte}"
        os.makedirs(self.capture_dir, exist_ok=True)
        self.wib_tz = pytz.timezone('Asia/Jakarta')
        self.start_hour, self.end_hour, self.interval = 7, 17, 3600
        self.last_capture_time = time.time() - (self.interval + 1)
        
        # Pengaturan Thread & Frame Sharing
        self.is_running = False
        self.stop_event = threading.Event()
        self.thread = None
        self.frame_lock = threading.Lock() # Kunci untuk akses frame yang aman
        self.output_frame = None # Frame yang akan di-stream

    def _load_model(self):
        try:
            net = cv2.dnn.readNet("yolov5n.onnx")
            print(f"[Halte {self.id_halte}] Model 'yolov5n.onnx' berhasil dimuat.")
            return net
        except cv2.error as e:
            print(f"[Halte {self.id_halte}] ERROR: Tidak dapat memuat model ONNX: {e}")
            return None

    def _draw_info_panel(self, frame, person_count, fps, status):
        # Fungsi ini sama seperti di crowd.py sebelumnya
        panel_height = 95
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], panel_height), (30, 30, 30), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f"Jumlah Orang: {person_count}", (15, 30), font, 0.8, (60, 160, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, f"FPS: {fps}", (15, 60), font, 0.6, (230, 230, 230), 1, cv2.LINE_AA)
        cv2.putText(frame, status, (15, 85), font, 0.6, (230, 230, 230), 1, cv2.LINE_AA)

    def _capture_and_save_data(self, frame_with_overlay: np.ndarray, person_count: int, timestamp_wib: datetime):
        """Menyimpan gambar ke file dan data kerumunan ke database."""
        timestamp_str = timestamp_wib.strftime("%Y%m%d_%H%M%S")
        
        # 1. Simpan ke Database
        kerumunan_entry = Kerumunan(id_halte=self.id_halte, waktu=timestamp_wib, jumlah_kerumunan=person_count)
        _, error = self.kerumunan_repo.create(kerumunan_entry)
        if error:
            print(f"[{timestamp_str}][Halte {self.id_halte}] DB ERROR: {error}")
        else:
            print(f"[{timestamp_str}][Halte {self.id_halte}] DB SAVE: Jumlah {person_count} orang.")

        # 2. Simpan Gambar
        file_path = os.path.join(self.capture_dir, f"capture_{timestamp_str}.jpg")
        try:
            cv2.imwrite(file_path, frame_with_overlay)
            print(f"[{timestamp_str}][Halte {self.id_halte}] FOTO TERSIMPAN: {file_path}")
        except Exception as e:
            print(f"[{timestamp_str}][Halte {self.id_halte}] FOTO ERROR: {e}")

    def _run_loop(self):
        if self.net is None: self.is_running = False; return
        
        print(f"[Halte {self.id_halte}] Memulai monitoring untuk URL: {self.rtsp_url}")
        cap = cv2.VideoCapture(self.rtsp_url)

        while not self.stop_event.is_set():
            if not cap.isOpened():
                print(f"[Halte {self.id_halte}] Gagal membuka stream. Mencoba lagi dalam 10 detik...")
                self.stop_event.wait(10); cap.release(); cap = cv2.VideoCapture(self.rtsp_url); continue

            ret, frame = cap.read()
            if not ret:
                print(f"[Halte {self.id_halte}] Tidak dapat membaca frame. Mencoba reconnect..."); cap.release(); self.stop_event.wait(5); continue

            # Proses deteksi
            frame_processed = frame.copy(); start_t = time.time()
            blob = cv2.dnn.blobFromImage(frame_processed, 1/255.0, (640, 640), swapRB=True)
            self.net.setInput(blob); detections = self.net.forward()[0]
            confidences, boxes, person_count = [], [], 0
            h, w = frame_processed.shape[:2]; x_scale, y_scale = w / 640.0, h / 640.0
            
            for row in detections:
                confidence = row[4]
                if confidence > 0.3:
                    scores = row[5:]; class_id = np.argmax(scores)
                    if scores[class_id] > 0.25 and class_id == 0:
                        confidences.append(float(confidence))
                        cx, cy, bw, bh = row[:4]; x1 = int((cx - bw/2) * x_scale); y1 = int((cy - bh/2) * y_scale)
                        boxes.append([x1, y1, int(bw * x_scale), int(bh * y_scale)])
            
            indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.3, 0.45); person_count = len(indices)

            # Gambar overlay
            if person_count > 0:
                for i in indices.flatten():
                    x1, y1, w_box, h_box = boxes[i]
                    cv2.rectangle(frame_processed, (x1, y1), (x1+w_box, y1+h_box), (60, 160, 255), 2)
            
            # Periksa jadwal & gambar panel
            now_wib = datetime.now(self.wib_tz)
            status_msg = f"Status: Nonaktif (Luar {self.start_hour:02}:00-{self.end_hour:02}:00)"
            capture_now = False
            if self.start_hour <= now_wib.hour <= self.end_hour:
                status_msg = f"Status: Aktif ({self.start_hour:02}:00-{self.end_hour:02}:00)";
                if (time.time() - self.last_capture_time) > self.interval:
                    capture_now = True; self.last_capture_time = time.time()
            
            fps = int(1 / (time.time() - start_t)) if time.time() > start_t else 0
            self._draw_info_panel(frame_processed, person_count, fps, status_msg)

            # Simpan data & gambar jika waktunya
            if capture_now:
                self._capture_and_save_data(frame_processed, person_count, now_wib)
            
            # Bagikan frame untuk live stream
            with self.frame_lock:
                self.output_frame = frame_processed.copy()
            
            time.sleep(0.02)

        cap.release(); print(f"[Halte {self.id_halte}] Proses monitoring dihentikan."); self.is_running = False

    def generate_frames(self):
        """Generator untuk menghasilkan frame untuk MJPEG stream."""
        while not self.stop_event.is_set():
            with self.frame_lock:
                if self.output_frame is None:
                    continue
                # Encode frame sebagai JPEG
                (flag, encodedImage) = cv2.imencode(".jpg", self.output_frame)
                if not flag:
                    continue
            
            # Hasilkan frame dalam format bytes untuk streaming
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                  bytearray(encodedImage) + b'\r\n')
            time.sleep(0.05) # Batasi FPS streaming agar tidak membebani jaringan

    def start(self):
        if self.is_running: return
        self.is_running = True; self.stop_event.clear()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self):
        if not self.is_running: return
        print(f"[Halte {self.id_halte}] Mengirim sinyal berhenti..."); self.stop_event.set()
        self.thread.join(timeout=15)