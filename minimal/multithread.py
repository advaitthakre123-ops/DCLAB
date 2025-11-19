import socket
import threading
import time

class MultithreadedServer:
    """Server that handles multiple clients with threads"""
    
    def __init__(self, host='localhost', port=9999):
        self.host = host
        self.port = port
        self.server_socket = None
        self.active_threads = []
    
    def handle_client(self, client_socket, address):
        """Handle individual client in separate thread"""
        thread_id = threading.get_ident()
        print(f"[Thread {thread_id}] Connected to client {address}")
        
        try:
            # Receive data from client
            data = client_socket.recv(1024).decode('utf-8')
            print(f"[Thread {thread_id}] Received: {data}")
            
            # Process request (text processing)
            if data.startswith("UPPER:"):
                result = data[6:].upper()
            elif data.startswith("LOWER:"):
                result = data[6:].lower()
            elif data.startswith("REVERSE:"):
                result = data[8:][::-1]
            elif data.startswith("COUNT:"):
                result = f"Length: {len(data[6:])}"
            else:
                result = f"Echo: {data}"
            
            # Simulate processing time
            time.sleep(1)
            
            # Send response
            response = f"Processed by Thread {thread_id}: {result}\n"
            client_socket.send(response.encode('utf-8'))
            print(f"[Thread {thread_id}] Sent response to {address}")
            
        except Exception as e:
            print(f"[Thread {thread_id}] Error: {e}")
        finally:
            client_socket.close()
            print(f"[Thread {thread_id}] Connection closed with {address}")
    
    def start(self):
        """Start the server"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        print(f"Server listening on {self.host}:{self.port}")
        print("Waiting for clients...\n")
        
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                
                # Create new thread for each client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.start()
                self.active_threads.append(client_thread)
                
                print(f"Active threads: {threading.active_count() - 1}\n")
                
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            self.server_socket.close()

class ClientSimulator:
    """Simulate multiple clients"""
    
    @staticmethod
    def send_request(client_id, message, host='localhost', port=9999):
        """Send request to server"""
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((host, port))
            
            print(f"Client {client_id}: Sending '{message}'")
            client_socket.send(message.encode('utf-8'))
            
            response = client_socket.recv(1024).decode('utf-8')
            print(f"Client {client_id}: {response}")
            
            client_socket.close()
        except Exception as e:
            print(f"Client {client_id} Error: {e}")
    
    @staticmethod
    def simulate_clients():
        """Simulate multiple concurrent clients"""
        print("Simulating 5 concurrent clients...\n")
        
        requests = [
            "UPPER:hello world",
            "LOWER:PYTHON SERVER",
            "REVERSE:multithreading",
            "COUNT:this is a test message",
            "ECHO:simple echo test"
        ]
        
        threads = []
        for i, request in enumerate(requests):
            time.sleep(0.2)  # Slight delay between clients
            t = threading.Thread(
                target=ClientSimulator.send_request,
                args=(i+1, request)
            )
            t.start()
            threads.append(t)
        
        for t in threads:
            t.join()
        
        print("\nAll clients completed!")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'client':
        # Run as client simulator
        time.sleep(1)  # Wait for server to start
        ClientSimulator.simulate_clients()
    else:
        # Run as server
        server = MultithreadedServer()
        server.start()

# RUN:
# Terminal 1: python script.py
# Terminal 2: python script.py client
#
# OR use curl/netcat:
# echo "UPPER:hello" | nc localhost 9999