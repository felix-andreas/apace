#include <stdio.h>
#include <omp.h>
#define DEBUG 0

void twiss_product_parallel(int n, int size, double (*A)[size][size], double (*B)[size], double (*out)[size][size])
{
    #if DEBUG
    #endif

    #pragma omp parallel //private(thread_id, nloops)
    {
        #if DEBUG
        int thread_id, nloops=0;
        #endif

        int pos, i ,j ,k, l;
        #pragma omp for
        for (pos=0; pos<n; ++pos)
        {
            for ( i = 0; i < size; i++ ) {
                for ( j = 0; j < size; j++ ) {
                    out[pos][i][j] = 0.0;
                    for ( k = 0; k < size; k++ ) {
                        for ( l = 0; l < size; l++ ) {
                            out[pos][i][j] += A[pos][i][k] * B[k][l] * A[pos][j][l];
                        }
                    }
                }
            }
            #if DEBUG
            ++nloops;
            #endif
    }

    #if DEBUG
    thread_id = omp_get_thread_num();
    printf("Thread %d performed %d iterations of the loop.\n", thread_id, nloops);
    #endif
    }

}