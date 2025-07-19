import os
import matplotlib.pyplot as plt
import re

def parse_log_file(file_path):
    log_cnt_list = []
    qperf_speed_list = []
    
    with open(file_path, 'r') as file:
        for line in file:
            match = re.search(r'log_cnt:(\d+).*?qperf_speed:(\d+)Kbit/s', line)
            if match:
                log_cnt = int(match.group(1))
                qperf_speed = int(match.group(2))
                log_cnt_list.append(log_cnt)
                qperf_speed_list.append(qperf_speed)
    return log_cnt_list, qperf_speed_list

def remove_max_value(data):
    """只移除数据中的最大值（保留最小值）"""
    if len(data) == 0:
        return data.copy()
    
    max_val = max(data)
    new_data = []
    max_removed = False
    
    for val in data:
        if not max_removed and val == max_val:
            max_removed = True  # 只移除第一个出现的最大值
        else:
            new_data.append(val)
    
    return new_data

def plot_data(directory, output_path=None):
    plt.figure(figsize=(10, 6))
    
    colors = ['b', 'g', 'r']  # flow 1, 2, 3的颜色
    shifts = [0, 30, 60]      # 整体右移量
    line_styles = ['-', '--', ':']  # 不同的线型
    
    for i, subdir in enumerate(['1', '2', '3']):
        file_path = os.path.join(directory, subdir, 'tmp.txt')
        if os.path.exists(file_path):
            log_cnt, qperf_speed = parse_log_file(file_path)
            
            if not log_cnt:  # 如果文件为空则跳过
                continue
                
            # 只移除最大值（保留最小值）
            filtered_qperf = remove_max_value(qperf_speed)
            
            # 调整log_cnt的长度以匹配filtered_qperf
            if len(log_cnt) > len(filtered_qperf):
                log_cnt = log_cnt[:len(filtered_qperf)]
            
            # 在开头添加0起始点，并将所有原始数据点的log_cnt+1
            extended_log_cnt = [0] + [x+1 for x in log_cnt]
            extended_qperf = [0] + filtered_qperf
            
            # 应用整体右移
            shifted_log_cnt = [x + shifts[i] for x in extended_log_cnt]
            
            # 绘制线条
            plt.plot(shifted_log_cnt, extended_qperf,
                    label=f'flow {i+1}',
                    color=colors[i],
                    linestyle=line_styles[i],
                    marker='o', markersize=5, linewidth=2)
    
    # 图表美化
    plt.xlabel('Adjusted log_cnt', fontsize=12)
    plt.ylabel('qperf_speed (Kbit/s)', fontsize=12)
    plt.title('Network Performance: qperf_speed vs Adjusted log_cnt (Max Value Removed)', fontsize=14)
    plt.legend(fontsize=10, framealpha=0.9)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    
    # 保存高分辨率图像
    if output_path is None:
        output_path = os.path.join(directory, 'qperf_speed_plot_shifted_max_removed.png')
    else:
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"High-quality plot saved to {output_path}")
    plt.show()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python script.py <directory> [output_image_path]")
        print("Example: python script.py ./data ./output/plot.png")
        sys.exit(1)
    
    directory = sys.argv[1]
    if not os.path.isdir(directory):
        print(f"Error: {directory} is not a valid directory")
        sys.exit(1)
    
    output_path = sys.argv[2] if len(sys.argv) == 3 else None
    plot_data(directory, output_path)