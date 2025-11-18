import socket
import time


host = "127.0.0.1"
port = 5000
local_clock = time.time()
print(f"[Client] Local clock before sync: {local_clock}")
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect((host, port))
c.send(str(local_clock).encode())
offset = float(c.recv(1024).decode())
print(f"[Client] Offset received: {offset}")
local_clock += offset
print(f"[Client] Local clock after sync: {local_clock}")
c.close()