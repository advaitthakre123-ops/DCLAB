import socket
import json
server_clock = [1,0]
def update_vector(recvd):
 global server_clock
 for i in range(len(server_clock)):
 server_clock[i] = max(server_clock[i], recvd[i])
 server_clock[1] += 1
 return server_clock
def lamport_server(host='localhost', port=6001):
 s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 s.bind((host, port))
 s.listen(5)
 print("Starting Vector Clock Server...")
 print(f"Server is listening on {host}:{port}...")
 while True:
 conn, addr = s.accept()
 print(f"Connected by {addr}")
 data = conn.recv(1024).decode()
 if not data:
 break

 recvd = json.loads(data)
 print(f"Received client vector: {recvd}")

 updated_vector = update_vector(recvd)

 print(f"Updated server vector: {updated_vector}")
 conn.close()
if __name__ == "__main__":
 lamport_server(