import socket
import struct
import cv2
import time
import threading
import os
import math
from gestures import HandGesture  # Your existing gesture detection
import pygame

# ===== CONFIG =====
SERVER_IP = "192.168.43.55"   # Replace with your receiver IP
PORT = 5001
FILE_TO_SEND = "sample.png"
TARGET_POS = (540, 380)       # screen coordinates for phone
MAX_CAMERA_INDEX = 5
# =================

# ----------- Automatic Webcam Detection -----------
def get_working_camera(max_index=5):
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap is None or not cap.isOpened():
            cap.release()
            continue
        ret, _ = cap.read()
        if ret:
            print(f"[INFO] Using camera index {i}")
            return cap
        cap.release()
    return None

# ---------------- Animation Class ----------------
class Animation:
    def __init__(self, file_path, win_size=(640,480), target_pos=(540,380)):
        pygame.init()
        self.win_w, self.win_h = win_size
        self.screen = pygame.display.set_mode(win_size)
        pygame.display.set_caption("Gesture File Transfer - Pro Version")
        self.clock = pygame.time.Clock()
        self.file_image_orig = pygame.image.load(file_path)
        self.file_image_orig = pygame.transform.scale(self.file_image_orig, (80,80))
        self.hand_pos = None
        self.flying = False
        self.fly_start = None
        self.fly_end = target_pos
        self.fly_progress = 0
        self.current_size = 80
        self.angle = 0
        self.trail_points = []

    def start_grab(self, x, y):
        self.hand_pos = (x, y)
        self.trail_points = []

    def drop(self):
        if self.hand_pos:
            self.fly_start = self.hand_pos
            self.flying = True
            self.fly_progress = 0
            self.current_size = 80
            self.angle = 0
            self.trail_points = []

    def update(self, x, y):
        self.screen.fill((30,30,30))

        # draw hand indicator
        if x is not None and y is not None:
            pygame.draw.circle(self.screen, (0,255,0), (int(x), int(y)), 15)
        if x is not None and y is not None:
            self.hand_pos = (x, y)

        # flying file
        if self.flying and self.fly_start and self.fly_end:
            self.fly_progress += 0.03
            if self.fly_progress >= 1:
                self.fly_progress = 1
                self.flying = False

            # interpolate position
            fx = self.fly_start[0] + (self.fly_end[0]-self.fly_start[0])*self.fly_progress
            fy = self.fly_start[1] + (self.fly_end[1]-self.fly_start[1])*self.fly_progress

            # shrink
            size = 80 - int(50*self.fly_progress)
            self.current_size = max(size,1)

            # rotate
            self.angle += 10
            img = pygame.transform.rotate(
                pygame.transform.scale(self.file_image_orig, (self.current_size,self.current_size)),
                self.angle
            )

            # add trail effect
            self.trail_points.append((fx, fy))
            for idx, point in enumerate(self.trail_points[-10:]):  # last 10 points
                alpha = int(255 * (idx+1)/10)
                trail_surf = pygame.Surface((self.current_size,self.current_size), pygame.SRCALPHA)
                trail_surf.blit(img, (0,0))
                trail_surf.set_alpha(alpha//2)
                self.screen.blit(trail_surf, (point[0]-self.current_size//2, point[1]-self.current_size//2))

            rect = img.get_rect(center=(fx, fy))
            self.screen.blit(img, rect.topleft)

        elif self.hand_pos and not self.flying:
            self.screen.blit(self.file_image_orig, (self.hand_pos[0]-40, self.hand_pos[1]-40))

        pygame.display.flip()
        self.clock.tick(60)

    def close(self):
        pygame.quit()

# ---------------- File Sender ----------------
def send_file(server_ip, port, file_path):
    if not os.path.exists(file_path):
        print("[CLIENT] File not found:", file_path)
        return False
    fname = os.path.basename(file_path)
    fsize = os.path.getsize(file_path)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_ip, port))
            fname_b = fname.encode('utf-8')
            s.sendall(struct.pack(">I", len(fname_b)))
            s.sendall(fname_b)
            s.sendall(struct.pack(">Q", fsize))
            with open(file_path,"rb") as f:
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    s.sendall(chunk)
        print("[CLIENT] File sent successfully.")
        return True
    except Exception as e:
        print("[CLIENT] Error sending file:", e)
        return False

# ---------------- Main ----------------
def main():
    if SERVER_IP == "REPLACE_WITH_RECEIVER_IP":
        print("Set SERVER_IP in client.py first!")
        return

    cap = get_working_camera(MAX_CAMERA_INDEX)
    if cap is None:
        print("[CLIENT] Cannot find any working webcam.")
        return
    cap.set(3,640)
    cap.set(4,480)

    detector = HandGesture()
    ui = Animation(FILE_TO_SEND, win_size=(640,480), target_pos=TARGET_POS)

    grabbed = False
    last_gesture_time = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("[CLIENT] Cannot read webcam frame.")
                break

            gesture, (x,y) = detector.detect(frame)

            if gesture == "fist" and not grabbed and time.time() - last_gesture_time > 0.8:
                print("[CLIENT] Grab detected.")
                grabbed = True
                ui.start_grab(x,y)
                last_gesture_time = time.time()

            elif gesture == "open" and grabbed and time.time() - last_gesture_time > 0.8:
                print("[CLIENT] Drop detected. Sending file...")
                threading.Thread(target=send_file, args=(SERVER_IP, PORT, FILE_TO_SEND), daemon=True).start()
                ui.drop()
                grabbed = False
                last_gesture_time = time.time()

            # webcam overlay
            cv2.putText(frame, f"Gesture: {gesture}", (10,30), cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
            cv2.imshow("Webcam - Gesture Sender (ESC to quit)", frame)

            ui.update(x, y)

            if cv2.waitKey(1) & 0xFF == 27:
                break
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
        ui.close()

if __name__ == "__main__":
    main()
