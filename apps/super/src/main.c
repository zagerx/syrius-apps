/*
 * Copyright (c) 2016 Intel Corporation
 *
 * SPDX-License-Identifier: Apache-2.0
 */

 #include "zephyr/device.h"
 #include <stdio.h>
 #include <sys/types.h>
 #include <zephyr/kernel.h>
 #include <zephyr/drivers/gpio.h>
 #include <zephyr/logging/log.h>
 #include <zephyr/drivers/can.h>
 #include <lib/foc/foc.h>
 
 LOG_MODULE_REGISTER(main, LOG_LEVEL_DBG);
 
 /* 1000 msec = 1 sec */
 #define SLEEP_TIME_MS   1
 
 extern void creat_motor_thread(const struct device *dev);
 extern void creat_canard_thread(void* p1);
 
 int main(void)
 {
    const struct device *motor0 = DEVICE_DT_GET(DT_NODELABEL(motor0));
     creat_canard_thread((void *)motor0); 
     creat_motor_thread(NULL);
     while (1) {
         k_msleep(1000);
     }
     return 0;
 }
 