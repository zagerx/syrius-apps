#ifndef S_POS_PLANNING_H
#define S_POS_PLANNING_H

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

// S曲线参数结构
typedef struct {
    float T[7];          // 7个时间段 [T1, T2, T3, T4, T5, T6, T7]
    float V;             // 归一化速度 (单位位移的速度)
    float A;             // 归一化加速度 (单位位移的加速度)
    float J;             // 归一化加加速度 (单位位移的加加速度)
    float Tf;            // 总时间
} SCurveParams;

// 轨迹规划状态
typedef enum {
    POS_TRAJ_IDLE = 0,
    POS_TRAJ_ACCEL_UP,      // T1: 加加速段
    POS_TRAJ_ACCEL_CONST,   // T2: 匀加速段
    POS_TRAJ_ACCEL_DOWN,    // T3: 减加速段
    POS_TRAJ_CRUISE,        // T4: 匀速段
    POS_TRAJ_DECEL_UP,      // T5: 加减速段
    POS_TRAJ_DECEL_CONST,   // T6: 匀减速段
    POS_TRAJ_DECEL_DOWN,    // T7: 减减速段
    POS_TRAJ_COMPLETE
} PosTrajState;

// S型位置轨迹规划结构体
typedef struct {
    // 配置参数
    float max_vel;          // 最大速度 (单位/秒)
    float max_acc;          // 最大加速度 (单位/秒²)
    float max_jerk;         // 最大加加速度 (单位/秒³)
    
    // 状态变量
    PosTrajState state;     // 当前状态
    float start_pos;        // 起始位置
    float target_pos;       // 目标位置
    float current_pos;      // 当前位置
    float total_dis;        // 总位移
    
    // 运动参数
    SCurveParams params;    // S曲线参数
    float elapsed_time;     // 已运行时间
    float current_vel;      // 当前速度
    float current_acc;      // 当前加速度
    float current_jerk;     // 当前加加速度
    
    // 时间控制
    uint16_t tau;           // 当前阶段计时器
    uint16_t Ts[7];         // 各阶段时间(ms)
} SPosPlanner;

// API接口
void s_pos_planner_init(SPosPlanner *planner, float max_vel, float max_acc, float max_jerk);
int s_pos_planning(SPosPlanner *planner, float start_pos, float target_pos, float total_time);
float s_pos_update(SPosPlanner *planner, float dt);
PosTrajState s_pos_get_state(SPosPlanner *planner);

#endif /* S_POS_PLANNING_H */