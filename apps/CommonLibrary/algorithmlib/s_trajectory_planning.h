/*
 * 轨迹规划算法头文件
 * 包含S型和线性轨迹规划接口定义
 * 
 * Copyright (c) 2023 DeepSeek Company
 * SPDX-License-Identifier: Apache-2.0
 */

#ifndef S_TRAJECTORY_PLANNING_H
#define S_TRAJECTORY_PLANNING_H

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    TRAJ_ACTOR_STATE_START = 0,
    TRAJ_ACTOR_STATE_T1,
    TRAJ_ACTOR_STATE_T2,
    TRAJ_ACTOR_STATE_T3,
    TRAJ_ACTOR_STATE_END,
    TRAJ_ACTOR_STATE_IDLE,
} trajectory_actor_state_t;

/* S型轨迹规划结构体 */
typedef struct {
    uint16_t tau;           /* 时间参数 */
    uint16_t Ts[4];         /* 各阶段时间分配 */
    trajectory_actor_state_t actor_state ; /* 执行状态 */
    float direction;
    float elapsed_time;
    float V[4];             /* 各阶段结束速度 V[0]代表初始时刻速度 V[1]代表第一阶段结束的速度*/
    float cur_output;       /* 当前输出值 */
    float last_target;      /* 上次目标值 */
    float max_acc;          /* 最大加速度 */
    float max_jerk;
    float acc;
    float jerk;
    float min_acc;
    float min_jerk;
} s_in_t;

/* API接口 */
void s_type_interpolation_init(void *object, float a_max,float Ja_max, float a_min,float Ja_min);
int16_t s_velocity_planning(s_in_t* pthis,float new_targe);
float s_velocity_actory(s_in_t *pthis);

#endif /* TRAJECTORY_PLANNING_H */