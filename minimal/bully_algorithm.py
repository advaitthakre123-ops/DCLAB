import time
import random

class Node:
    """Node in distributed system"""
    
    def __init__(self, node_id, priority):
        self.id = node_id
        self.priority = priority
        self.is_alive = True
        self.is_coordinator = False
    
    def __repr__(self):
        status = "ALIVE" if self.is_alive else "DEAD"
        role = " [COORDINATOR]" if self.is_coordinator else ""
        return f"Node {self.id} (P={self.priority}) - {status}{role}"

class BullyElection:
    """Bully Algorithm implementation"""
    
    def __init__(self, nodes):
        self.nodes = sorted(nodes, key=lambda n: n.priority)
        self.coordinator = None
    
    def display_nodes(self):
        """Display all nodes"""
        print("\n--- Nodes Status ---")
        for node in self.nodes:
            print(node)
    
    def elect_leader(self, initiator_id):
        """
        Bully Algorithm:
        1. Node sends ELECTION message to all higher priority nodes
        2. If no response, declare itself coordinator
        3. If response received, higher node takes over election
        """
        print(f"\n{'='*60}")
        print(f"ELECTION INITIATED BY Node {initiator_id}")
        print(f"{'='*60}")
        
        initiator = next(n for n in self.nodes if n.id == initiator_id)
        
        if not initiator.is_alive:
            print(f"Node {initiator_id} is dead, cannot initiate election")
            return
        
        # Step 1: Send ELECTION to higher priority nodes
        higher_nodes = [n for n in self.nodes 
                       if n.priority > initiator.priority and n.is_alive]
        
        print(f"\nStep 1: Node {initiator_id} sends ELECTION to higher priority nodes")
        if higher_nodes:
            print(f"   Sending to: {[n.id for n in higher_nodes]}")
        else:
            print(f"   No higher priority nodes found")
        
        time.sleep(0.5)
        
        # Step 2: Check responses
        responses = []
        for node in higher_nodes:
            if node.is_alive:
                responses.append(node)
                print(f"   ← Node {node.id} responds: OK")
        
        time.sleep(0.5)
        
        # Step 3: Determine coordinator
        if not responses:
            # No response - become coordinator
            print(f"\nStep 2: No response received")
            print(f"Step 3: Node {initiator_id} becomes COORDINATOR")
            self.set_coordinator(initiator)
        else:
            # Higher nodes responded - they continue election
            highest = max(responses, key=lambda n: n.priority)
            print(f"\nStep 2: Response received from higher priority nodes")
            print(f"Step 3: Node {highest.id} (highest responder) becomes COORDINATOR")
            self.set_coordinator(highest)
        
        # Step 4: Announce coordinator
        print(f"\nStep 4: Broadcasting COORDINATOR message")
        print(f"   Node {self.coordinator.id} announces: I am the coordinator")
        
        print(f"\n{'='*60}")
        print(f"ELECTION COMPLETE - Coordinator: Node {self.coordinator.id}")
        print(f"{'='*60}")
    
    def set_coordinator(self, node):
        """Set node as coordinator"""
        for n in self.nodes:
            n.is_coordinator = False
        node.is_coordinator = True
        self.coordinator = node
    
    def simulate_failure(self, node_id):
        """Simulate node failure"""
        node = next(n for n in self.nodes if n.id == node_id)
        node.is_alive = False
        node.is_coordinator = False
        print(f"\n!!! Node {node_id} has FAILED !!!")
        
        if self.coordinator and self.coordinator.id == node_id:
            print(f"!!! Coordinator Node {node_id} has CRASHED !!!")
            self.coordinator = None

# Simulation
def main():
    print("=== BULLY ALGORITHM SIMULATION ===")
    
    # Create nodes with different priorities
    nodes = [
        Node(id=1, priority=10),
        Node(id=2, priority=25),
        Node(id=3, priority=30),
        Node(id=4, priority=45),
        Node(id=5, priority=50)
    ]
    
    election = BullyElection(nodes)
    election.display_nodes()
    
    # Initial election
    print("\n\n### Scenario 1: Initial Election ###")
    election.elect_leader(initiator_id=1)
    election.display_nodes()
    
    time.sleep(1)
    
    # Coordinator fails
    print("\n\n### Scenario 2: Coordinator Failure ###")
    election.simulate_failure(node_id=5)
    election.display_nodes()
    
    time.sleep(1)
    
    # New election
    print("\n\n### Scenario 3: Re-election ###")
    election.elect_leader(initiator_id=2)
    election.display_nodes()
    
    time.sleep(1)
    
    # Another failure
    print("\n\n### Scenario 4: Another Failure ###")
    election.simulate_failure(node_id=4)
    election.elect_leader(initiator_id=1)
    election.display_nodes()

if __name__ == '__main__':
    main()