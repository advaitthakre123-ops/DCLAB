import xmlrpc.client
import time
import statistics


proxy = xmlrpc.client.ServerProxy("http://localhost:8000/", allow_none=True)


FIB_POSITION = 25
TEST_RUNS = [100, 1000, 10000]


# Measure payload size
request_payload = xmlrpc.client.dumps(((FIB_POSITION,),))
response_payload = xmlrpc.client.dumps((proxy.get_fib(FIB_POSITION),))
PAYLOAD_SIZE_BYTES = len(request_payload) + len(response_payload)


print("--- Starting XML-RPC Performance Test ---")


for num_requests in TEST_RUNS:
   latencies = []
   print(f"\n--- Running for {num_requests} requests ---")


   cpu_start = time.process_time()
   total_start_time = time.perf_counter()


   for _ in range(num_requests):
       req_start_time = time.perf_counter()
       result = proxy.get_fib(FIB_POSITION)
       req_end_time = time.perf_counter()
       latencies.append((req_end_time - req_start_time) * 1000)


   total_end_time = time.perf_counter()
   cpu_end = time.process_time()
  
   total_time = total_end_time - total_start_time
   total_cpu_time = cpu_end - cpu_start


   print(f"Fibonacci Number at position (n count): {FIB_POSITION+1}")
   print(f"Final Fibonacci Result: {result}")
   print(f"Execution Time: {total_time:.4f} seconds")
   print(f"CPU Utilization Time: {total_cpu_time:.4f} seconds")
   print(f"Bandwidth per Request (Payload Size): {PAYLOAD_SIZE_BYTES} bytes")
   print(f"Requests Per Second (Throughput): {num_requests / total_time:.2f} RPS")
   print(f"Latency (ms) - Average: {statistics.mean(latencies):.4f}, StdDev: {statistics.stdev(latencies):.4f}")