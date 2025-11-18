#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>


static void fill_random(int *M, int rows, int cols) {
   for (int i = 0; i < rows * cols; ++i) M[i] = rand() % 10;
}


static void print_matrix(const char *name, const int *M, int rows, int cols) {
   printf("%s (%dx%d):\n", name, rows, cols);
   for (int i = 0; i < rows; ++i) {
       for (int j = 0; j < cols; ++j) printf("%4d ", M[i*cols + j]);
       printf("\n");
   }
}


int main(int argc, char **argv) {
   MPI_Init(&argc, &argv);
   int rank, size;
   MPI_Comm_rank(MPI_COMM_WORLD, &rank);
   MPI_Comm_size(MPI_COMM_WORLD, &size);
   int N = 4;
   if (argc >= 2) N = atoi(argv[1]);
   if (N <= 0) N = 4;
   int *A = NULL, *B = NULL, *C = NULL;
   if (rank == 0) {
       A = (int *)malloc(N * N * sizeof(int));
       B = (int *)malloc(N * N * sizeof(int));
       C = (int *)malloc(N * N * sizeof(int));
       srand(42);
       fill_random(A, N, N);
       fill_random(B, N, N);
   } else {
       B = (int *)malloc(N * N * sizeof(int));
   }
   MPI_Bcast(&N, 1, MPI_INT, 0, MPI_COMM_WORLD);
   int base = N / size;
   int rem  = N % size;
   int *sendcountsA = (int *)malloc(size * sizeof(int));
   int *displsA     = (int *)malloc(size * sizeof(int));
   int *recvcountsC = (int *)malloc(size * sizeof(int));
   int *displsC     = (int *)malloc(size * sizeof(int));
   int offsetA = 0, offsetC = 0;
   for (int p = 0; p < size; ++p) {
       int rows_p = base + (p < rem ? 1 : 0);
       sendcountsA[p] = rows_p * N;  
       displsA[p]     = offsetA;
       recvcountsC[p] = rows_p * N;   
       displsC[p]     = offsetC;
       offsetA += rows_p * N;
       offsetC += rows_p * N;
   }
   int my_rows = base + (rank < rem ? 1 : 0);
   int *localA = (my_rows > 0) ? (int *)malloc(my_rows * N * sizeof(int)) : NULL;
   int *localC = (my_rows > 0) ? (int *)malloc(my_rows * N * sizeof(int)) : NULL;
   MPI_Barrier(MPI_COMM_WORLD);
   double t0 = MPI_Wtime();
   MPI_Bcast(B, N * N, MPI_INT, 0, MPI_COMM_WORLD);
   MPI_Scatterv(A, sendcountsA, displsA, MPI_INT,
                localA, (my_rows > 0 ? my_rows * N : 0), MPI_INT,
                0, MPI_COMM_WORLD);
   for (int i = 0; i < my_rows; ++i) {
       for (int j = 0; j < N; ++j) {
           int sum = 0;
           for (int k = 0; k < N; ++k) {
               sum += localA[i * N + k] * B[k * N + j];
           }
           localC[i * N + j] = sum;
       }
   }
   if (rank != 0) {
       MPI_Gatherv(localC, my_rows * N, MPI_INT, NULL, NULL, NULL, MPI_INT, 0, MPI_COMM_WORLD);
   } else {
       MPI_Gatherv(localC, my_rows * N, MPI_INT, C, recvcountsC, displsC, MPI_INT, 0, MPI_COMM_WORLD);
   }
   MPI_Barrier(MPI_COMM_WORLD);
   double t1 = MPI_Wtime();
   double elapsed = t1 - t0;
   if (rank == 0) {
       if (N <= 8) {
           print_matrix("A", A, N, N);
           print_matrix("B", B, N, N);
           print_matrix("C = A x B", C, N, N);
       }
       printf("\n--- Parallel Run Info ---\n");
       printf("Matrix size: %d x %d\n", N, N);
       printf("Processes  : %d\n", size);
       printf("Elapsed    : %.6f seconds\n", elapsed);
   }
   free(sendcountsA); free(displsA); free(recvcountsC); free(displsC);
   if (localA) free(localA);
   if (localC) free(localC);
   if (rank == 0) { free(A); free(B); free(C); }
   else { free(B); }
   MPI_Finalize();
   return 0;
}

//mpicc -o matmul matmul.c
//mpirun -np 4 ./matmul 