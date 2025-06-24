"""
Odometry data visualization tool
Reads odm.csv and plots velocity/odometry over time
"""

import csv
import matplotlib.pyplot as plt
from typing import List, Dict
from pathlib import Path

def read_csv_data(file_path: str) -> List[Dict[str, float]]:
    """
    Read odometry data from CSV file
    Returns list of dictionaries with timestamp, velocities and odometry values
    """
    data = []
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f, fieldnames=['timestamp', 'v_l', 'v_r', 'o_l', 'o_r'])
        for row in reader:
            # Clean and convert data
            clean_row = {
                'timestamp': float(row['timestamp'].split(':')[1]),
                'v_l': float(row['v_l'].split(':')[1]),
                'v_r': float(row['v_r'].split(':')[1]),
                'o_l': float(row['o_l'].split(':')[1]),
                'o_r': float(row['o_r'].split(':')[1])
            }
            data.append(clean_row)
    return data

def plot_velocity(data: List[Dict[str, float]]):
    """Plot left/right wheel velocities over time"""
    timestamps = [d['timestamp'] for d in data]
    v_left = [d['v_l'] for d in data]
    v_right = [d['v_r'] for d in data]

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, v_left, label='Left Wheel Velocity (m/s)')
    plt.plot(timestamps, v_right, label='Right Wheel Velocity (m/s)')
    
    plt.title('Wheel Velocities Over Time')
    plt.xlabel('Timestamp (s)')
    plt.ylabel('Velocity (m/s)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('./MotorAsst/output/velocity_plot.png')
    plt.close()

def plot_odometry(data: List[Dict[str, float]]):
    """Plot left/right wheel odometry over time"""
    timestamps = [d['timestamp'] for d in data]
    o_left = [d['o_l'] for d in data]
    o_right = [d['o_r'] for d in data]

    plt.figure(figsize=(10, 5))
    plt.plot(timestamps, o_left, label='Left Wheel Odometry (m)')
    plt.plot(timestamps, o_right, label='Right Wheel Odometry (m)')
    
    plt.title('Wheel Odometry Over Time')
    plt.xlabel('Timestamp (s)')
    plt.ylabel('Distance (m)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('./MotorAsst/output/odometry_plot.png')
    plt.close()

def main():
    input_file = './MotorAsst/output/odom.csv'
    
    if not Path(input_file).exists():
        print(f"Error: File {input_file} not found!")
        return

    try:
        data = read_csv_data(input_file)
        plot_velocity(data)
        plot_odometry(data)
        print("Plots saved as velocity_plot.png and odometry_plot.png")
    except Exception as e:
        print(f"Error processing data: {e}")

if __name__ == "__main__":
    main()