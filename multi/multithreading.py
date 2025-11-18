from flask import Flask, jsonify
import numpy as np
import threading
import time
import psutil


app = Flask(__name__)
def add_matrix_threads(A, B, num_threads=4):
   rows = A.shape[0]
   result = np.zeros_like(A)
   chunk = rows // num_threads
   threads = []
   def worker(start, end):
       result[start:end] = A[start:end] + B[start:end]
   for i in range(num_threads):
       start = i * chunk
       end = rows if i == num_threads - 1 else (i + 1) * chunk
       t = threading.Thread(target=worker, args=(start, end))
       threads.append(t)
       t.start()
   for t in threads:
       t.join()
   return result
def get_system_usage():
   # CPU usage (percentage of total CPU usage)
   cpu_percent = psutil.cpu_percent(interval=1)
   # Memory usage (in MB)
   memory_info = psutil.virtual_memory()
   memory_used = memory_info.used / (1024 ** 2)  # in MB
   memory_total = memory_info.total / (1024 ** 2)  # in MB
   memory_percent = memory_info.percent
   return {
       "cpu_percent": cpu_percent,
       "memory_used_mb": round(memory_used, 2),
       "memory_total_mb": round(memory_total, 2),
       "memory_percent": memory_percent
   }
@app.route("/threading")
def threading_add():
   N = 500
   A = np.random.randint(0, 100, (N, N))
   B = np.random.randint(0, 100, (N, N))
   # Capture system usage before running the computation
   system_before = get_system_usage()
   t0 = time.time()
   result = add_matrix_threads(A, B, num_threads=4)
   t1 = time.time()
   # Capture system usage after running the computation
   system_after = get_system_usage()
   return jsonify({
       "status": "ok",
       "method": "Multithreading",
       "execution_time_sec": round(t1 - t0, 4),
       "sample": result[0, :10].tolist(),
       "system_before": system_before,
       "system_after": system_after
   })
@app.route("/")
def index():
   return "Matrix Addition (Multithreading) API"
if __name__ == "__main__":
   app.run(debug=True)