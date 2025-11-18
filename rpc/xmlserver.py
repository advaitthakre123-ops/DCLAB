from xmlrpc.server import SimpleXMLRPCServer


def get_fib_number(n):
   a, b = 0, 1
   for _ in range(n - 1):
       a, b = b, a + b
   return b


server = SimpleXMLRPCServer(("localhost", 8000), logRequests=False)
print("XML-RPC server listening on port 8000...")
server.register_function(get_fib_number, "get_fib")
server.serve_forever()