void twiss_product(int n, int size, double (*A)[size][size], double (*B0vec)[size], double (*out)[size][size]) {
  int pos, i, j, k, l;
  double B[5][5] = {
        {1., 1., 1., 1., 1.},
        {1., 5., 6., 1., 1.},
        {1., 8., 9., 1., 1.},
        {1., 5., 6., 1., 1.},
        {1., 8., 9., 1., 1.},
  }
  for (pos = 0; pos < n; pos++) {
    for (i = 0; i < size; i++) {
      for (j = 0; j < size; j++) {
        out[pos][i][j] = 0.0;
        for (k = 0; k < size; k++) {
          for (l = 0; l < size; l++) {
            out[pos][i][j] += A[pos][i][k] * B[k][l] * A[pos][j][l];
          }
        }
      }
    }
  }
}
