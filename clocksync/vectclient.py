import socket
import json
client_vector = [0, 0]
def sendMessage():
 client_vector[0] += 1
 print(f"Client vector : {client_vector}")
 s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 s.connect(("localhost", 6001))
 s.send(json.dumps(client_vector).encode())
 s.close()

sendMessage()