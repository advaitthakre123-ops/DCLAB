import grpc
from concurrent import futures
import fibonacci_pb2
import fibonacci_pb2_grpc


class FibonacciServicer(fibonacci_pb2_grpc.FibonacciServicer):
   def GetSequence(self, request, context):
       n = request.n
       sequence = []
       a, b = 0, 1
       for _ in range(n):  # generate first n Fibonacci numbers
           sequence.append(a)
           a, b = b, a + b


       return fibonacci_pb2.FibonacciResponse(sequence=sequence)




def serve():
   server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
   fibonacci_pb2_grpc.add_FibonacciServicer_to_server(FibonacciServicer(), server)
   server.add_insecure_port('[::]:50051')
   print("gRPC Server running on port 50051...")
   server.start()
   server.wait_for_termination()


if __name__ == '__main__':
   serve()