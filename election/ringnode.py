import json, socket, threading, time, argparse


parser = argparse.ArgumentParser()
parser.add_argument("--pid", type=int, required=True)
args = parser.parse_args()


with open("ring_nodes.json") as f:
   nodes = json.load(f)


PID = args.pid
me = next(n for n in nodes if n["pid"] == PID)
HOST, PORT = me["host"], me["port"]


next_node = nodes[(nodes.index(me) + 1) % len(nodes)]
coordinator = None
alive = True
last_election = 0


PING_INTERVAL = 5       
ELECTION_INTERVAL = 10  


def get_node(pid):
   for n in nodes:
       if n["pid"] == pid:
           return n
   return None


def send_message(target, msg):
   """Try to send message; if unreachable, skip to next alive node."""
   try:
       s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       s.connect((target["host"], target["port"]))
       s.send(msg.encode())
       s.close()
   except:
       target_pid = target["pid"]
       idx = next((i for i, n in enumerate(nodes) if n["pid"] == target_pid), None)
       if idx is not None:
           next_idx = (idx + 1) % len(nodes)
           next_target = nodes[next_idx]
           if next_target["pid"] != PID:
               print(f"[{PID}] Skipping dead node {target_pid}, forwarding to {next_target['pid']}")
               send_message(next_target, msg)


def start_election(force=False):
   """Begin a ring election."""
   global last_election, coordinator
   now = time.time()
   if not force and now - last_election < ELECTION_INTERVAL:
       return
   last_election = now
   coordinator = None
   print(f"[{PID}] Initiating election...")
   send_message(next_node, f"ELECTION|{PID}|{PID}")


def heartbeat():
   """Ping coordinator; if no response, start election."""
   global coordinator
   while alive:
       time.sleep(PING_INTERVAL)
       if coordinator and coordinator != PID:
           coord_node = get_node(coordinator)
           if not coord_node:
               continue
           try:
               s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
               s.settimeout(2)
               s.connect((coord_node["host"], coord_node["port"]))
               s.send(f"PING|{PID}".encode())
               s.close()
           except:
               print(f"[{PID}] Coordinator {coordinator} not responding -> starting election")
               coordinator = None
               start_election(force=True)


       elif not coordinator and PID == max(n["pid"] for n in nodes):
           print(f"[{PID}] I am the highest PID alive -> becoming coordinator")
           coordinator = PID
           send_message(next_node, f"COORDINATOR|{PID}")


def handle_client(conn):
   global coordinator
   try:
       msg = conn.recv(1024).decode()
       parts = msg.split("|")
       t = parts[0]


       if t == "ELECTION":
           origin = int(parts[1])
           ids = list(map(int, parts[2].split(","))) if "," in parts[2] else [int(parts[2])]
           if PID not in ids:
               ids.append(PID)
           if origin == PID:
               new_coord = max(ids)
               coordinator = new_coord
               print(f"[{PID}] ELECTION result -> coordinator = {new_coord}")
               send_message(next_node, f"COORDINATOR|{new_coord}")
           else:
               send_message(next_node, f"ELECTION|{origin}|{','.join(map(str, ids))}")


       elif t == "COORDINATOR":
           new_coord = int(parts[1])
           coordinator = new_coord
           print(f"[{PID}] Received COORDINATOR announcement: {new_coord}")
           if new_coord != PID:
               send_message(next_node, msg)


       elif t == "PING":


           pass
   finally:
       conn.close()


def server():
   s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   s.bind((HOST, PORT))
   s.listen(5)
   print(f"[{PID}] Listening on {HOST}:{PORT} | next -> {next_node['pid']} @ {next_node['host']}:{next_node['port']}")
   threading.Thread(target=start_election, daemon=True).start()
   threading.Thread(target=heartbeat, daemon=True).start()
   while alive:
       conn, _ = s.accept()
       threading.Thread(target=handle_client, args=(conn,)).start()


threading.Thread(target=server).start()