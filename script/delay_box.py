import os
import re
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

# 设置字体为Arial
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 12

def extract_log_data(log_path):
    pattern = re.compile(r'send_time:\s*(\d+)\|delay:\s*(\d+)')
    data = []
    with open(log_path, 'r') as f:
        for line in f:
            match = pattern.search(line)
            if match:
                send_time = int(match.group(1))
                delay = int(match.group(2))
                data.append((send_time, delay))
    return data

def extract_pcc_data(pcc_path):
    data = []
    with open(pcc_path, 'r') as f:
        # 跳过标题行
        next(f)
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 2:
                try:
                    rtt_ms = float(parts[1])
                    # 将毫秒转换为微秒
                    rtt_us = rtt_ms * 1000
                    data.append((0, rtt_us))  # 使用0作为时间戳，因为我们不关心PCC的时间戳
                except ValueError:
                    continue
    return data

def process_log_data(data, time_limit_sec=120):
    if not data:
        return []

    base_time = data[0][0]
    delays = []
    for send_time, delay in data:
        time_offset_sec = (send_time - base_time) / 1e6  # 微秒转秒
        if time_offset_sec <= time_limit_sec or send_time == 0:  # PCC数据的时间戳为0
            delays.append(delay)
        else:
            break
    
    # 去掉1%的极大值
    if delays:
        delays = np.array(delays)
        percentile_99 = np.percentile(delays, 99)
        delays = delays[delays <= percentile_99]
        delays = delays.tolist()
    
    return delays

def plot_all_logs(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # USENIX风格的图像设置
    plt.figure(figsize=(8, 5))
    
    # 收集所有数据
    all_delays = []
    labels = []
    
    # 处理client_log.txt文件
    for root, dirs, files in os.walk(input_dir):
        if 'client_log.txt' in files:
            log_path = Path(root) / 'client_log.txt'
            label = Path(root).name

            data = extract_log_data(log_path)
            delays = process_log_data(data)

            if delays:
                all_delays.append(delays)
                labels.append(label)
    
    # 处理PCC文件
    pcc_files = list(input_dir.rglob('PCC'))
    for pcc_file in pcc_files:
        if pcc_file.is_file():
            data = extract_pcc_data(pcc_file)
            delays = process_log_data(data)
            
            if delays:
                all_delays.append(delays)
                labels.append('PCC')

    # 绘制箱型图
    if all_delays:
        box_plot = plt.boxplot(all_delays, labels=labels, patch_artist=True, showmeans=True,
                              boxprops=dict(facecolor='lightblue', alpha=0.7),
                              medianprops=dict(color='red', linewidth=2),
                              flierprops=dict(marker='o', markersize=4, alpha=0.5))
        
        # 为不同的箱子设置简洁的颜色
        colors = ['lightblue', 'lightgreen', 'lightcoral', 'lightyellow', 'lightpink']
        for i, patch in enumerate(box_plot['boxes']):
            patch.set_facecolor(colors[i % len(colors)])
            patch.set_alpha(0.7)
        
        # 突出显示LIFE（如果存在）
        if 'LIFE' in labels:
            life_index = labels.index('LIFE')
            box_plot['boxes'][life_index].set_facecolor('orange')
            box_plot['boxes'][life_index].set_alpha(0.8)
            box_plot['boxes'][life_index].set_linewidth(2)

    plt.xlabel("System Type")
    plt.ylabel("Delay (μs)")
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.xticks(rotation=0)
    
    # USENIX风格的边框
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.5)
    ax.spines['bottom'].set_linewidth(0.5)
    
    plt.tight_layout()

    # 使用 input_dir 的最后一段作为图像文件名
    output_file = output_dir / f"{input_dir.name}_boxplot.pdf"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Boxplot saved to: {output_file}")
    
    # 输出统计信息
    print("\nStatistics (after removing top 1% outliers):")
    for i, (label, delays) in enumerate(zip(labels, all_delays)):
        print(f"{label}:")
        print(f"  Sample size: {len(delays)}")
        print(f"  Median: {np.median(delays):.2f} μs")
        print(f"  Mean: {np.mean(delays):.2f} μs")
        print(f"  Std dev: {np.std(delays):.2f} μs")
        print(f"  Min: {np.min(delays)} μs")
        print(f"  Max: {np.max(delays)} μs")
        print(f"  25th percentile: {np.percentile(delays, 25):.2f} μs")
        print(f"  75th percentile: {np.percentile(delays, 75):.2f} μs")
        print()

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Extract client_log.txt logs and generate delay boxplot")
    parser.add_argument('input_dir', help='Input directory')
    parser.add_argument('output_dir', help='Output directory')

    args = parser.parse_args()
    plot_all_logs(args.input_dir, args.output_dir)