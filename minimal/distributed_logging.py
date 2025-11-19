import threading
import time
import random
from datetime import datetime

class LamportClock:
    """Lamport Logical Clock for event ordering"""
    def __init__(self):
        self.clock = 0
        self.lock = threading.Lock()
    
    def tick(self):
        with self.lock:
            self.clock += 1
            return self.clock
    
    def update(self, received_clock):
        with self.lock:
            self.clock = max(self.clock, received_clock) + 1
            return self.clock

class DistributedServer:
    def __init__(self, server_id):
        self.server_id = server_id
        self.clock = LamportClock()
        self.logs = []
    
    def generate_log(self, event):
        """Generate log with Lamport timestamp"""
        timestamp = self.clock.tick()
        raw_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        log = {
            "server_id": self.server_id,
            "event": event,
            "lamport_clock": timestamp,
            "raw_timestamp": raw_time
        }
        self.logs.append(log)
        print(f"Server {self.server_id} [LC={timestamp}]: {event}")
        return log

class LogManager:
    def __init__(self):
        self.all_logs = []
        self.lock = threading.Lock()
    
    def collect_log(self, log):
        """Collect log from servers"""
        with self.lock:
            self.all_logs.append(log)
    
    def display_ordered_logs(self):
        """Display logs ordered by Lamport clock"""
        sorted_logs = sorted(self.all_logs, key=lambda x: (x["lamport_clock"], x["server_id"]))
        
        print("\n" + "="*70)
        print("CENTRALIZED LOGS (Ordered by Lamport Clock)")
        print("="*70)
        print(f"{'LC':<5} {'Server':<8} {'Raw Time':<15} {'Event':<30}")
        print("-"*70)
        
        for log in sorted_logs:
            print(f"{log['lamport_clock']:<5} {log['server_id']:<8} {log['raw_timestamp']:<15} {log['event']:<30}")
        print("="*70)

# Simulation
def simulate_server(server_id, log_manager):
    """Simulate server generating logs"""
    server = DistributedServer(server_id)
    
    events = [
        "User login",
        "Database query",
        "File upload",
        "Cache miss",
        "API request"
    ]
    
    for i in range(3):
        time.sleep(random.uniform(0.1, 0.5))
        event = random.choice(events)
        log = server.generate_log(f"{event} #{i+1}")
        log_manager.collect_log(log)

def main():
    log_manager = LogManager()
    
    # Create 3 servers
    threads = []
    for i in range(1, 4):
        t = threading.Thread(target=simulate_server, args=(f"S{i}", log_manager))
        threads.append(t)
        t.start()
    
    # Wait for all servers
    for t in threads:
        t.join()
    
    # Display ordered logs
    time.sleep(0.5)
    log_manager.display_ordered_logs()

if __name__ == '__main__':
    main()

# Uses Lamport Logical Clocks because:
# - Physical clock sync is complex and unnecessary for log ordering
# - Lamport ensures causal ordering of events
# - Simple to implement in distributed systems
# - No need for time server coordination