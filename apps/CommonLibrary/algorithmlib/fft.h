/*
 * Fast Fourier Transform (FFT) Implementation
 *
 * Copyright (C) 2023 DeepSeek Company
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef _FFT_H
#define _FFT_H

#include "arm_math.h"

#define FFT_BUF_SIZE 1024  /* Size of FFT input/output buffers */

/**
 * struct fft - FFT processing context
 * @wr_index: Write index for input buffer
 * @wr_flag: Flag indicating buffer ready for processing
 * @input: Input data buffer
 * @output: Output spectrum buffer
 */
struct fft {
    int16_t wr_index;
    int8_t wr_flag;
    float input[FFT_BUF_SIZE];
    float output[FFT_BUF_SIZE];
};

/* Public API */
void fft_getdata(struct fft *fft, float *data, uint8_t datalen);
void fft_process(struct fft *fft, float *out);

#endif /* _FFT_H */