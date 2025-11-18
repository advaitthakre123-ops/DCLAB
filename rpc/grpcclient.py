import grpc
import fibonacci_pb2
import fibonacci_pb2_grpc
import time
import psutil
import sys


def measure_bandwidth(request, response):
   """Estimate bandwidth per request by serialized message size (in bytes)."""
   request_size = sys.getsizeof(request.SerializeToString())
   response_size = sys.getsizeof(response.SerializeToString())
   return request_size + response_size  # total bytes transferred


def run(n, num_requests):
   channel = grpc.insecure_channel('localhost:50051')
   stub = fibonacci_pb2_grpc.FibonacciStub(channel)


   # Get CPU time before starting requests
   cpu_times_before = psutil.cpu_times()


   start_time = time.time()
   total_bandwidth = 0
   latencies = []


   for _ in range(num_requests):
       req_start = time.time()
       response = stub.GetSequence(fibonacci_pb2.FibonacciRequest(n=n))
       req_end = time.time()


       latencies.append(req_end - req_start)


       # Measure bandwidth per request
       total_bandwidth += measure_bandwidth(
           fibonacci_pb2.FibonacciRequest(n=n), response
       )


   end_time = time.time()
   cpu_times_after = psutil.cpu_times()


   # Calculate actual CPU time used during the request period (user + system)
   cpu_time_used = (
       (cpu_times_after.user - cpu_times_before.user) +
       (cpu_times_after.system - cpu_times_before.system)
   )


   # Compute metrics
   total_time = end_time - start_time
   avg_latency = sum(latencies) / len(latencies)
   avg_bandwidth = total_bandwidth / num_requests  # bytes/request


   # Output results
   print(f"\nFor n = {n} and {num_requests} requests:")
   print(f"Execution Time: {total_time:.4f} seconds")
   print(f"Average Latency per request: {avg_latency * 1000:.4f} ms")
   print(f"CPU Utilization Time: {cpu_time_used:.4f} seconds")
   print(f"Average Bandwidth per request: {avg_bandwidth:.1f} bytes")


   # Print nth Fibonacci number (assuming sequence includes n items)
   if response.sequence:
       print(f"Fibonacci number at position n: {response.sequence[-1]}")
   else:
       print("Received empty Fibonacci sequence")


if __name__ == '__main__':
   test_ns = [26]  # Fibonacci up to the 26th position
   test_requests = [100, 1000, 10000]


   for n in test_ns:
       for req_count in test_requests:
           run(n, req_count)