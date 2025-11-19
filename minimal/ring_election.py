import time

class Process:
    """Process in ring topology"""
    
    def __init__(self, process_id):
        self.id = process_id
        self.is_alive = True
        self.is_leader = False
        self.next_process = None
    
    def __repr__(self):
        status = "ALIVE" if self.is_alive else "DEAD"
        leader = " [LEADER]" if self.is_leader else ""
        return f"P{self.id} ({status}){leader}"

class RingElection:
    """Ring Election Algorithm"""
    
    def __init__(self, num_processes):
        # Create processes
        self.processes = [Process(i) for i in range(num_processes)]
        
        # Create ring topology
        for i in range(num_processes):
            self.processes[i].next_process = self.processes[(i + 1) % num_processes]
        
        self.leader = None
    
    def display_ring(self):
        """Display ring structure"""
        print("\n--- Ring Status ---")
        for p in self.processes:
            print(p)
        print(f"Ring: P0 → P1 → P2 → ... → P{len(self.processes)-1} → P0")
    
    def elect_leader(self, initiator_id):
        """
        Ring Election Algorithm:
        1. Initiator sends ELECTION(id) message clockwise
        2. Each process adds its ID if alive and passes message
        3. When message returns to initiator, highest ID is leader
        4. Leader sends COORDINATOR message around ring
        """
        print(f"\n{'='*70}")
        print(f"RING ELECTION INITIATED BY Process {initiator_id}")
        print(f"{'='*70}")
        
        initiator = self.processes[initiator_id]
        if not initiator.is_alive:
            print(f"Process {initiator_id} is dead!")
            return
        
        # Phase 1: ELECTION - collect IDs
        print("\n--- Phase 1: ELECTION (Collecting Process IDs) ---")
        election_msg = [initiator.id]
        current = initiator.next_process
        
        print(f"P{initiator.id} starts election with message: {election_msg}")
        
        steps = 0
        while current.id != initiator.id and steps < len(self.processes) * 2:
            if current.is_alive:
                election_msg.append(current.id)
                print(f"P{current.id} adds its ID. Message: {election_msg}")
            else:
                print(f"P{current.id} is DEAD, skipping")
            
            current = current.next_process
            time.sleep(0.3)
            steps += 1
        
        print(f"\nElection message returned to P{initiator.id}")
        print(f"Final message: {election_msg}")
        
        # Phase 2: Determine leader
        leader_id = max(election_msg)
        print(f"\n--- Phase 2: COORDINATOR (Announcing Leader) ---")
        print(f"Highest ID: {leader_id} → Process {leader_id} is the new LEADER")
        
        # Phase 3: Send COORDINATOR message
        coordinator_msg = f"COORDINATOR: P{leader_id}"
        current = self.processes[(initiator_id + 1) % len(self.processes)]
        
        print(f"\nP{leader_id} sends COORDINATOR message around ring:")
        
        steps = 0
        while steps < len(self.processes):
            if current.is_alive:
                print(f"   P{current.id} receives: {coordinator_msg}")
                if current.id == leader_id:
                    current.is_leader = True
                else:
                    current.is_leader = False
            
            current = current.next_process
            steps += 1
        
        self.leader = self.processes[leader_id]
        
        print(f"\n{'='*70}")
        print(f"ELECTION COMPLETE - Leader: Process {leader_id}")
        print(f"{'='*70}")
    
    def simulate_failure(self, process_id):
        """Simulate process failure"""
        process = self.processes[process_id]
        process.is_alive = False
        process.is_leader = False
        print(f"\n!!! Process {process_id} has FAILED !!!")
        
        if self.leader and self.leader.id == process_id:
            print(f"!!! Leader Process {process_id} has CRASHED !!!")
            self.leader = None

# Simulation
def main():
    print("=== RING ELECTION ALGORITHM SIMULATION ===")
    
    # Create ring with 5 processes
    ring = RingElection(num_processes=5)
    ring.display_ring()
    
    # Scenario 1: Initial election
    print("\n\n### Scenario 1: Initial Election ###")
    ring.elect_leader(initiator_id=0)
    ring.display_ring()
    
    time.sleep(1)
    
    # Scenario 2: Leader fails
    print("\n\n### Scenario 2: Leader Failure ###")
    ring.simulate_failure(process_id=4)
    ring.display_ring()
    
    time.sleep(1)
    
    # Scenario 3: Re-election
    print("\n\n### Scenario 3: Re-election After Leader Failure ###")
    ring.elect_leader(initiator_id=1)
    ring.display_ring()
    
    time.sleep(1)
    
    # Scenario 4: Multiple failures
    print("\n\n### Scenario 4: Multiple Process Failures ###")
    ring.simulate_failure(process_id=3)
    ring.simulate_failure(process_id=2)
    ring.display_ring()
    
    time.sleep(1)
    
    print("\n\n### Scenario 5: Election with Limited Processes ###")
    ring.elect_leader(initiator_id=0)
    ring.display_ring()

if __name__ == '__main__':
    main()