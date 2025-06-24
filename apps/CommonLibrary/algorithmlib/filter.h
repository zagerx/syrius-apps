/**
 * @file filter.h
 * @brief Header for digital filter implementations
 */

 #ifndef __FILTER_H
 #define __FILTER_H
 
 #include <stdint.h>
 
 /**
  * struct lowfilter_t - Low-pass filter structure
  * @freq: Filter frequency coefficient
  * @pre_val: Previous filtered value
  */
 typedef struct {
     float freq;
     float pre_val;
 } lowfilter_t;
 
 void lowfilter_init(lowfilter_t *pfilter, float freq);
 float lowfilter_cale(lowfilter_t *pfilter, float val);
 
 /**
  * struct KalmanFilter - Kalman filter structure
  * @x: State estimate
  * @P: Estimate error variance
  * @Q: Process noise variance
  * @R: Measurement noise variance
  */
 typedef struct {
     float x;
     float P;
     float Q;
     float R;
 } KalmanFilter;
 
 void kalman_filter_init(KalmanFilter *kf, float initial_x, float initial_P,
                        float process_noise, float measurement_noise);
 void kalman_filter_step(KalmanFilter *kf, float measurement);
 
 /**
  * struct moving_avg_t - Moving average filter structure
  * @buffer: Circular buffer for samples
  * @size: Window size
  * @index: Current buffer position
  * @sum: Running sum of samples
  */
 typedef struct {
     int16_t *buffer;
     uint16_t size;
     uint16_t index;
     int32_t sum;
 } moving_avg_t;
 
 void moving_avg_init(moving_avg_t *filter, int16_t *buf, uint16_t size);
 int16_t moving_avg_update(moving_avg_t *filter, int16_t new_val);
 void moving_avg_reset(moving_avg_t *filter);
 
 #endif /* __FILTER_H */