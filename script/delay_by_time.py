import os
import re
import math # 引入math库用于计算图例列数
import matplotlib.pyplot as plt
from pathlib import Path
import argparse
from collections import defaultdict
import numpy as np

# --- 全局样式设置 (使用您最新代码中的参数) ---
plt.style.use('seaborn-v0_8-paper')
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial"],
    "font.size": 14,
    "axes.labelsize": 16,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
    "legend.fontsize": 12,
    "figure.titlesize": 18,
    "lines.linewidth": 2,
    "lines.markersize": 5
})

def extract_log_data(log_path):
    """从单个标准日志文件中提取 send_time 和 delay 数据 (单位: μs)"""
    pattern = re.compile(r'send_time:\s*(\d+)\|delay:\s*(\d+)')
    data = []
    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    send_time = int(match.group(1))
                    delay = int(match.group(2)) # 延迟单位是 μs
                    data.append((send_time, delay))
    except IOError as e:
        print(f"Error reading file {log_path}: {e}")
    return data

def extract_pcc_data(pcc_path, time_limit_sec=120):
    """从PCC日志中提取RTT(ms)，转换为μs，并生成合成时间戳"""
    delays_us = []
    try:
        with open(pcc_path, 'r', encoding='utf-8') as f:
            next(f, None)
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    try:
                        rtt_ms = float(parts[1])
                        delays_us.append(rtt_ms * 1000) # 内部统一使用μs
                    except ValueError:
                        continue
    except IOError as e:
        print(f"Error reading file {pcc_path}: {e}")
        return []

    if not delays_us:
        return []
        
    synthetic_timestamps_us = np.linspace(0, time_limit_sec * 1e6, num=len(delays_us))
    return list(zip(synthetic_timestamps_us, delays_us))


def process_log_data(data, time_limit_sec=120, interval_sec=1):
    """处理提取的数据，返回的延迟单位仍为μs"""
    if not data:
        return [], []

    base_time = data[0][0] if data[0][0] != 0 else 0
    
    if interval_sec > 0:
        aggregated_data = defaultdict(list)
        for send_time, delay in data:
            time_offset_sec = (send_time - base_time) / 1e6
            if time_offset_sec > time_limit_sec:
                break
            interval_index = int(time_offset_sec / interval_sec)
            aggregated_data[interval_index].append(delay)

        x_agg, y_agg = [], []
        for interval_index, delays in sorted(aggregated_data.items()):
            if delays:
                x_agg.append((interval_index + 0.5) * interval_sec)
                y_agg.append(np.mean(delays))
        return x_agg, y_agg
    else:
        x_raw, y_raw = [], []
        for send_time, delay in data:
            time_offset_sec = (send_time - base_time) / 1e6
            if time_offset_sec <= time_limit_sec:
                x_raw.append(time_offset_sec)
                y_raw.append(delay)
            else:
                break
        return x_raw, y_raw

def plot_all_logs(input_dir, output_dir, interval_sec):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5.5))

    colors = plt.cm.get_cmap('tab10').colors
    linestyles = ['-', '--', '-.', ':']
    markers = ['o', 's', '^', 'D', 'v', '*']
    
    # 统一收集所有数据源
    data_sources = []
    standard_logs = sorted([p for p in input_path.rglob('client_log.txt')])
    for log_path in standard_logs:
        label = log_path.parent.name
        data = extract_log_data(log_path)
        if data:
            data_sources.append({'label': label, 'data': data})
    
    pcc_logs = sorted([p for p in input_path.rglob('PCC')])
    for log_path in pcc_logs:
        if log_path.is_file():
            data = extract_pcc_data(log_path)
            if data:
                data_sources.append({'label': 'PCC', 'data': data})

    shadow_data = None
    shadow_color = 'gray'
    plot_labels = []

    for i, source in enumerate(data_sources):
        label = source['label']
        data = source['data']
        
        x, y_us = process_log_data(data, interval_sec=interval_sec)

        if x:
            # --- 单位转换：在绘图时将y值从μs转换为ms ---
            y_ms = np.array(y_us) / 1000.0

            plot_labels.append(label)
            color = colors[i % len(colors)]
            linestyle = linestyles[i % len(linestyles)]
            marker = markers[i % len(markers)] if interval_sec > 0 else None

            ax.plot(x, y_ms, label=label, color=color, linestyle=linestyle, marker=marker)
            
            if label == 'LIFE':
                # 阴影数据也使用转换后的ms单位
                shadow_data = (x, y_ms)
                shadow_color = color

    if shadow_data:
        shadow_x, shadow_y_ms = shadow_data
        ax.fill_between(shadow_x, shadow_y_ms, color=shadow_color, alpha=0.2, label='_nolegend_')

    ax.set_xlabel("Time (s)")
    # --- Y轴标签修改 ---
    ax.set_ylabel("Delay (ms)")
    # ax.set_title(f"Delay Comparison ({input_path.name})") # 标题已注释
    
    ax.set_ylim(bottom=0)
    ax.set_xlim(left=0, right=120)

    ax.grid(True, which='major', linestyle='--', linewidth=0.5, color='gray')
    ax.grid(True, which='minor', linestyle=':', linewidth=0.3, color='lightgray')
    ax.minorticks_on()

    # --- 修改图例：分两行，带黑色边框 ---
    if plot_labels:
        # 计算分两行需要的列数
        num_cols = math.ceil(len(plot_labels) / 2)
        ax.legend(
            loc='lower center',
            bbox_to_anchor=(0.5, 1.02),
            ncol=num_cols,          # 设置为计算出的列数
            frameon=True,           # 显示边框
            edgecolor='black',      # 边框颜色为黑色
            borderaxespad=0.
        )

    # 调整布局，为上方的图例留出空间
    fig.tight_layout(rect=[0, 0, 1, 0.93]) 

    output_file = output_path / f"{input_path.name}.png"
    output_file_pdf = output_path / f"{input_path.name}.pdf"
    
    fig.savefig(output_file, dpi=300, bbox_inches='tight')
    fig.savefig(output_file_pdf, bbox_inches='tight')

    print(f"图像已保存至: {output_file}")
    print(f"矢量图已保存至: {output_file_pdf}")

    plt.close(fig)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Recursively extract data from log files and plot delay curves in ms."
    )
    parser.add_argument('input_dir', help='Input directory containing log subdirectories.')
    parser.add_argument('output_dir', help='Output directory to save the plots.')
    parser.add_argument(
        '--interval', 
        type=int, 
        default=1, 
        help='Aggregation interval in seconds. Set to 0 for raw data. (default: 1)'
    )

    args = parser.parse_args()
    plot_all_logs(args.input_dir, args.output_dir, args.interval)
