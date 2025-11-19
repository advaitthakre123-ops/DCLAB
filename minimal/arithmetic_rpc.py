from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
import time

# SERVER
class ArithmeticService:
    """Remote arithmetic operations"""
    
    def add(self, a, b):
        """Addition"""
        result = a + b
        print(f"Server: add({a}, {b}) = {result}")
        return result
    
    def subtract(self, a, b):
        """Subtraction"""
        result = a - b
        print(f"Server: subtract({a}, {b}) = {result}")
        return result
    
    def multiply(self, a, b):
        """Multiplication"""
        result = a * b
        print(f"Server: multiply({a}, {b}) = {result}")
        return result
    
    def divide(self, a, b):
        """Division with error handling"""
        if b == 0:
            return "Error: Division by zero"
        result = a / b
        print(f"Server: divide({a}, {b}) = {result}")
        return result

def start_server():
    """Start RPC server"""
    server = SimpleXMLRPCServer(("localhost", 9000), allow_none=True)
    server.register_instance(ArithmeticService())
    print("Arithmetic RPC Server running on port 9000...")
    print("Waiting for client requests...")
    server.serve_forever()

# CLIENT
def run_client():
    """Client invoking remote methods"""
    print("Connecting to RPC server...")
    server = ServerProxy("http://localhost:9000")
    
    print("\n--- Remote Method Invocations ---")
    
    # Addition
    result = server.add(15, 25)
    print(f"Client received: 15 + 25 = {result}")
    
    # Subtraction
    result = server.subtract(50, 20)
    print(f"Client received: 50 - 20 = {result}")
    
    # Multiplication
    result = server.multiply(7, 8)
    print(f"Client received: 7 * 8 = {result}")
    
    # Division
    result = server.divide(100, 4)
    print(f"Client received: 100 / 4 = {result}")
    
    # Division by zero
    result = server.divide(10, 0)
    print(f"Client received: 10 / 0 = {result}")
    
    print("\n--- Marshalling/Unmarshalling Demonstration ---")
    print("Data is automatically serialized (marshalled) by XML-RPC")
    print("and deserialized (unmarshalled) on both ends")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'client':
        time.sleep(1)  # Wait for server to start
        run_client()
    else:
        start_server()

# RUN:
# Terminal 1: python script.py
# Terminal 2: python script.py client