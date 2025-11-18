import socket
import time
def lamport_client(server_ip='localhost', server_port=6000):
 client_clock = 0
 for i in range(3):
 client_clock += 1
 print(f"Client clock on sending: {client_clock}")
 s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 s.connect((server_ip, server_port))
 s.send(str(client_clock).encode())
 data = s.recv(1024).decode()
 server_clock = int(data)
 print(f"Received updated server clock:
{server_clock}")
 s.close()
 time.sleep(1)
if __name__ == "__main__":
 lamport_client()