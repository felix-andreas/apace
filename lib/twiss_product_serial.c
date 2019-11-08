#define DEBUG 0

#if DEBUG
#include <stdio.h>
#endif

// Method 2 from Klaus Wille chapter 3.10
// 0 beta_x 1 beta_y 2 alpha_x 3 alpha_y 4 gamma_x 5 gamma_y 6 eta_x 7 d/ds eta_x
void twiss_product_serial (
        int n,
        int from_idx,
        double (*matrix_array)[6][6], // shape (6, 6, n - 1)
        double *B0,
        double (*twiss_array)[n] // shape (8, n)
) {
    for (int i = 0; i < 8; i++) {
        twiss_array[i][from_idx] = B0[i];
    }

    for (int i = 1 + from_idx; i < n + from_idx; i++) {
        int pos = i < n ? i : i - n;
        int pos_1 = (pos != 0) ? pos - 1 : n - 2;
        double(*m)[6] = matrix_array[pos_1];

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

// TODO: Check if it is faster to write to memory continuously by transposing twiss_array
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
