import threading
import time
import random
from collections import defaultdict

class BackendServer:
    """Backend server that processes requests"""
    
    def __init__(self, server_id):
        self.id = server_id
        self.request_count = 0
        self.lock = threading.Lock()
    
    def process_request(self, request_id):
        """Process a request"""
        with self.lock:
            self.request_count += 1
            processing_time = random.uniform(0.1, 0.5)
        
        print(f"  Server {self.id}: Processing request #{request_id}")
        time.sleep(processing_time)
        print(f"  Server {self.id}: Completed request #{request_id} (Total: {self.request_count})")
        
        return f"Response from Server {self.id}"
    
    def get_stats(self):
        """Get server statistics"""
        with self.lock:
            return {
                "server_id": self.id,
                "requests_processed": self.request_count
            }

class LoadBalancer:
    """Load Balancer with Round Robin algorithm"""
    
    def __init__(self, num_servers=3):
        self.servers = [BackendServer(i) for i in range(num_servers)]
        self.current_index = 0
        self.lock = threading.Lock()
        self.total_requests = 0
    
    def get_next_server_round_robin(self):
        """Round Robin: Select next server in circular order"""
        with self.lock:
            server = self.servers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.servers)
            return server
    
    def get_next_server_least_connections(self):
        """Least Connections: Select server with fewest requests"""
        with self.lock:
            # Find server with minimum request count
            server = min(self.servers, key=lambda s: s.request_count)
            return server
    
    def distribute_request(self, request_id, algorithm="round_robin"):
        """Distribute request to backend server"""
        with self.lock:
            self.total_requests += 1
        
        # Select server based on algorithm
        if algorithm == "round_robin":
            server = self.get_next_server_round_robin()
        elif algorithm == "least_connections":
            server = self.get_next_server_least_connections()
        else:
            server = self.servers[0]
        
        print(f"Request #{request_id} → Server {server.id}")
        
        # Process request
        response = server.process_request(request_id)
        return response
    
    def display_load_distribution(self):
        """Display load distribution across servers"""
        print("\n" + "="*60)
        print("LOAD DISTRIBUTION")
        print("="*60)
        print(f"{'Server':<15} {'Requests':<15} {'Percentage':<15}")
        print("-"*60)
        
        for server in self.servers:
            stats = server.get_stats()
            percentage = (stats['requests_processed'] / self.total_requests * 100) if self.total_requests > 0 else 0
            print(f"Server {stats['server_id']:<8} {stats['requests_processed']:<15} {percentage:.1f}%")
        
        print("="*60)
        print(f"Total Requests: {self.total_requests}")
        print("="*60)

def simulate_requests(load_balancer, num_requests, algorithm):
    """Simulate incoming requests"""
    print(f"\nSimulating {num_requests} requests with {algorithm.upper()} algorithm\n")
    
    threads = []
    for i in range(num_requests):
        t = threading.Thread(
            target=load_balancer.distribute_request,
            args=(i+1, algorithm)
        )
        threads.append(t)
        t.start()
        time.sleep(0.1)  # Simulate request arrival
    
    # Wait for all requests to complete
    for t in threads:
        t.join()

def main():
    print("=== LOAD BALANCER SIMULATION ===\n")
    
    # Demo 1: Round Robin
    print("\n" + "="*60)
    print("DEMO 1: ROUND ROBIN LOAD BALANCING")
    print("="*60)
    
    lb_round_robin = LoadBalancer(num_servers=3)
    simulate_requests(lb_round_robin, num_requests=12, algorithm="round_robin")
    time.sleep(1)
    lb_round_robin.display_load_distribution()
    
    time.sleep(2)
    
    # Demo 2: Least Connections
    print("\n\n" + "="*60)
    print("DEMO 2: LEAST CONNECTIONS LOAD BALANCING")
    print("="*60)
    
    lb_least_conn = LoadBalancer(num_servers=3)
    simulate_requests(lb_least_conn, num_requests=12, algorithm="least_connections")
    time.sleep(1)
    lb_least_conn.display_load_distribution()
    
    print("\n--- Algorithm Comparison ---")
    print("Round Robin: Distributes requests evenly in circular order")
    print("Least Connections: Sends requests to server with fewest active connections")

if __name__ == '__main__':
    main()