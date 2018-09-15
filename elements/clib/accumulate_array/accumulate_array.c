#include <stdio.h>

void accumulate_array(int n, int size, double (*ina)[size][size], double (*outa)[size][size])
{
    int pos, i ,j ,k;
    /*for ( i = 0; i < size; i++ ) {
        for ( j = 0; j < size; j++ ) {
            outa[0][i][j] = ina[0][i][j];
        }
    }*/
    for ( pos = 0; pos < n; pos ++ ) {
        for ( i = 0; i < size; i++ ) {
            for ( j = 0; j < size; j++ ) {
                outa[pos + 1][i][j] = 0;
                for ( k = 0; k < size; k++ ) {
                    outa[pos + 1][i][j] += ina[pos][i][k] * outa[pos][k][j];
                }
            }
        }
    }
}

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