#define DEBUG 0

#if DEBUG
#include <stdio.h>
#endif

// perform accumulated matrix product on array of matrices
void matrix_product_accumulated(
    int n,
    int start_idx,
    double (*matrices)[6][6],
    double (*accumulated)[6][6]
) {
    for (int i = 0; i < 6; i++) {
        for (int j = 0; j < 6; j++) {
            accumulated[start_idx][i][j] = matrices[start_idx][i][j];
        }
    }

    for (int pos = start_idx + 1, pos_1 = start_idx;; pos++) {
        if (pos >= n) {
            pos = 0;
        }

        if (pos == start_idx) {
            break;
        }

        for (int i = 0; i < 6; i++) {
            for (int j = 0; j < 6; j++) {
                accumulated[pos][i][j] = 0.0;
                for (int k = 0; k < 6; k++) {
                    accumulated[pos][i][j] += matrices[pos][i][k] * accumulated[pos_1][k][j];
                }
            }
        }

        pos_1 = pos;
    }
}

// perform matrix product on array of matrices for given ranges
void matrix_product_ranges(
    int n_ranges,
    int n_matrices,
    int (*ranges)[2],
    double (*matrices)[6][6],
    double (*accumulated)[6][6]
) {
    for (int l = 0; l < n_ranges; l++) {
        int start = ranges[l][0];
        int end = ranges[l][1];

        for (int i = 0; i < 6; i++) {
            for (int j = 0; j < 6; j++) {
                accumulated[l][i][j] = matrices[start][i][j];
            }
        }

        if (end < start) {
            end += n_matrices;
        }

        for (int m = start + 1; m < end; m++) {
            int pos = m < n_matrices ? m : m - n_matrices;
            double tmp[6][6] = {{0}};
            for (int i = 0; i < 6; i++) {
                for (int j = 0; j < 6; j++) {
                    for (int k = 0; k < 6; k++) {
                        tmp[i][j] += matrices[pos][i][k] * accumulated[l][k][j];
                    }
                }
            }

            for (int i = 0; i < 6; i++) {
                for (int j = 0; j < 6; j++) {
                    accumulated[l][i][j] = tmp[i][j];
                }
            }
        }
    }
}
