#include "s_posi_planning.h"
#include <string.h>

#define EPSILON 1e-6f
#define MAX_ITERATIONS 1000

// 计算S曲线参数 (对应Matlab的SCurvePara函数)
static void calculate_scurve_params(SCurveParams *params, float Tf, float v, float a) {
    float T[7] = {0};
    float J = 0;
    float V = v;
    float A = a;
    float Tf1 = Tf;
    
    for(int i = 0; i < MAX_ITERATIONS; i++) {
        // 计算加加速度J
        J = (A * A * V) / (Tf1 * V * A - V * V - A);
        
        // 计算各时间段
        T[0] = A / J;                           // T1
        T[1] = V / A - A / J;                   // T2
        T[2] = T[0];                            // T3
        T[3] = Tf1 - 2 * A / J - 2 * V / A;     // T4
        T[4] = T[2];                            // T5
        T[5] = T[1];                            // T6
        T[6] = T[0];                            // T7
        
        // 检查参数有效性
        if(T[1] < -EPSILON) {
            // T2 < 0, 调整加速度
            A = sqrtf(V * J);
        } else if(T[3] < -EPSILON) {
            // T4 < 0, 调整速度
            V = Tf1 * A / 2 - A * A / J;
        } else if(J < -EPSILON) {
            // J < 0, 调整总时间
            Tf1 = (V * V + A) / (V * A) + 0.1f;
        } else {
            // 参数有效，保存结果
            params->J = J;
            params->V = V;
            params->A = A;
            params->Tf = Tf1;
            memcpy(params->T, T, sizeof(params->T));
            return;
        }
    }
    
    // 达到最大迭代次数仍未收敛，使用最后一次计算结果
    params->J = J;
    params->V = V;
    params->A = A;
    params->Tf = Tf1;
    memcpy(params->T, T, sizeof(params->T));
}

// 计算S曲线位置 (对应Matlab的SCurveScaling函数)
static float calculate_scurve_position(float t, const SCurveParams *params) {
    const float *T = params->T;
    const float V = params->V;
    const float A = params->A;
    const float J = params->J;
    const float Tf = params->Tf;
    
    float s = 0.0f;
    float dt = 0.0f;
    
    if (t >= 0 && t <= T[0]) {
        // T1: 加加速段
        s = 1.0f/6.0f * J * t * t * t;
    } else if (t > T[0] && t <= T[0] + T[1]) {
        // T2: 匀加速段
        dt = t - T[0];
        s = 0.5f * A * dt * dt 
            + (A * A)/(2.0f * J) * dt 
            + (A * A * A)/(6.0f * J * J);
    } else if (t > T[0] + T[1] && t <= T[0] + T[1] + T[2]) {
        // T3: 减加速段
        dt = t - T[0] - T[1];
        s = -1.0f/6.0f * J * dt * dt * dt 
            + 0.5f * A * dt * dt 
            + (A * T[1] + (A * A)/(2.0f * J)) * dt 
            + 0.5f * A * T[1] * T[1] 
            + (A * A)/(2.0f * J) * T[1] 
            + (A * A * A)/(6.0f * J * J);
    } else if (t > T[0] + T[1] + T[2] && t <= T[0] + T[1] + T[2] + T[3]) {
        // T4: 匀速段
        dt = t - T[0] - T[1] - T[2];
        s = V * dt 
            + (-1.0f/6.0f * J * T[2] * T[2] * T[2]) 
            + 0.5f * A * T[2] * T[2] 
            + (A * T[1] + (A * A)/(2.0f * J)) * T[2] 
            + 0.5f * A * T[1] * T[1] 
            + (A * A)/(2.0f * J) * T[1] 
            + (A * A * A)/(6.0f * J * J);
    } else if (t > T[0] + T[1] + T[2] + T[3] && t <= T[0] + T[1] + T[2] + T[3] + T[4]) {
        // T5: 加减速段
        float t_temp = Tf - t; 
        dt = t_temp - T[0] - T[1];
        s = -1.0f/6.0f * J * dt * dt * dt 
            + 0.5f * A * dt * dt 
            + (A * T[1] + (A * A)/(2.0f * J)) * dt 
            + 0.5f * A * T[1] * T[1] 
            + (A * A)/(2.0f * J) * T[1] 
            + (A * A * A)/(6.0f * J * J);
        s = 1.0f - s;
    } else if (t > T[0] + T[1] + T[2] + T[3] + T[4] && t <= T[0] + T[1] + T[2] + T[3] + T[4] + T[5]) {
        // T6: 匀减速段
        float t_temp = Tf - t; 
        dt = t_temp - T[0];
        s = 0.5f * A * dt * dt 
            + (A * A)/(2.0f * J) * dt 
            + (A * A * A)/(6.0f * J * J);
        s = 1.0f - s;
    } else if (t > T[0] + T[1] + T[2] + T[3] + T[4] + T[5] && t <= Tf + EPSILON) {
        // T7: 减减速段
        float t_temp = Tf - t; 
        s = 1.0f/6.0f * J * t_temp * t_temp * t_temp;
        s = 1.0f - s;
    }
    
    return s;
}

/**
 * @brief 初始化位置规划器
 * @param planner 规划器实例
 * @param max_vel 最大速度
 * @param max_acc 最大加速度
 * @param max_jerk 最大加加速度
 */
void s_pos_planner_init(SPosPlanner *planner, float max_vel, float max_acc, float max_jerk) {
    memset(planner, 0, sizeof(SPosPlanner));
    planner->max_vel = fabsf(max_vel);
    planner->max_acc = fabsf(max_acc);
    planner->max_jerk = fabsf(max_jerk);
    planner->state = POS_TRAJ_IDLE;
}

/**
 * @brief 执行位置规划
 * @param planner 规划器实例
 * @param start_pos 起始位置
 * @param target_pos 目标位置
 * @param total_time 总时间
 * @return 1: 成功, 0: 失败
 */
int s_pos_planning(SPosPlanner *planner, float start_pos, float target_pos, float total_time) {
    // 检查参数有效性
    if (total_time <= 0) {
        return 0;
    }
    
    // 计算总位移
    float total_dis = target_pos - start_pos;
    if (fabsf(total_dis) < EPSILON) {
        return 0;
    }
    
    // 归一化参数 (与Matlab一致)
    float v = planner->max_vel / fabsf(total_dis);
    float a = planner->max_acc / fabsf(total_dis);
    
    // 计算S曲线参数
    calculate_scurve_params(&planner->params, total_time, v, a);
    
    // 转换为毫秒时间
    for (int i = 0; i < 7; i++) {
        planner->Ts[i] = (uint16_t)(planner->params.T[i] * 1000.0f);
    }
    
    // 设置规划器状态
    planner->start_pos = start_pos;
    planner->target_pos = target_pos;
    planner->total_dis = total_dis;
    planner->current_pos = start_pos;
    planner->current_vel = 0.0f;
    planner->current_acc = 0.0f;
    planner->current_jerk = 0.0f;
    planner->elapsed_time = 0.0f;
    planner->tau = 0;
    planner->state = POS_TRAJ_ACCEL_UP;
    
    return 1;
}

/**
 * @brief 更新位置规划器
 * @param planner 规划器实例
 * @param dt 时间步长 (秒)
 * @return 当前位置
 */
float s_pos_update(SPosPlanner *planner, float dt) {
    if (planner->state == POS_TRAJ_IDLE || 
        planner->state == POS_TRAJ_COMPLETE) {
        return planner->current_pos;
    }
    
    // 更新已运行时间
    planner->elapsed_time += dt;
    
    // 计算归一化位置
    float s_norm = calculate_scurve_position(planner->elapsed_time, &planner->params);
    
    // 计算实际位置
    planner->current_pos = planner->start_pos + s_norm * planner->total_dis;
    
    // 更新状态机
    if (planner->elapsed_time >= planner->params.Tf) {
        planner->state = POS_TRAJ_COMPLETE;
        planner->current_pos = planner->target_pos;  // 确保精确到达
    }
    
    return planner->current_pos;
}

/**
 * @brief 获取当前状态
 * @param planner 规划器实例
 * @return 当前状态
 */
PosTrajState s_pos_get_state(SPosPlanner *planner) {
    return planner->state;
}
