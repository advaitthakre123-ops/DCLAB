import socket
import time
COORDINATOR_IP = "10.10.123.22"
COORDINATOR_PORT = 6000
CLIENT_ID = input("Enter client ID: ")
def critical_section():
 time_in_cs = 2

 time.sleep(time_in_cs)
 return time_in_cs
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
 s.connect((COORDINATOR_IP, COORDINATOR_PORT))
 while True:
 s.sendall(f"REQUEST {CLIENT_ID}".encode())
 data = s.recv(1024).decode()
 if data == "GRANT":
 print(f"{CLIENT_ID} entering CS")
 cs_duration = critical_section()
 print(f"{CLIENT_ID} leaving CS")
 s.sendall(f"RELEASE {CLIENT_ID} {cs_duration}".encode())
 time.sleep