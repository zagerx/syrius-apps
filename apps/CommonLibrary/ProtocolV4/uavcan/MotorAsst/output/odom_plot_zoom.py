"""
Odometry zoom visualization tool
Manual time range selection for detailed inspection
"""

import csv
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple
from pathlib import Path

# 手动配置需要放大的时间范围 (根据第一次绘图观察后填写)
ZOOM_RANGE = (1.74529e9+2609, 1.74529e9+2763)  # 示例值，根据实际需要修改

def read_csv_data(file_path: str) -> Tuple[List[Dict[str, float]], Tuple[float, float]]:
    """Read odometry data from CSV file and return data + time range"""
    data = []
    min_time = float('inf')
    max_time = float('-inf')
    
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f, fieldnames=['timestamp', 'v_l', 'v_r', 'o_l', 'o_r'])
        for row in reader:
            try:
                timestamp = float(row['timestamp'].split(':')[1])
                clean_row = {
                    'timestamp': timestamp,
                    'v_l': float(row['v_l'].split(':')[1]),
                    'v_r': float(row['v_r'].split(':')[1]),
                    'o_l': float(row['o_l'].split(':')[1]),
                    'o_r': float(row['o_r'].split(':')[1])
                }
                data.append(clean_row)
                
                # 更新时间范围
                min_time = min(min_time, timestamp)
                max_time = max(max_time, timestamp)
            except (ValueError, IndexError) as e:
                print(f"Warning: 跳过格式错误的行: {row}. Error: {e}")
    
    if not data:
        raise ValueError("CSV文件没有有效数据")
    
    return data, (min_time, max_time)

def filter_data(data: List[Dict[str, float]], zoom_range: Tuple[float, float]) -> List[Dict[str, float]]:
    """Filter data by time range"""
    return [d for d in data if zoom_range[0] <= d['timestamp'] <= zoom_range[1]]

def plot_zoomed_velocity(data: List[Dict[str, float]], zoom_range: Tuple[float, float]):
    """Plot zoomed velocity data"""
    filtered_data = filter_data(data, zoom_range)
    if not filtered_data:
        raise ValueError(f"No data in time range {zoom_range}")

    timestamps = [d['timestamp'] for d in filtered_data]
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, [d['v_l'] for d in filtered_data], label='Left Wheel Velocity (m/s)')
    plt.plot(timestamps, [d['v_r'] for d in filtered_data], label='Right Wheel Velocity (m/s)')
    
    plt.title(f'Wheel Velocities (Zoom: {zoom_range[0]:.2f}-{zoom_range[1]:.2f}s)')
    plt.xlabel('Timestamp (s)')
    plt.ylabel('Velocity (m/s)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('./MotorAsst/output/velocity_plot_zoom.png')
    plt.close()

def plot_zoomed_odometry(data: List[Dict[str, float]], zoom_range: Tuple[float, float]):
    """Plot zoomed odometry data"""
    filtered_data = filter_data(data, zoom_range)
    if not filtered_data:
        raise ValueError(f"No data in time range {zoom_range}")

    timestamps = [d['timestamp'] for d in filtered_data]
    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, [d['o_l'] for d in filtered_data], label='Left Wheel Distance (m)')
    plt.plot(timestamps, [d['o_r'] for d in filtered_data], label='Right Wheel Distance (m)')
    
    plt.title(f'Wheel Distance (Zoom: {zoom_range[0]:.2f}-{zoom_range[1]:.2f}s)')
    plt.xlabel('Timestamp (s)')
    plt.ylabel('Distance (m)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('./MotorAsst/output/odometry_plot_zoom.png')
    plt.close()

def main():
    input_file = './MotorAsst/output/odom.csv'
    output_dir = './MotorAsst/output'
    
    if not Path(input_file).exists():
        print(f"Error: Input file {input_file} not found!")
        return

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    try:
        data, (min_time, max_time) = read_csv_data(input_file)
        print(f"数据时间范围: {min_time:.2f}s 到 {max_time:.2f}s")
        print(f"当前ZOOM_RANGE: {ZOOM_RANGE[0]:.2f}s 到 {ZOOM_RANGE[1]:.2f}s")
        
        plot_zoomed_velocity(data, ZOOM_RANGE)
        plot_zoomed_odometry(data, ZOOM_RANGE)
        print(f"Zoomed plots saved to {output_dir}")
    except ValueError as e:
        print(f"错误: {str(e)}")
        print("请根据上面的时间范围调整ZOOM_RANGE参数")
    except Exception as e:
        print(f"未知错误: {str(e)}")

if __name__ == "__main__":
    main()