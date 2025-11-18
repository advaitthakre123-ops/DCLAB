import socket
import threading
import argparse
import time
import random
parser = argparse.ArgumentParser()
parser.add_argument('--id', type=int, required=True)
parser.add_argument('--n', type=int, required=True)
parser.add_argument('--base-port', type=int, required=True)
parser.add_argument('--initial-holder', action='store_true')
args = parser.parse_args()
NODE_ID = args.id
NUM_NODES = args.n
BASE_PORT = args.base_port
TOKEN_HOLDER = args.initial_holder
MY_PORT = BASE_PORT + NODE_ID
NEXT_NODE = (NODE_ID + 1) % NUM_NODES
NEXT_PORT = BASE_PORT + NEXT_NODE
HOST = '0.0.0.0'

token = TOKEN_HOLDER
token_lock = threading.Lock()
token_received_event = threading.Event()
def critical_section():
 cs_time = random.uniform(2, 3)
 print(f"Node {NODE_ID} entering CS for {cs_time:.2f} seconds")
 time.sleep(cs_time)
 print(f"Node {NODE_ID} leaving CS")
 return cs_time
def listen_for_token():
 with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
 s.bind((HOST, MY_PORT))
 s.listen()
 while True:
 conn, addr = s.accept()
 with conn:
 data = conn.recv(1024).decode()
 if data == "TOKEN":
 with token_lock:
 global token
token = True
 token_received_event.set()
def pass_token():
 global token
 while True:
 token_received_event.wait()
 with token_lock:
 if token:
 cs_time = critical_section()
 print(f"Node {NODE_ID} passed token after CS")
 try:
 with socket.socket(socket.AF_INET,

socket.SOCK_STREAM) as s:
 s.connect(('localhost', NEXT_PORT))
 s.sendall("TOKEN".encode())
 except ConnectionRefusedError:
 print(f"Node {NODE_ID}: Could not connect to next
node {NEXT_NODE} on port {NEXT_PORT}")
 token = False
 token_received_event.clear()
 time.sleep(1)
if __name__ == "__main__":
 threading.Thread(target=listen_for_token, daemon=True).start()
 if TOKEN_HOLDER:
 token_received_event.set()
 pass_token(