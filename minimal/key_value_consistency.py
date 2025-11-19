import threading
import time
from datetime import datetime

class Replica:
    """Replica node for key-value store"""
    
    def __init__(self, replica_id):
        self.id = replica_id
        self.data = {}
        self.lock = threading.Lock()
        self.version = {}  # Track version numbers
    
    def put(self, key, value):
        """Store key-value pair"""
        with self.lock:
            self.data[key] = value
            self.version[key] = self.version.get(key, 0) + 1
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            print(f"[{timestamp}] Replica {self.id}: PUT {key}={value} (v{self.version[key]})")
    
    def get(self, key):
        """Retrieve value"""
        with self.lock:
            return self.data.get(key, None)
    
    def get_all(self):
        """Get all data"""
        with self.lock:
            return self.data.copy()
    
    def display(self):
        """Display replica state"""
        with self.lock:
            print(f"Replica {self.id}: {self.data}")

class DistributedKVStore:
    """Distributed Key-Value Store with replication"""
    
    def __init__(self, num_replicas=3):
        self.replicas = [Replica(i) for i in range(num_replicas)]
        self.propagation_delay = 2  # seconds
    
    def write_with_strong_consistency(self, key, value):
        """Strong consistency: write to all replicas immediately"""
        print(f"\n--- STRONG CONSISTENCY WRITE ---")
        print(f"Writing {key}={value} to all replicas synchronously")
        
        for replica in self.replicas:
            replica.put(key, value)
        
        print("All replicas updated immediately")
        self.display_all()
    
    def write_with_eventual_consistency(self, key, value):
        """Eventual consistency: write to primary, propagate later"""
        print(f"\n--- EVENTUAL CONSISTENCY WRITE ---")
        print(f"Writing {key}={value} to primary replica only")
        
        # Write to primary (Replica 0)
        self.replicas[0].put(key, value)
        
        print(f"\nState immediately after write:")
        self.display_all()
        
        # Propagate to other replicas after delay
        def propagate():
            time.sleep(self.propagation_delay)
            print(f"\n[After {self.propagation_delay}s delay] Propagating to other replicas...")
            for replica in self.replicas[1:]:
                replica.put(key, value)
            
            print(f"\nState after propagation:")
            self.display_all()
            print("✓ All replicas eventually consistent")
        
        threading.Thread(target=propagate, daemon=True).start()
    
    def read_from_replica(self, replica_id, key):
        """Read from specific replica"""
        value = self.replicas[replica_id].get(key)
        print(f"Read {key} from Replica {replica_id}: {value}")
        return value
    
    def display_all(self):
        """Display all replicas"""
        print("-" * 50)
        for replica in self.replicas:
            replica.display()
        print("-" * 50)

# Simulation
def main():
    print("=== DISTRIBUTED KEY-VALUE STORE ===")
    print("Demonstrating Strong vs Eventual Consistency\n")
    
    store = DistributedKVStore(num_replicas=3)
    
    # Demo 1: Strong Consistency
    print("\n" + "="*60)
    print("DEMO 1: STRONG CONSISTENCY")
    print("="*60)
    store.write_with_strong_consistency("user:1", "Alice")
    store.write_with_strong_consistency("user:2", "Bob")
    
    print("\nReading from any replica gives same result:")
    store.read_from_replica(0, "user:1")
    store.read_from_replica(1, "user:1")
    store.read_from_replica(2, "user:1")
    
    time.sleep(1)
    
    # Demo 2: Eventual Consistency
    print("\n\n" + "="*60)
    print("DEMO 2: EVENTUAL CONSISTENCY")
    print("="*60)
    store.write_with_eventual_consistency("user:3", "Charlie")
    
    print("\nImmediate read from different replicas:")
    print("(Replicas 1 & 2 don't have the data yet)")
    store.read_from_replica(0, "user:3")  # Has data
    store.read_from_replica(1, "user:3")  # Doesn't have data yet
    store.read_from_replica(2, "user:3")  # Doesn't have data yet
    
    print("\nWaiting for propagation...")
    time.sleep(3)
    
    print("\nRead after propagation delay:")
    store.read_from_replica(0, "user:3")
    store.read_from_replica(1, "user:3")
    store.read_from_replica(2, "user:3")
    
    # Demo 3: Multiple updates with eventual consistency
    print("\n\n" + "="*60)
    print("DEMO 3: MULTIPLE UPDATES (Eventual Consistency)")
    print("="*60)
    
    store.write_with_eventual_consistency("counter", "1")
    time.sleep(0.5)
    store.write_with_eventual_consistency("counter", "2")
    time.sleep(0.5)
    store.write_with_eventual_consistency("counter", "3")
    
    print("\n--- Summary ---")
    print("Strong Consistency: All replicas updated synchronously (slow, consistent)")
    print("Eventual Consistency: Primary updated first, replicas later (fast, eventually consistent)")
    
    time.sleep(3)  # Wait for all propagations

if __name__ == '__main__':
    main()