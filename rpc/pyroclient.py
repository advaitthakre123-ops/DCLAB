import Pyro5.api
import time
import psutil
import sys
import random


# Replace this with the actual URI printed by your server
uri = "PYRO:obj_553a3e67656747329f11d5052d62fcf5@localhost:43837"  # placeholder


def get_size(obj, seen=None):
   """Recursively finds size of objects for bandwidth approx."""
   size = sys.getsizeof(obj)
   if seen is None:
       seen = set()
   obj_id = id(obj)
   if obj_id in seen:
       return 0
   seen.add(obj_id)
   if isinstance(obj, dict):
       size += sum([get_size(v, seen) + get_size(k, seen) for k, v in obj.items()])
   elif hasattr(obj, '__dict__'):
       size += get_size(obj.__dict__, seen)
   elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
       size += sum([get_size(i, seen) for i in obj])
   return size


def benchmark_requests(calculator, num_requests):
   process = psutil.Process()
   total_time = 0.0
   total_bandwidth = 0
   cpu_times_start = process.cpu_times()
  
   latencies = []
   for _ in range(num_requests):
       n = random.randint(10, 100)  # Random n between 10 and 100 for each request
       start_time = time.perf_counter()
       result = calculator.fib(n)
       end_time = time.perf_counter()


       latency = end_time - start_time
       latencies.append(latency)
      
       total_time += latency
       total_bandwidth += get_size(result)
  
   cpu_times_end = process.cpu_times()
   cpu_time_used = (cpu_times_end.user - cpu_times_start.user) + (cpu_times_end.system - cpu_times_start.system)


   avg_latency = total_time / num_requests
   avg_bandwidth = total_bandwidth / num_requests


   print(f"Requests: {num_requests}")
   print(f"Average latency per request: {avg_latency * 1000:.3f} ms")
   print(f"Total execution time: {total_time:.3f} s")
   print(f"CPU time used: {cpu_time_used:.3f} s")
   print(f"Approximate average bandwidth consumption per response: {avg_bandwidth / 1024:.3f} KB")


def main():
   calculator = Pyro5.api.Proxy(uri)


   while True:
       print("\nChoose an option:")
       print("1. Send custom Fibonacci request")
       print("2. Benchmark with random n (10-100) for 100, 1000, 10000 requests")
       print("3. Exit")
       choice = input("Enter choice (1/2/3): ").strip()


       if choice == "1":
           n = input("Enter Fibonacci sequence length (positive integer): ").strip()
           if not n.isdigit() or int(n) <= 0:
               print("Please enter a valid positive integer.")
               continue
           n = int(n)
           start_time = time.perf_counter()
           result = calculator.fib(n)
           end_time = time.perf_counter()
           print(f"Fibonacci sequence up to {n}: {result}")
           print(f"Execution time: {(end_time - start_time)*1000:.3f} ms")


       elif choice == "2":
           print("Running benchmark for 100 requests...")
           benchmark_requests(calculator, 100)
           print("\nRunning benchmark for 1000 requests...")
           benchmark_requests(calculator, 1000)
           print("\nRunning benchmark for 10000 requests...")
           benchmark_requests(calculator, 10000)


       elif choice == "3":
           print("Exiting...")
           break
       else:
           print("Invalid choice. Please select 1, 2, or 3.")


if __name__ == "__main__":
   main()