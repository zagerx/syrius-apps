/**
 * @file filter.c
 * @brief Implementation of various digital filters (low-pass, Kalman, moving average)
 */

 #include "filter.h"

 /**
  * lowfilter_init - Initialize a low-pass filter instance
  * @pfilter: Pointer to filter structure
  * @freq: Cutoff frequency (inverse time constant)
  */
 void lowfilter_init(lowfilter_t *pfilter, float freq)
 {
     if (!pfilter)
         return;
     
     pfilter->freq = 1.0f/freq;
     pfilter->pre_val = 0.0f;
 }
 
 /**
  * lowfilter_cale - Calculate filtered output (single step)
  * @pfilter: Pointer to filter structure
  * @val: New input value
  * Return: Filtered output value
  */
 float lowfilter_cale(lowfilter_t *pfilter, float val)
 {
     if (!pfilter)
         return val;
     
     float curval = pfilter->freq * val + (1.0f-pfilter->freq) * pfilter->pre_val;
     pfilter->pre_val = curval;
     return curval;
 }
 
 /**
  * kalman_filter_init - Initialize Kalman filter instance
  * @kf: Pointer to Kalman filter structure
  * @initial_x: Initial state estimate
  * @initial_P: Initial error variance
  * @process_noise: Process noise variance (Q)
  * @measurement_noise: Measurement noise variance (R)
  */
 void kalman_filter_init(KalmanFilter *kf, float initial_x, float initial_P,
                        float process_noise, float measurement_noise)
 {
     kf->x = initial_x;
     kf->P = initial_P;
     kf->Q = process_noise;
     kf->R = measurement_noise;
 }
 
 /**
  * kalman_filter_step - Perform one Kalman filter update step
  * @kf: Pointer to Kalman filter structure
  * @measurement: New measurement value
  */
 void kalman_filter_step(KalmanFilter *kf, float measurement) 
 {
     /* Prediction step */
     kf->P += kf->Q;
     
     /* Update step */
     float K = kf->P / (kf->P + kf->R); /* Kalman gain */
     kf->x += K * (measurement - kf->x);
     kf->P *= (1 - K);
 }
 
 /**
  * moving_avg_init - Initialize moving average filter
  * @filter: Pointer to filter structure
  * @buf: Preallocated buffer for storing samples
  * @size: Window size (number of samples)
  */
 void moving_avg_init(moving_avg_t *filter, int16_t *buf, uint16_t size)
 {
    //  filter->buffer = buf;
    //  filter->size = size;
     filter->index = 0;
     filter->sum = 0;
     
     /* Zero out buffer */
     for (uint16_t i = 0; i < size; i++)
         filter->buffer[i] = 0;
 }
 
 /**
  * moving_avg_update - Update filter with new value and return output
  * @filter: Pointer to filter structure
  * @new_val: New input value
  * Return: Filtered output value
  */
 int16_t moving_avg_update(moving_avg_t *filter, int16_t new_val)
 {
     /* Update running sum by replacing oldest sample */
     filter->sum -= filter->buffer[filter->index];
     filter->sum += new_val;
     filter->buffer[filter->index] = new_val;
     
     /* Update circular buffer index */
     filter->index = (filter->index + 1) % filter->size;
     
     return filter->sum / filter->size;
 }
 
 /**
  * moving_avg_reset - Reset filter state (clear buffer and sum)
  * @filter: Pointer to filter structure
  */
 void moving_avg_reset(moving_avg_t *filter)
 {
     filter->index = 0;
     filter->sum = 0;
     
     for (uint16_t i = 0; i < filter->size; i++)
         filter->buffer[i] = 0;
 }