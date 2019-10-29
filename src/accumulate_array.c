#include <stdio.h>

void accumulate_array(int n, int size, double (*input_array)[size][size], double (*accumulated_array)[size][size]) {
  for (int i = 0; i < size; i++) {
    for (int j = 0; j < size; j++) {
      accumulated_array[0][i][j] = input_array[0][i][j];
    }
  }
  
  for (int pos = 1; pos < n; pos++) {
    int pos_1 = pos - 1;
    for (int i = 0; i < size; i++) {
      for (int j = 0; j < size; j++) {
        accumulated_array[pos][i][j] = 0.0;
        for (int k = 0; k < size; k++) {
          accumulated_array[pos][i][j] += input_array[pos][i][k] * accumulated_array[pos_1][k][j];
        }
      }
    }
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