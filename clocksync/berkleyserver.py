import socket
import threading
import time


host = "127.0.0.1"
port = 5000
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
print(f"[Server] Listening on {host}:{port}...")
clients = []
times = {}


def handle_client(conn, addr):
   node_time = float(conn.recv(1024).decode())
   print(f"[Server] Received time {node_time} from {addr}")
   times[addr] = node_time
   clients.append((conn, addr))


while True:
   while len(clients) < 3:
       conn, addr = server.accept()
       threading.Thread(target=handle_client, args=(conn, addr)).start()
       time.sleep(0.2)
   if len(times) == 3:
       master = time.time()
       print(f"[Server] Master clock time: {master}")
       avg = (master + sum(times.values())) / (len(times) + 1)
       print(f"[Server] Average time: {avg}")
       for conn, addr in clients:
           offset = avg - times[addr]
           conn.send(str(offset).encode())
           print(f"[Server] Sent offset {offset} to {addr}")
       master_offset = avg - master
       print(f"[Server] Adjusting master by {master_offset} seconds")
       break