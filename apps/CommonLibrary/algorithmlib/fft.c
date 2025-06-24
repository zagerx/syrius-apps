/*
 * Fast Fourier Transform (FFT) Implementation
 *
 * Copyright (C) 2023 DeepSeek Company
 * SPDX-License-Identifier: Apache-2.0
 */

#include "fft.h"

/**
 * fft_getdata - Collect data samples for FFT processing
 * @fft: FFT context structure
 * @data: Input data array
 * @datalen: Number of samples to collect
 *
 * Buffers input data until FFT_BUF_SIZE is reached, then sets processing flag.
 */
void fft_getdata(struct fft *fft, float *data, uint8_t datalen)
{
    if (!fft || !data || datalen == 0) {
        return;
    }

    if (!fft->wr_flag) {
        for (int16_t i = 0; i < datalen; i++) {
            fft->input[fft->wr_index] = *data++;
            
            if (++fft->wr_index >= FFT_BUF_SIZE) {
                fft->wr_index = 0;
                fft->wr_flag = 1;
                break;  /* Buffer full, stop collecting */
            }
        }
    }
}

/**
 * fft_process - Perform FFT on collected data
 * @fft: FFT context structure
 * @out: Output buffer for spectrum results
 *
 * Processes buffered data using ARM DSP library when buffer is full.
 * Resets processing flag when complete.
 */
void fft_process(struct fft *fft, float *out)
{
    if (!fft || !out || !fft->wr_flag) {
        return;
    }

    /* ARM DSP FFT processing */
    arm_rfft_fast_instance_f32 fft_instance;
    arm_rfft_fast_init_f32(&fft_instance, FFT_BUF_SIZE);
    arm_rfft_fast_f32(&fft_instance, fft->input, fft->output, 0);
    
    /* Copy to output buffer if provided */
    if (out) {
        memcpy(out, fft->output, FFT_BUF_SIZE * sizeof(float));
    }

    fft->wr_flag = 0;  /* Ready for new data */
}