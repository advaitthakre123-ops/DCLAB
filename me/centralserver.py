import socket
import threading
import queue
import time
HOST = '0.0.0.0'
PORT = 6000
lock = False
lock_holder = None
waiting_queue = queue.Queue()
client_sockets = {}
def handle_client(conn, addr):
global lock, lock_holder
while True:
try:
data = conn.recv(1024).decode()
if not data:
break
if data.startswith("REQUEST"):
client_id = data.split()[1]
if not lock:
lock = True
lock_holder = client_id
client_sockets[client_id] = conn

conn.sendall("GRANT".encode())
print(f"GRANT sent to {client_id}")
else:
waiting_queue.put((client_id, conn))
print(f"{client_id} queued")
elif data.startswith("RELEASE"):
client_id = data.split()[1]
cs_time = float(data.split()[2])
print(f"{client_id} was in critical section for
{cs_time:.3f} seconds")
if not waiting_queue.empty():
next_client_id, next_conn = waiting_queue.get()
lock_holder = next_client_id
client_sockets[next_client_id] = next_conn
next_conn.sendall("GRANT".encode())
print(f"GRANT sent to {next_client_id}")
else:
lock = False
lock_holder = None
except:
break
conn.close()
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
s.bind((HOST, PORT))
s.listen()
print(f"Coordinator listening on port {PORT} ...")
while True:
conn, addr = s.accept()
threading.Thread(target=handle_client, args=(conn, addr),
daemon=True).start()