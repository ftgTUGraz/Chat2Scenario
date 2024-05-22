import pandas as pd
import numpy as np

# 读取CSV文件
df = pd.read_csv('39_tracks.csv')

# 提取lonVelocity和latVelocity列
lon_velocity = df['lonVelocity']
lat_velocity = df['latVelocity']

# 计算速度的大小
speeds = np.sqrt(lon_velocity**2 + lat_velocity**2)

# 找出最大速度和最小速度
max_speed = speeds.max()
min_speed = speeds.min()

# 计算总比较次数
num_comparisons = len(speeds)

# 打印结果
print(f'最大速度: {max_speed} m/s')
print(f'最小速度: {min_speed} m/s')
print(f'总比较次数: {num_comparisons}')

# 如果需要将结果转换为km/h
max_speed_kmh = max_speed * 3.6
min_speed_kmh = min_speed * 3.6

print(f'最大速度: {max_speed_kmh} km/h')
print(f'最小速度: {min_speed_kmh} km/h')
