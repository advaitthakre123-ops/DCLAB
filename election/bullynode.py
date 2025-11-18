Import socket
import threading
import json
import time
import argparse
import random


SOCKET_TIMEOUT = 2.0


class BullyNode:
   def __init__(self, pid, nodes_config):
       self.pid = pid
       self.nodes = {int(p['pid']): p for p in nodes_config}
       self.host = self.nodes[pid]['host']
       self.port = self.nodes[pid]['port']
      
       self.higher_nodes = {p_id: config for p_id, config in self.nodes.items() if p_id > self.pid}
      
       self.coordinator_pid = None
       self.election_in_progress = False
       self.is_listening = True


       print(f"[{self.pid}] Node initialized. Listening on {self.host}:{self.port}")


   def listen(self):
       server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
       server_socket.bind((self.host, self.port))
       server_socket.listen(len(self.nodes))
      
       while self.is_listening:
           try:
               conn, addr = server_socket.accept()
               threading.Thread(target=self.handle_connection, args=(conn,)).start()
           except Exception as e:
               print(f"[{self.pid}] Error in listening socket: {e}")
               break
       server_socket.close()


   def handle_connection(self, conn):
       try:
           message_bytes = conn.recv(1024)
           if message_bytes:
               message = json.loads(message_bytes.decode())
               self.handle_message(message)
       except Exception as e:
           print(f"[{self.pid}] Error handling connection: {e}")
       finally:
           conn.close()


   def handle_message(self, message):
       msg_type = message.get("type")
       sender_pid = message.get("sender_pid")
      
       if msg_type == "ELECTION":
           print(f"[{self.pid}] Received ELECTION from {sender_pid}")
           response = {"type": "OK", "sender_pid": self.pid}
           self.send_message(self.nodes[sender_pid]['host'], self.nodes[sender_pid]['port'], response)
          
           if not self.election_in_progress:
               self.start_election()


       elif msg_type == "OK":
           print(f"[{self.pid}] Received OK from {sender_pid}")
           self.election_in_progress = True


       elif msg_type == "COORDINATOR":
           new_coordinator_pid = message.get("coordinator_pid")
           print(f"[{self.pid}] Received COORDINATOR message: new coordinator is {new_coordinator_pid}")
           self.coordinator_pid = new_coordinator_pid
           self.election_in_progress = False


   def send_message(self, target_host, target_port, message):
       try:
           with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
               s.settimeout(SOCKET_TIMEOUT)
               s.connect((target_host, target_port))
               s.sendall(json.dumps(message).encode())
           return True
       except (socket.timeout, ConnectionRefusedError):
           return False
       except Exception as e:
           print(f"[{self.pid}] Error sending message to {target_host}:{target_port}: {e}")
           return False


   def start_election(self):
       print(f"[{self.pid}] Initiating election...")
       self.election_in_progress = True
      
       responses = []
       for pid, config in self.higher_nodes.items():
           message = {"type": "ELECTION", "sender_pid": self.pid}
           response_ok = self.send_message(config['host'], config['port'], message)
           if response_ok:
               responses.append(pid)


       if not responses:
           print(f"[{self.pid}] No response from higher nodes. I am the new COORDINATOR.")
           self.coordinator_pid = self.pid
           self.announce_coordinator()
       else:
           print(f"[{self.pid}] Got OK from a higher process; waiting for COORDINATOR announcement...")


   def announce_coordinator(self):
       self.election_in_progress = False
       message = {"type": "COORDINATOR", "coordinator_pid": self.pid}
       for pid, config in self.nodes.items():
           if pid != self.pid:
               self.send_message(config['host'], config['port'], message)


   def heartbeat(self):
       while True:
           time.sleep(random.uniform(3, 5))


           if self.coordinator_pid is None:
               print(f"[{self.pid}] No coordinator known. Starting initial election.")
               self.start_election()
               continue
          
           if self.pid == self.coordinator_pid:
               continue


           coord_config = self.nodes.get(self.coordinator_pid)
           if not coord_config or not self.send_message(coord_config['host'], coord_config['port'], {"type": "PING"}):
               print(f"[{self.pid}] Coordinator {self.coordinator_pid} not responding -> starting election.")
               self.start_election()


   def run(self):
       listener_thread = threading.Thread(target=self.listen)
       listener_thread.daemon = True
       listener_thread.start()


       self.heartbeat()


if __name__ == "__main__":
   parser = argparse.ArgumentParser(description="Bully Algorithm Node")
   parser.add_argument("--pid", type=int, required=True, help="Process ID of this node")
   args = parser.parse_args()


   with open("nodes.json", "r") as f:
       nodes_config = json.load(f)


   node = BullyNode(args.pid, nodes_config)
   node.run()