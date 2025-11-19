import threading
import time

class VectorClock:
    """Vector Clock implementation"""
    
    def __init__(self, process_id, num_processes):
        self.process_id = process_id
        self.clock = [0] * num_processes
        self.lock = threading.Lock()
    
    def tick(self):
        """Increment own clock on internal event"""
        with self.lock:
            self.clock[self.process_id] += 1
            return self.clock.copy()
    
    def send_event(self):
        """Update clock before sending message"""
        return self.tick()
    
    def receive_event(self, received_clock):
        """Update clock on receiving message"""
        with self.lock:
            for i in range(len(self.clock)):
                self.clock[i] = max(self.clock[i], received_clock[i])
            self.clock[self.process_id] += 1
            return self.clock.copy()
    
    def __str__(self):
        return str(self.clock)

class Process:
    """Distributed process with vector clock"""
    
    def __init__(self, process_id, num_processes):
        self.id = process_id
        self.clock = VectorClock(process_id, num_processes)
        self.message_queue = []
    
    def internal_event(self, event_name):
        """Execute internal event"""
        timestamp = self.clock.tick()
        print(f"P{self.id}: {event_name} | VC={timestamp}")
        return timestamp
    
    def send_message(self, receiver, message):
        """Send message to another process"""
        timestamp = self.clock.send_event()
        print(f"P{self.id} → P{receiver.id}: {message} | VC={timestamp}")
        receiver.receive_message(self.id, message, timestamp)
    
    def receive_message(self, sender_id, message, sender_clock):
        """Receive message from another process"""
        self.message_queue.append((sender_id, message, sender_clock))
    
    def process_messages(self):
        """Process received messages"""
        while self.message_queue:
            sender_id, message, sender_clock = self.message_queue.pop(0)
            timestamp = self.clock.receive_event(sender_clock)
            print(f"P{self.id} ← P{sender_id}: Received '{message}' | VC={timestamp}")

def compare_events(vc1, vc2):
    """Compare two vector clock timestamps"""
    less = all(vc1[i] <= vc2[i] for i in range(len(vc1)))
    greater = all(vc1[i] >= vc2[i] for i in range(len(vc1)))
    
    if less and vc1 != vc2:
        return "happened-before"
    elif greater and vc1 != vc2:
        return "happened-after"
    elif vc1 == vc2:
        return "concurrent/same"
    else:
        return "concurrent"

# Simulation
def main():
    print("=== Vector Clock Simulation ===\n")
    
    # Create 3 processes
    num_processes = 3
    p0 = Process(0, num_processes)
    p1 = Process(1, num_processes)
    p2 = Process(2, num_processes)
    
    # Simulate distributed events
    print("--- Internal Events ---")
    t1 = p0.internal_event("Event A")
    t2 = p1.internal_event("Event B")
    
    print("\n--- Message Passing ---")
    time.sleep(0.1)
    p0.send_message(p1, "Hello from P0")
    time.sleep(0.1)
    p1.process_messages()
    
    time.sleep(0.1)
    t3 = p1.internal_event("Event C")
    
    time.sleep(0.1)
    p1.send_message(p2, "Data from P1")
    time.sleep(0.1)
    p2.process_messages()
    
    time.sleep(0.1)
    p2.send_message(p0, "Response from P2")
    time.sleep(0.1)
    p0.process_messages()
    
    print("\n--- Event Ordering Analysis ---")
    print(f"Event A (P0): {t1}")
    print(f"Event B (P1): {t2}")
    print(f"Event C (P1): {t3}")
    print(f"Relationship A→B: {compare_events(t1, t2)}")
    print(f"Relationship A→C: {compare_events(t1, t3)}")

if __name__ == '__main__':
    main()