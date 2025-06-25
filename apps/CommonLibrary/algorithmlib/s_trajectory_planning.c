#include "s_trajectory_planning.h"
#include <math.h>
#include <string.h>
#define EPSILON 0.01f
#define MILLISEC_TO_SEC 0.001f

// 内部状态获取函数
static trajectory_actor_state_t s_velocity_actory_get_state(s_in_t *pthis);

/**
 * @brief 速度规划函数 - 200ms指令周期调用
 * @param pthis 轨迹规划器实例
 * @param new_targe 新的目标速度
 * @return 1: 开始新规划, 0: 无变化或忙碌
 */
int16_t s_velocity_planning(s_in_t* pthis, float new_targe)
{
    s_in_t *s = pthis;
    float T1,T2, total_time,initial_accel;
    // 检查是否需要更新
    if(fabsf(s->last_target - new_targe) < EPSILON) {
        return 0;
    }
    
    // 检查状态是否空闲
    if(s_velocity_actory_get_state(pthis) != TRAJ_ACTOR_STATE_IDLE) {
        return 0;
    }
    
    // 计算速度差
    float diff = fabsf(new_targe - s->cur_output);
    
    // 根据速度差选择参数
    if(diff < 1.67f) { // 1.67 rpm/s ≈ 100 rpm/min
        s->acc = 5.0f;
        s->jerk = 15.0f;
    } else if(diff > 50.0f) { // 50 rpm/s ≈ 3000 rpm/min
        s->acc = s->max_acc;
        s->jerk = s->max_jerk;
    } else { // 1.67~50 rpm/s (100~3000 rpm/min)
        s->acc = 25.0f;
        s->jerk = 75.0f;
    }
    
    // 计算方向
    s->direction = (new_targe > s->cur_output) ? 1.0f : -1.0f;
    
    // 计算各阶段时间 (单位: 秒)
    // 加加速/减减速阶段时间 T1 = T3
    T1 = s->acc / s->jerk;
    
    // 匀加速阶段时间 T2 = (Δv - a*T1)/a
    // 总速度变化量 Δv = a*(T1 + T2)
    T2 = (diff / s->acc) - T1;
    
    // 如果T2为负，使用两段式规划
    if(T2 < 0) {
        T2 = 0;
        T1 = sqrtf(diff / s->jerk);
        // 两段式规划：减加速阶段初始加速度 = jerk * T1
        initial_accel = s->jerk * T1;
    } else {
        // 三段式规划：减加速阶段初始加速度 = s->acc
        initial_accel = s->acc;
    }

    // 总时间
    total_time = T1 + T2 + T1; // T1 + T2 + T3
    
    // 计算各阶段结束速度
    s->V[0] = s->cur_output; // 初始速度
    s->V[1] = s->V[0] + s->direction * (0.5f * s->jerk * T1 * T1); // T1结束速度
    s->V[2] = s->V[1] + s->direction * (s->acc * T2); // T2结束速度
    s->V[3] = s->V[2] + s->direction * (initial_accel * T1 - 0.5f * s->jerk * T1 * T1);
    
    // 转换为毫秒时间 (用于状态机)
    s->Ts[0] = (uint16_t)(T1 * 1000.0f); // T1阶段时间(ms)
    s->Ts[1] = (uint16_t)(T2 * 1000.0f); // T2阶段时间(ms)
    s->Ts[2] = (uint16_t)(T1 * 1000.0f); // T3阶段时间(ms)
    s->Ts[3] = 0; // 未使用
    
    // 重置状态机
    s->tau = 0;
    s->elapsed_time = 0.0f;
    s->last_target = new_targe;
    s->actor_state = TRAJ_ACTOR_STATE_START;
    
    return 1;
}

/**
 * @brief 速度生成器 - 1ms周期调用
 * @param pthis 轨迹规划器实例
 * @return 当前速度值
 */
float s_velocity_actory(s_in_t *pthis)
{
    s_in_t *s = pthis;
    float retval = s->cur_output; // 默认返回当前速度
    float t; // 当前阶段内的时间(秒)
    float initial_accel = 0.0f;
    
    // 确定减加速阶段的初始加速度
    if(s->Ts[1] == 0) {
        // 两段式规划：初始加速度 = jerk * T1
        initial_accel = s->jerk * (s->Ts[0] * 0.001f);
    } else {
        // 三段式规划：初始加速度 = acc
        initial_accel = s->acc;
    }    
    switch (s->actor_state) {
        case TRAJ_ACTOR_STATE_START:
            s->V[0] = s->cur_output;
            s->tau = 0;
            s->elapsed_time = 0.0f;
            s->actor_state = TRAJ_ACTOR_STATE_T1;
            // 继续执行T1状态
            
        case TRAJ_ACTOR_STATE_T1:
            t = s->tau * MILLISEC_TO_SEC;
            retval = s->V[0] + s->direction * (0.5f * s->jerk * t * t);
            
            if (s->tau >= s->Ts[0]) {
                // T1阶段结束
                s->actor_state = TRAJ_ACTOR_STATE_T2;
                s->tau = 0;
            } else {
                s->tau++;
            }
            break;
            
        case TRAJ_ACTOR_STATE_T2:
            t = s->tau * MILLISEC_TO_SEC;
            retval = s->V[1] + s->direction * (s->acc * t);
            
            if (s->tau >= s->Ts[1]) {
                // T2阶段结束
                s->actor_state = TRAJ_ACTOR_STATE_T3;
                s->tau = 0;
            } else {
                s->tau++;
            }
            break;
            
        case TRAJ_ACTOR_STATE_T3:
            t = s->tau * MILLISEC_TO_SEC;
            
            // 使用正确的初始加速度
            retval = s->V[2] + s->direction * 
                    (initial_accel * t - 0.5f * s->jerk * t * t);
            
            if (s->tau >= s->Ts[2]) {
                // T3阶段结束，精确设置速度
                retval = s->V[3];
                s->actor_state = TRAJ_ACTOR_STATE_END;
            } else {
                s->tau++;
            }
            break;
            
        case TRAJ_ACTOR_STATE_END:
            // 确保精确到达目标速度
            retval = s->last_target;
            s->cur_output = retval;
            s->actor_state = TRAJ_ACTOR_STATE_IDLE;
            break;
            
        case TRAJ_ACTOR_STATE_IDLE:
            // 保持当前速度
            retval = s->cur_output;
            break;
            
        default:
            break;
    }
    
    // 更新当前速度
    s->cur_output = retval;
    s->elapsed_time += MILLISEC_TO_SEC;
    
    return retval;
}

/**
 * @brief 获取当前状态
 * @param pthis 轨迹规划器实例
 * @return 当前状态
 */
static trajectory_actor_state_t s_velocity_actory_get_state(s_in_t *pthis)
{
    return pthis->actor_state;
}

/**
 * @brief 初始化S型轨迹规划器
 * @param object 轨迹规划器实例
 * @param a_max 最大加速度
 * @param Ja_max 最大加加速度
 * @param a_min 最小加速度
 * @param Ja_min 最小加加速度
 */
void s_type_interpolation_init(void *object, float a_max, float Ja_max, float a_min, float Ja_min)
{
    s_in_t *s = (s_in_t *)object;
    s->actor_state  = TRAJ_ACTOR_STATE_IDLE;
    s->max_acc = a_max;
    s->max_jerk = Ja_max;
    s->min_acc = a_min;
    s->min_jerk = Ja_min;
    s->cur_output = 0.0f;
    s->last_target = 0.0f;
    s->tau = 0;
    memset(s->Ts, 0, sizeof(s->Ts));
    memset(s->V, 0, sizeof(s->V));
}