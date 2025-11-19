from flask import Flask, jsonify
import threading
import time
import uuid
import random

app = Flask(__name__)

class APIKeyManager:
    def __init__(self):
        self.keys = {}  # {key: {"status": "available/blocked", "created": timestamp, "last_keepalive": timestamp}}
        self.lock = threading.Lock()
        
        # Start cleanup threads
        threading.Thread(target=self.auto_delete_expired, daemon=True).start()
        threading.Thread(target=self.auto_unblock, daemon=True).start()
    
    def create_key(self):
        """Generate new API key"""
        with self.lock:
            key = str(uuid.uuid4())[:8]
            self.keys[key] = {
                "status": "available",
                "created": time.time(),
                "last_keepalive": time.time()
            }
            print(f"Created key: {key}")
            return key
    
    def get_available_key(self):
        """Get and block an available key"""
        with self.lock:
            for key, info in self.keys.items():
                if info["status"] == "available":
                    info["status"] = "blocked"
                    info["blocked_at"] = time.time()
                    print(f"Key {key} blocked")
                    return key
            return None
    
    def unblock_key(self, key):
        """Unblock a key"""
        with self.lock:
            if key in self.keys:
                self.keys[key]["status"] = "available"
                print(f"Key {key} unblocked")
                return True
            return False
    
    def keepalive(self, key):
        """Reset keepalive timer"""
        with self.lock:
            if key in self.keys:
                self.keys[key]["last_keepalive"] = time.time()
                print(f"Keepalive: {key}")
                return True
            return False
    
    def auto_delete_expired(self):
        """Delete keys after 5 minutes without keepalive"""
        while True:
            time.sleep(10)
            with self.lock:
                current_time = time.time()
                to_delete = []
                for key, info in self.keys.items():
                    if current_time - info["last_keepalive"] > 300:  # 5 minutes
                        to_delete.append(key)
                for key in to_delete:
                    del self.keys[key]
                    print(f"Auto-deleted expired key: {key}")
    
    def auto_unblock(self):
        """Unblock keys after 60 seconds"""
        while True:
            time.sleep(5)
            with self.lock:
                current_time = time.time()
                for key, info in self.keys.items():
                    if info["status"] == "blocked":
                        if "blocked_at" in info and current_time - info["blocked_at"] > 60:
                            info["status"] = "available"
                            print(f"Auto-unblocked: {key}")

manager = APIKeyManager()

@app.route('/create', methods=['POST'])
def create():
    key = manager.create_key()
    return jsonify({"key": key})

@app.route('/get', methods=['GET'])
def get_key():
    key = manager.get_available_key()
    if key:
        return jsonify({"key": key})
    return jsonify({"error": "No keys available"}), 404

@app.route('/unblock/<key>', methods=['POST'])
def unblock(key):
    success = manager.unblock_key(key)
    return jsonify({"success": success})

@app.route('/keepalive/<key>', methods=['POST'])
def keepalive(key):
    success = manager.keepalive(key)
    return jsonify({"success": success})

@app.route('/status', methods=['GET'])
def status():
    return jsonify({"keys": manager.keys})

if __name__ == '__main__':
    app.run(port=5000, debug=False)

# TEST:
# curl -X POST http://localhost:5000/create
# curl http://localhost:5000/get
# curl -X POST http://localhost:5000/keepalive/YOUR_KEY
# curl http://localhost:5000/status