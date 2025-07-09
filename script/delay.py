import os
import re
import matplotlib.pyplot as plt
from pathlib import Path

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

def process_log_data(data, time_limit_sec=120):
    if not data:
        return [], []

    base_time = data[0][0]
    x = []
    y = []
    for send_time, delay in data:
        time_offset_sec = (send_time - base_time) / 1e6  # 微秒转秒
        if time_offset_sec <= time_limit_sec:
            x.append(time_offset_sec)
            y.append(delay)
        else:
            break
    return x, y

def plot_all_logs(input_dir, output_dir):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 6))

    shadow_x = shadow_y = None

    for root, dirs, files in os.walk(input_dir):
        if 'client_log.txt' in files:
            log_path = Path(root) / 'client_log.txt'
            label = Path(root).name

            data = extract_log_data(log_path)
            x, y = process_log_data(data)

            if x:
                plt.plot(x, y, label=label)
                if label == 'LIFE':
                    shadow_x, shadow_y = x, y

    if shadow_x and shadow_y:
        plt.fill_between(shadow_x, shadow_y, alpha=0.3, color='gray', label='LIFE shaded')

    plt.xlabel("Time (s)")
    plt.ylabel("Delay (μs)")
    plt.title("Delay vs Time (First 120 seconds)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # 使用 input_dir 的最后一段作为图像文件名
    output_file = output_dir / f"{input_dir.name}.png"
    plt.savefig(output_file)
    print(f"图像已保存至：{output_file}")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="递归提取client_log.txt日志并绘制delay图（合成一个图像）")
    parser.add_argument('input_dir', help='输入目录')
    parser.add_argument('output_dir', help='输出目录')

    args = parser.parse_args()
    plot_all_logs(args.input_dir, args.output_dir)
