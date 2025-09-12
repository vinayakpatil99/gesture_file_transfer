import socket
import os

HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 5001

def get_next_filename(base="received_file", ext=".txt"):
    i = 1
    while True:
        filename = f"{base}_{i}{ext}"
        if not os.path.exists(filename):
            return filename
        i += 1

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[SERVER] Listening on {HOST}:{PORT} ...")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"[SERVER] Connected by {addr}")
                filename = get_next_filename(base="received_file", ext=".txt")

                with open(filename, "wb") as f:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        f.write(data)

                print(f"[SERVER] File saved as {filename}")

if __name__ == "__main__":
    start_server()
