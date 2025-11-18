import socket
import time


host = "127.0.0.1"
port = 5000
t0 = time.time()
c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
c.connect((host, port))
c.send(b"REQ")
server_time = float(c.recv(1024).decode())
t1 = time.time()
c.close()
rtt = t1 - t0
one_way = rtt / 2
adjusted = server_time + one_way
print(f"[Client] Sent request at t0 = {t0}")
print(f"[Client] Received server time = {server_time} at t1 = {t1}")
print(f"[Client] RTT = {rtt} seconds")
print(f"[Client] Estimated one-way delay = {one_way} seconds")
print(f"[Client] Adjusted time should be: {adjusted}")
