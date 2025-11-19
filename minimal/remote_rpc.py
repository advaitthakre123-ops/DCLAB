from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
import threading
import time
# SERVER
class CodeExecutionServer:
    def execute_code(self, code_type, *args):
        """Execute different types of code safely"""
        try:
            if code_type == "add":
                return sum(args)
            elif code_type == "multiply":
                result = 1
                for x in args:
                    result *= x
                return result
            elif code_type == "sort":
                return sorted(list(args))
            elif code_type == "reverse":
                return args[0][::-1]
            else:
                return "Unknown operation"
        except Exception as e:
            return f"Error: {str(e)}"

def handle_client(client_id, server_address):
    """Thread function to handle client request"""
    print(f"Thread {client_id}: Processing request")

def start_server():
    server = SimpleXMLRPCServer(("localhost", 8000), allow_none=True)
    server.register_instance(CodeExecutionServer())
    print("Server running on port 8000...")
    server.serve_forever()

# CLIENT
def client_example():
    server = ServerProxy("http://localhost:8000")
    
    # Test various operations
    print("Add: 5 + 10 + 15 =", server.execute_code("add", 5, 10, 15))
    print("Multiply: 2 * 3 * 4 =", server.execute_code("multiply", 2, 3, 4))
    print("Sort: [5,1,9,3] =", server.execute_code("sort", 5, 1, 9, 3))
    print("Reverse: 'hello' =", server.execute_code("reverse", "hello"))

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'client':
        # Run as client
        time.sleep(1)  # Wait for server
        
        # Simulate multiple clients with threads
        threads = []
        for i in range(3):
            t = threading.Thread(target=client_example)
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
    else:
        # Run as server
        start_server()

# RUN:
# Terminal 1: python script.py
# Terminal 2: python script.py client