import socket
def lamport_server(host='localhost', port=6000):
 server_clock = 0
 s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 s.bind((host, port))
 s.listen(5)
 print("Starting Lamport Clock Server...")
 print(f"Server is listening on {host}:{port}...")
 while True:
    conn, addr = s.accept()
    print(f"Connected by {addr}")
    data = conn.recv(1024).decode()
    if not data:
        break

    client_time = int(data)
    print(f"Received client time: {client_time}")
    server_clock = max(server_clock, client_time) + 1
    print(f"Updated server clock: {server_clock}")
    conn.send(str(server_clock).encode())
    conn.close()
if __name__ == "__main__":
 lamport_server()