#define DEBUG 0

#if DEBUG
#include <stdio.h>
#endif

void accumulate_array(
        int n,
        int from_idx,
        double (*input_array)[6][6],
        double (*accumulated_array)[6][6]
) {
    for (int i = 0; i < 6; i++) {
        for (int j = 0; j < 6; j++) {
            accumulated_array[from_idx][i][j] = input_array[from_idx][i][j];
        }
    }

    for (int pos = from_idx + 1, pos_1 = from_idx;; pos++) {
        if (pos >= n) {
            pos = 0;
        }

        if (pos == from_idx){
            break;
        }

        for (int i = 0; i < 6; i++) {
            for (int j = 0; j < 6; j++) {
                accumulated_array[pos][i][j] = 0.0;
                for (int k = 0; k < 6; k++) {
                    accumulated_array[pos][i][j] += input_array[pos][i][k] * accumulated_array[pos_1][k][j];
                }
            }
        }

        pos_1 = pos;
    }
}


void accumulate_array_partial(
        int n,
        int (*ranges)[2],
        double (*input_array)[6][6],
        double (*accumulated_array)[6][6]
) {
    for (int l = 0; l < n; l++) {
        int start = ranges[l][0];
        int end = ranges[l][1];
        for (int i = 0; i < 6; i++) {
            for (int j = 0; j < 6; j++) {
            accumulated_array[l][i][j] = input_array[start][i][j];
            }
        }

        for (int pos = start + 1; pos < end; pos++) {
            for (int i = 0; i < 6; i++) {
                for (int j = 0; j < 6; j++) {
                    for (int k = 0; k < 6; k++) {
                        accumulated_array[l][i][j] += input_array[pos][i][k] * accumulated_array[l][k][j];
                    }
                }
            }
        }
    }
}

