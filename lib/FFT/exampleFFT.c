/*
This is a C Program to perform 2D FFT. A fast Fourier transform (FFT) is an algorithm to compute the discrete Fourier transform (DFT) and its inverse. Fourier analysis converts time (or space) to frequency and vice versa; an FFT rapidly computes such transformations by factorizing the DFT matrix into a product of sparse (mostly zero) factors.
Here is source code of the C Perform to a 2D FFT Inplace Given a Complex 2D Array. The C program is successfully compiled and run on a Linux system. The program output is also shown below.
*/

/*
    $ gcc exampleFFT.c
    $ ./a.out
    
    Enter the size: 
    2
    Enter the 2D elements 
    2 3
    4 2
    
    2.5 + 0.0 i
    5.5 + 0.0 i
    -0.5 + -1.8369701987210297E-16 i
    0.5 + -3.0616169978683826E-16 i
    2.5 + 0.0 i
    -0.5 + -3.6739403974420594E-16 i
    -0.5 + -1.8369701987210297E-16 i
    -1.5 + -1.8369701987210297E-16 i
*/

#include<stdio.h>
#include<math.h>
#define PI 3.14159265
int n;
 
int main(int argc, char **argv) {
    double realOut[n][n];
    double imagOut[n][n];
    double amplitudeOut[n][n];
 
    int height = n;
    int width = n;
    int yWave;
    int xWave;
    int ySpace;
    int xSpace;
    int i, j;
    double inputData[n][n];
 
    printf("Enter the size: ");
    scanf("%d", &n);
 
    printf("Enter the 2D elements ");
    for (i = 0; i < n; i++)
        for (j = 0; j < n; j++)
            scanf("%lf", &inputData[i][j]);
 
 
    // Two outer loops iterate on output data.
    for (yWave = 0; yWave < height; yWave++) {
        for (xWave = 0; xWave < width; xWave++) {
            // Two inner loops iterate on input data.
            for (ySpace = 0; ySpace < height; ySpace++) {
                for (xSpace = 0; xSpace < width; xSpace++) {
                    // Compute real, imag, and ampltude.
                    realOut[yWave][xWave] += (inputData[ySpace][xSpace] * cos(
                            2 * PI * ((1.0 * xWave * xSpace / width) + (1.0
                                    * yWave * ySpace / height)))) / sqrt(
                            width * height);
                    imagOut[yWave][xWave] -= (inputData[ySpace][xSpace] * sin(
                            2 * PI * ((1.0 * xWave * xSpace / width) + (1.0
                                    * yWave * ySpace / height)))) / sqrt(
                            width * height);
                    amplitudeOut[yWave][xWave] = sqrt(
                            realOut[yWave][xWave] * realOut[yWave][xWave]
                                    + imagOut[yWave][xWave]
                                            * imagOut[yWave][xWave]);
                }
                printf(" %e + %e i (%e)\n", realOut[yWave][xWave],
                        imagOut[yWave][xWave], amplitudeOut[yWave][xWave]);
            }
        }
    }
    return 0;
}
 
