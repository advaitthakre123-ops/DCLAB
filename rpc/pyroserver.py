import Pyro5.api


@Pyro5.api.expose
class FibonacciCalculator:
   def fib(self, n):
       if n <= 0:
           return []
       elif n == 1:
           return [0]
       fib_seq = [0, 1]
       for i in range(2, n):
           fib_seq.append(fib_seq[-1] + fib_seq[-2])
       return fib_seq


def main():
   daemon = Pyro5.api.Daemon()  # start Pyro daemon
   uri = daemon.register(FibonacciCalculator)
   print("Ready. Object uri =", uri)
   daemon.requestLoop()


if __name__ == "__main__":
   main()