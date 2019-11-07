#include <stdio.h>

// method 2 of klaus wille chapter 3.10
// 0 betax 1 betay 2 alphax 3 alphay 4 gammax 5 gammay 6 etax 7 d/ds etax

void twiss_product_serial (int n, double (*matrix_array)[6][6], double *B0, double (*twiss_array)[n]) {
  for (int i = 0; i < 8; i++) {
    twiss_array[i][0] = B0[i];
  }

  for (int pos = 1; pos < n; pos++) {
    double(*m)[6] = matrix_array[pos - 1]; // matrix array has shape (6, 6, n - 1)

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
  }
}

// TODO: testen ob es schneller ist kontinuierlich in den speicher zu schreiben!
//    for ( pos = 0; pos < n; pos ++ ) {
//        m = A[pos];
//        tmp[0] = m[0][0] * m[0][0] * B0[0] - 2. * m[0][0] * m[0][1] * B0[2] + m[0][1] * m[0][1] * B0[4];
//        tmp[1] = m[2][2] * m[2][2] * B0[1] - 2. * m[2][2] * m[2][3] * B0[3] + m[2][3] * m[2][3] * B0[5];
//
//        tmp[2] =-m[0][0] * m[1][0] * B0[0] + (m[0][0] * m[1][1] + m[0][1] * m[1][0]) * B0[2] - m[1][1] * m[0][1] * B0[4];
//        tmp[3] =-m[2][2] * m[3][2] * B0[1] + (m[2][2] * m[3][3] + m[2][3] * m[3][2]) * B0[3] - m[3][3] * m[2][3] * B0[5];
//
//        tmp[4] = m[1][0] * m[1][0] * B0[0] - 2. * m[1][1] * m[1][0] * B0[2] + m[1][1] * m[1][1] * B0[4];
//        tmp[5] = m[3][2] * m[3][2] * B0[1] - 2. * m[3][3] * m[3][2] * B0[3] + m[3][3] * m[3][3] * B0[5];
//        tmp[6] = m[0][0] * B0[6]  + m[0][1]* B0[7] + m[0][4];
//        tmp[7] = m[1][0] * B0[6]  + m[1][1]* B0[7] + m[1][4];
//    }
