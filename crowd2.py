# Menyimpan foto dengan overlay
import numpy as np
import cv2
import time
import argparse
import os
from datetime import datetime
import pytz

def draw_modern_info_panel(frame, person_count, fps_value, capture_status):
    """
    Draws a modern, semi-transparent information panel on the given frame.
    """
    panel_height = 95
    panel_alpha = 0.6
    panel_color = (30, 30, 30)

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (frame.shape[1], panel_height), panel_color, -1)
    cv2.addWeighted(overlay, panel_alpha, frame, 1 - panel_alpha, 0, frame)

    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale_main = 0.8
    font_scale_sub = 0.6
    text_color_main = (230, 230, 230)
    text_color_accent = (60, 160, 255)
    thickness = 2
    line_type = cv2.LINE_AA

    count_text = f"Jumlah Orang: {person_count}"
    cv2.putText(frame, count_text, (15, 30), font, font_scale_main, text_color_accent, thickness, line_type)
    fps_text = f"FPS: {fps_value}"
    cv2.putText(frame, fps_text, (15, 60), font, font_scale_sub, text_color_main, thickness - 1, line_type)

    cv2.putText(frame, capture_status, (15, 85), font, font_scale_sub, text_color_main, thickness - 1, line_type)

    quit_text = "Tekan 'q' untuk keluar"
    (text_width, _), _ = cv2.getTextSize(quit_text, font, font_scale_sub, thickness - 1)
    cv2.putText(frame, quit_text, (frame.shape[1] - text_width - 15, 30), font, font_scale_sub, text_color_main, thickness - 1, line_type)

def crowd(args):
    CAPTURE_DIR = "captured_images"
    os.makedirs(CAPTURE_DIR, exist_ok=True)

    wib_tz = pytz.timezone('Asia/Jakarta')
    CAPTURE_START_HOUR = 7
    CAPTURE_END_HOUR = 17
    CAPTURE_INTERVAL_SECONDS = 30

    last_capture_time = time.time() - (CAPTURE_INTERVAL_SECONDS + 1)
    capture_status_message = "Status: Menunggu jadwal..."

    arg_input = "http://61.211.241.239/nphMotionJpeg?Resolution=640x480&Quality=High"

    cap = cv2.VideoCapture(arg_input)
    if not cap.isOpened():
        print(f"Error: Could not open video source '{arg_input}'.")
        return

    try:
        net = cv2.dnn.readNet("yolov5n.onnx")
    except cv2.error as e:
        print("Error: Could not load the ONNX model 'yolov5n.onnx'.")
        print(f"Details: {e}")
        return

    classes = ["Orang"]

    while True:
        ret, frame_original = cap.read()
        if not ret:
            print("Reached end of video or cannot read frame.")
            break

        current_time_unix = time.time()
        now_wib = datetime.now(wib_tz)
        
        if CAPTURE_START_HOUR <= now_wib.hour <= CAPTURE_END_HOUR:
            capture_status_message = f"Status: Aktif (07:00 - 17:00 WIB)"
            if (time.time() - last_capture_time) > CAPTURE_INTERVAL_SECONDS:
                capture_this_frame = True
                last_capture_time = time.time()
        else:
            capture_status_message = f"Status: Tidak aktif (di luar 07:00 - 17:00 WIB)"

        frame_processed = frame_original.copy()
        start_time_inference = time.time()
        
        blob = cv2.dnn.blobFromImage(frame_processed, scalefactor=1/255, size=(640, 640), mean=[0, 0, 0], swapRB=True, crop=False)
        net.setInput(blob)
        detections = net.forward()[0]

        confidences, boxes = [], []
        for i in range(detections.shape[0]):
            row = detections[i]
            confidence = row[4]
            if confidence > 0.2:
                classes_scores = row[5:]
                class_id = np.argmax(classes_scores)
                if classes_scores[class_id] > 0.2 and class_id == 0:
                    confidences.append(float(confidence))
                    cx, cy, w, h = row[:4]
                    img_height, img_width = frame_processed.shape[:2]
                    x_scale, y_scale = img_width / 640.0, img_height / 640.0
                    x1 = int((cx - w / 2) * x_scale)
                    y1 = int((cy - h / 2) * y_scale)
                    box_width = int(w * x_scale)
                    box_height = int(h * y_scale)
                    boxes.append([x1, y1, box_width, box_height])

        indices = cv2.dnn.NMSBoxes(boxes, confidences, score_threshold=0.2, nms_threshold=0.2)
        processing_time = time.time() - start_time_inference
        current_fps = int(1 / processing_time) if processing_time > 0 else 0
        person_count = len(indices) if len(indices) > 0 else 0

        if person_count > 0:
            for i in indices.flatten():
                x1, y1, w, h = boxes[i]
                cv2.rectangle(frame_processed, (x1, y1), (x1 + w, y1 + h), (60, 160, 255), 2, cv2.LINE_AA)

        display_frame = cv2.resize(frame_processed, (960, 720))
        draw_modern_info_panel(display_frame, person_count, current_fps, capture_status_message)

        cv2.imshow("Crowd Analysis", display_frame)

        if capture_this_frame:
            timestamp_str = now_wib.strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(CAPTURE_DIR, f"capture_overlay_{timestamp_str}.jpg")
            
            # Simpan 'display_frame' yang sudah berisi semua overlay
            cv2.imwrite(file_path, display_frame)
            print(f"[{now_wib.strftime('%H:%M:%S WIB')}] Foto dengan overlay berhasil disimpan sebagai: {file_path}")

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("Exiting...")
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Analysis Done.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Crowd counting.")
    parser.add_argument(
        '--input',
        type=str,
        default='0',
        help="Path to video file OR camera index (e.g., '0', '1'). Default is '0'."
    )
    args = parser.parse_args()
    crowd(args)