from flask import Flask, jsonify
import numpy as np
import multiprocessing as mp
import time
import platform
import psutil


app = Flask(__name__)
# Worker function to add the sub-matrices
def worker_process(A, B, start, end, shared_result):
   try:
       # Perform matrix addition for the given range
       shared_result[start:end] = A[start:end] + B[start:end]
   except Exception as e:
       print(f"Error in worker {start}-{end}: {e}")
       raise e  # Re-raise exception to propagate it to the main process
# Main function to add matrices using multiprocessing
def add_matrix_processes(A, B, num_processes=4, timeout=60):
   rows = A.shape[0]
   result = np.zeros_like(A)
   # Shared memory for result
   shared_result = mp.Array('d', result.flatten())  # Shared memory for the result
   chunk = rows // num_processes
   procs = []
   # Divide the task into sub-processes
   for i in range(num_processes):
       start = i * chunk
       end = rows if i == num_processes - 1 else (i + 1) * chunk
       p = mp.Process(target=worker_process, args=(A, B, start, end, shared_result))
       procs.append(p)
       p.start()
   # Wait for all processes with a timeout
   for p in procs:
       p.join(timeout)
       if p.is_alive():
           print(f"Process {p} timed out.")
           p.terminate()
   # Convert shared memory back into a NumPy array
   result = np.frombuffer(shared_result.get_obj()).reshape(A.shape)
   return result
# Function to get system resource usage (CPU and memory)
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


@app.route("/multiprocessing")
def processing_add():
   # Matrix size (can adjust N for smaller testing)
   N = 500
   A = np.random.randint(0, 100, (N, N))
   B = np.random.randint(0, 100, (N, N))
   # Capture system usage before running the computation
   system_before = get_system_usage()
   # Start the matrix addition
   t0 = time.time()
   try:
       result = add_matrix_processes(A, B, num_processes=4, timeout=60)
   except Exception as e:
       return jsonify({
           "status": "error",
           "message": f"Error during matrix addition: {e}"
       })
   t1 = time.time()
   # Capture system usage after running the computation
   system_after = get_system_usage()
   return jsonify({
       "status": "ok",
       "method": "Multiprocessing",
       "execution_time_sec": round(t1 - t0, 4),
       "sample": result[0, :10].tolist(),
       "system_before": system_before,
       "system_after": system_after
   })


@app.route("/")
def index():
   return "Matrix Addition (Multiprocessing) API"
if __name__ == "__main__":
   # Set the correct start method for multiprocessing depending on OS
   if platform.system() == "Windows":
       mp.set_start_method("spawn", force=True)
   else:
       mp.set_start_method("fork")
   # Run Flask app
   app.run(debug=True, port=8002)