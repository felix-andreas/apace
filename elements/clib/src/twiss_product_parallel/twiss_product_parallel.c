#include <stdio.h>
#include <omp.h>

void twiss_product_parallel(int n, int size, double (*A)[size][size], double (*B)[size], double (*out)[size][size])
{
  int pos, i ,j ,k, l;
  //int thread_id, nloops;

#pragma omp parallel //private(thread_id, nloops)
  {
    //nloops = 0;

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
    //++nloops;
    }

    //thread_id = omp_get_thread_num();

    //printf("Thread %d performed %d iterations of the loop.\n",
    //thread_id, nloops );
    }

}
/*
int main(void)
{
    double a[][5][5] = {
    {
        {1., 1., 1., 1., 1.},
        {1., 5., 6., 1., 1.},
        {1., 8., 9., 1., 1.},
        {1., 5., 6., 1., 1.},
        {1., 8., 9., 1., 1.},
    },
    {
        {1., 1., 1., 1., 1.},
        {1., 5., 6., 1., 1.},
        {1., 8., 9., 1., 1.},
        {1., 5., 6., 1., 1.},
        {1., 8., 9., 1., 1.},
    }
    };
    double b[][5][5] = {
    {
        {1., 1., 1., 1., 1.},
        {1., 5., 6., 1., 1.},
        {1., 8., 9., 1., 1.},
        {1., 5., 6., 1., 1.},
        {1., 8., 9., 1., 1.},
    },
    {
        {1., 1., 1., 1., 1.},
        {1., 5., 6., 1., 1.},
        {1., 8., 9., 1., 1.},
        {1., 5., 6., 1., 1.},
        {1., 8., 9., 1., 1.},
    }
    };

    accumulate_array(2, 5, a, b);
    return 0;
}
*/