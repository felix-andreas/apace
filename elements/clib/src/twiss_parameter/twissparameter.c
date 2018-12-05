#include <stdio.h>

// method 2 of klaus wille chapter 3.10
// 0 betax 1 betay 2 alphax 3 alphay 4 gammax 5 gammay 6 etax 7 d/ds etax

void twissparameter(int n, int size, double (*A)[size][size], double (*B0), double (*twissarray)[n])
{
    int pos;
    double (*m)[5];
    double tmp[8];
    for ( pos = 0; pos < n; pos ++ ) {
        m = A[pos];
        tmp[0] = m[0][0] * m[0][0] * B0[0] - 2. * m[0][0] * m[0][1] * B0[2] + m[0][1] * m[0][1] * B0[4];
        tmp[1] = m[2][2] * m[2][2] * B0[1] - 2. * m[2][2] * m[2][3] * B0[3] + m[2][3] * m[2][3] * B0[5];
        tmp[2] =-m[0][0] * m[1][0] * B0[0] + (m[0][0] * m[1][1] + m[0][1] * m[1][0]) * B0[2] - m[1][1] * m[0][1] * B0[4];
        tmp[3] =-m[2][2] * m[3][2] * B0[1] + (m[2][2] * m[3][3] + m[2][3] * m[3][2]) * B0[3] - m[3][3] * m[2][3] * B0[5];
        tmp[4] = m[1][0] * m[1][0] * B0[0] - 2. * m[1][1] * m[1][0] * B0[2] + m[1][1] * m[1][1] * B0[4];
        tmp[5] = m[3][2] * m[3][2] * B0[1] - 2. * m[3][3] * m[3][2] * B0[3] + m[3][3] * m[3][3] * B0[5];
        tmp[6] = m[0][0] * B0[6]  + m[0][1]* B0[7] + m[0][4];
        tmp[7] = m[1][0] * B0[6]  + m[1][1]* B0[7] + m[1][4];
        twissarray[] //hierhin kopieren balbal
    }
}
