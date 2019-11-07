#include <omp.h>
#include <stdio.h>
#define DEBUG 0

void twiss_product_parallel (int n, double (*matrix_array)[6][6], double *B0, double (*twiss_array)[n]) {
  for (int i = 0; i < 8; i++) {
    twiss_array[i][0] = B0[i];
  }
#pragma omp parallel shared(twiss_array, B0, matrix_array)  // private(thread_id, n_loops)
  {
#if DEBUG
    int thread_id, n_loops = 0;
#endif

#pragma omp for schedule(static, 1000)
    for (int pos = 1; pos < n; pos++) {
        double(*m)[6] = matrix_array[pos - 1];

        // beta
        twiss_array[0][pos] = m[0][0] * m[0][0] * B0[0] - 2. * m[0][0] * m[0][1] * B0[2] + m[0][1] * m[0][1] * B0[4];
        twiss_array[1][pos] = m[2][2] * m[2][2] * B0[1] - 2. * m[2][2] * m[2][3] * B0[3] + m[2][3] * m[2][3] * B0[5];

        // alpha
        twiss_array[2][pos] = -m[0][0] * m[1][0] * B0[0] + (m[0][0] * m[1][1] + m[0][1] * m[1][0]) * B0[2] - m[1][1] * m[0][1] * B0[4];
        twiss_array[3][pos] = -m[2][2] * m[3][2] * B0[1] + (m[2][2] * m[3][3] + m[2][3] * m[3][2]) * B0[3] - m[3][3] * m[2][3] * B0[5];

        // gamma
        twiss_array[4][pos] = m[1][0] * m[1][0] * B0[0] - 2. * m[1][1] * m[1][0] * B0[2] + m[1][1] * m[1][1] * B0[4];
        twiss_array[5][pos] = m[3][2] * m[3][2] * B0[1] - 2. * m[3][3] * m[3][2] * B0[3] + m[3][3] * m[3][3] * B0[5];

        // eta_x
        twiss_array[6][pos] = m[0][0] * B0[6] + m[0][1] * B0[7] + m[0][5];
        twiss_array[7][pos] = m[1][0] * B0[6] + m[1][1] * B0[7] + m[1][5];

#if DEBUG
      ++n_loops;
#endif
    }

#if DEBUG
    thread_id = omp_get_thread_num();
    printf("Thread %d performed %d iterations of the loop.\n", thread_id,
           n_loops);
#endif
  }

#if DEBUG
  printf("\n m11 %f\n",m[1][1]);
  printf("\nbetax    %f\n", B0[0]);
  printf("betay    %f\n", B0[1]);
  printf("alphax   %f\n", B0[2]);
  printf("alphay   %f\n", B0[3]);
  printf("gammax   %f\n", B0[4]);
  printf("gammay   %f\n", B0[5]);
  printf("etax     %f\n", B0[6]);
  printf("ddseta   %f\n", B0[7]);
#endif
}
