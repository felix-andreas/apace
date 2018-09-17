#include <stdio.h>


void twissparameter(int n, int size, double (*A)[size][size], double (*B0), double (*twissarray)[n])
{
    int pos;
    double (*m)[5];
    for ( pos = 0; pos < n; pos ++ ) {
        m = A[pos];
        // method 2 of klaus wille chapter 3.10
        // 0 betax 1 betay 2 alphax 3 alphay 4 gammax 5 gammay 6 etax 7 d/ds etax
        twissarray[0][pos] = m[0][0] * m[0][0] * B0[0] - 2. * m[0][0] * m[0][1] * B0[2] + m[0][1] * m[0][1] * B0[4];
        twissarray[2][pos] =-m[0][0] * m[1][0] * B0[0] + (m[0][0] * m[1][1] + m[0][1] * m[1][0]) * B0[2] - m[1][1] * m[0][1] * B0[4];
        twissarray[4][pos] = m[1][0] * m[1][0] * B0[0] - 2. * m[1][1] * m[1][0] * B0[2] + m[1][1] * m[1][1] * B0[4];

        twissarray[1][pos] = m[2][2] * m[2][2] * B0[1] - 2. * m[2][2] * m[2][3] * B0[3] + m[2][3] * m[2][3] * B0[5];
        twissarray[3][pos] =-m[2][2] * m[3][2] * B0[1] + (m[2][2] * m[3][3] + m[2][3] * m[3][2]) * B0[3] - m[3][3] * m[2][3] * B0[5];
        twissarray[5][pos] = m[3][2] * m[3][2] * B0[1] - 2. * m[3][3] * m[3][2] * B0[3] + m[3][3] * m[3][3] * B0[5];
        twissarray[5][pos] = m[3][2] * m[3][2] * B0[1] - 2. * m[3][3] * m[3][2] * B0[3] + m[3][3] * m[3][3] * B0[5];

        twissarray[6][pos] = m[0][0] * B0[6]  + m[0][1]* B0[7] + m[0][4];
        twissarray[7][pos] = m[1][0] * B0[6]  + m[1][1]* B0[7] + m[1][4];
    }
    /*printf("\n m11 %f\n",m[1][1]);
    printf("\nbetax    %f\n", B0[0]);
    printf("betay    %f\n", B0[1]);
    printf("alphax   %f\n", B0[2]);
    printf("alphay   %f\n", B0[3]);
    printf("gammax   %f\n", B0[4]);
    printf("gammay   %f\n", B0[5]);
    printf("etax     %f\n", B0[6]);
    printf("ddseta   %f\n", B0[7]);*/
}
