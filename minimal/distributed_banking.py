import threading
import time
import random
from flask import Flask, request, jsonify

class BankingServer:
    def __init__(self, server_id, port):
        self.server_id = server_id
        self.port = port
        self.is_leader = False
        self.is_alive = True
        self.servers = {}  # {id: port}
        self.balance = 1000
        self.logical_clock = 0
        self.lock = threading.Lock()
        
    def bully_election(self):
        """Bully algorithm: highest ID wins"""
        print(f"Server {self.server_id}: Starting election")
        higher_servers = [sid for sid in self.servers.keys() if sid > self.server_id]
        
        if not higher_servers:
            self.is_leader = True
            print(f"Server {self.server_id}: I am the new leader!")
            return
        
        # In real implementation, send election messages to higher servers
        # For simulation, assume no response from crashed servers
        time.sleep(0.5)
        self.is_leader = True
        print(f"Server {self.server_id}: No response from higher servers, I am leader")
    
    def synchronize_clock(self):
        """Lamport logical clock - increments on each event"""
        with self.lock:
            self.logical_clock += 1
            return self.logical_clock
    
    def process_transaction(self, amount, operation):
        """Process transaction with logical clock"""
        timestamp = self.synchronize_clock()
        
        with self.lock:
            if operation == "deposit":
                self.balance += amount
            elif operation == "withdraw" and self.balance >= amount:
                self.balance -= amount
            else:
                return {"error": "Insufficient funds", "timestamp": timestamp}
        
        print(f"Server {self.server_id} [Clock={timestamp}]: {operation} ${amount}, Balance: ${self.balance}")
        return {"balance": self.balance, "timestamp": timestamp, "leader": self.server_id}

# Flask app for REST API
app = Flask(__name__)
server = BankingServer(server_id=1, port=5001)
server.servers = {1: 5001, 2: 5002, 3: 5003}

@app.route('/transaction', methods=['POST'])
def transaction():
    data = request.json
    result = server.process_transaction(data['amount'], data['operation'])
    return jsonify(result)

@app.route('/elect', methods=['POST'])
def elect_leader():
    server.bully_election()
    return jsonify({"leader": server.server_id, "is_leader": server.is_leader})

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"server_id": server.server_id, "is_leader": server.is_leader, 
                    "balance": server.balance, "clock": server.logical_clock})

if __name__ == '__main__':
    # Simulate crash and election
    threading.Timer(2, server.bully_election).start()
    app.run(port=5001, debug=False)

# CLIENT TEST:
# curl -X POST http://localhost:5001/transaction -H "Content-Type: application/json" -d '{"amount": 100, "operation": "deposit"}'
# curl -X POST http://localhost:5001/elect