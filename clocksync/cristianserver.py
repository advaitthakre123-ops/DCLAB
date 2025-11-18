import socket
import time


host = "127.0.0.1"
port = 5000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen()
print(f"[Server] Listening on {host}:{port}...")
while True:
   conn, addr = s.accept()
   print(f"[Server] Connection from {addr}")
   server_time = time.time()
   conn.send(str(server_time).encode())
   print(f"[Server] Sent time {server_time}")
   conn.close()
