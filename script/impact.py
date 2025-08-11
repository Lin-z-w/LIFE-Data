import os
import json
import glob
import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.ticker import MultipleLocator
from cycler import cycler
import matplotlib.patches as patches

# Set USENIX paper style
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.linewidth'] = 0.5
plt.rcParams['lines.linewidth'] = 1.5
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['grid.linestyle'] = '--'

# Fixed config reference
# config_changes = [
#     (0, 100.0, 30.0),
#     (120, 100.0, 30.0)
# ]
config_changes = [
    (0, 85.42, 20.25),
    (15, 72.80, 19.70),
    (30, 110.14, 15.84),
    (45, 105.71, 14.63),
    (60, 63.93, 18.57),
    (75, 92.89, 17.10),
    (90, 80.37, 18.57),
    (105, 98.54, 19.81),
    (120, 85.38, 20.72)
]

def parse_pcc_log_files(directory, max_time=120, bin_width=1.0):
    """Parse PCC log files and extract SendRate data"""
    results = {}
    pattern = os.path.join(directory, '**', 'PCC')
    for filepath in glob.glob(pattern, recursive=True):
        if not os.path.isfile(filepath):
            continue

        name = os.path.basename(os.path.dirname(filepath)) or "pcc"
        times, sendrates = [], []
        with open(filepath, 'r') as f:
            next(f)
            for line in f:
                parts = line.strip().split()
                if len(parts) < 2:
                    continue
                try:
                    sendrate = float(parts[0])
                    t = len(times) * bin_width  # Adjust time based on bin width
                    if t > max_time:
                        continue
                    times.append(t)
                    sendrates.append(sendrate)
                except (ValueError, IndexError):
                    continue
        
        if not times:
            continue
            
        bins = np.arange(0, max_time + bin_width, bin_width)
        inds = np.digitize(times, bins)
        avg_sendrate, centers = [], []
        for i in range(1, len(bins)):
            mask = (inds == i)
            avg_sendrate.append(np.mean(np.array(sendrates)[mask]) if np.any(mask) else 0.0)
            centers.append((bins[i-1] + bins[i]) / 2)
        
        results[name] = (centers, avg_sendrate)
    return results

def parse_iperf_json_files(directory, max_time=120, bin_width=1.0):
    results = {}
    bins = np.arange(0, max_time + bin_width, bin_width)
    pattern = os.path.join(directory, '**', '*.json')
    for filepath in glob.glob(pattern, recursive=True):
        name = os.path.splitext(os.path.basename(filepath))[0]
        times, bws = [], []
        with open(filepath, 'r') as f:
            data = json.load(f)
        for interval in data.get('intervals', []):
            s = interval.get('sum', {})
            t = s.get('start')
            bw = s.get('bits_per_second')
            if t is None or bw is None or t > max_time:
                continue
            times.append(t)
            bws.append(bw / 1e6)  # bits/s to Mbit/s
        
        if not times:
            continue
        
        # For 0.1s intervals, we need to interpolate the data
        if bin_width == 0.1:
            new_times = np.arange(0, max_time, bin_width)
            if times:
                interp_bws = np.interp(new_times, times, bws)
                results[name] = (new_times, interp_bws)
            continue
            
        # Default 1s binning
        times = np.array(times)
        bws = np.array(bws)
        inds = np.digitize(times, bins)
        avg_bw, centers = [], []
        for i in range(1, len(bins)):
            mask = (inds == i)
            avg_bw.append(bws[mask].mean() if np.any(mask) else 0.0)
            centers.append((bins[i-1] + bins[i]) / 2)
        results[name] = (centers, avg_bw)
    return results

def parse_qperf_txt_files(directory, max_time=120, bin_width=1.0):
    results = {}
    pattern = os.path.join(directory, '**', '*.txt')
    for filepath in glob.glob(pattern, recursive=True):
        name = os.path.splitext(os.path.basename(filepath))[0]
        times, bws = [], []
        with open(filepath, 'r') as f:
            for line in f:
                if not line.startswith('[qperf]'):
                    continue
                parts = line.strip().split('|')
                fields = {p.split(':',1)[0]: p.split(':',1)[1] for p in parts[1:] if ':' in p}
                t = float(fields.get('log_cnt', 0)) + 1.0
                if t > max_time:
                    continue
                bw_str = fields.get('qperf_speed', '0').rstrip('Kbit/s')
                try:
                    bw = float(bw_str)
                except ValueError:
                    bw = 0.0
                times.append(t)
                bws.append(bw / 1e3)  # Kbit/s to Mbit/s
        
        if not times:
            continue
            
        # For 0.1s intervals, interpolate the data
        if bin_width == 0.1:
            new_times = np.arange(0, max_time, bin_width)
            if times:
                interp_bws = np.interp(new_times, times, bws)
                results[name] = (new_times, interp_bws)
            continue
            
        # Default 1s binning
        idx = np.argsort(times)
        results[name] = ([times[i] for i in idx], [bws[i] for i in idx])
    return results

def make_reference_segments(config_changes, max_time=120):
    bw_segs = []
    latency_segs = []
    cfg = sorted(config_changes, key=lambda x: x[0])
    for i, (t_start, bw_mbps, latency_ms) in enumerate(cfg):
        t_end = cfg[i+1][0] if i+1 < len(cfg) else max_time
        bw_segs.append((t_start, t_end, bw_mbps))
        latency_segs.append((t_start, t_end, latency_ms * 2))
    return bw_segs, latency_segs

def plot_all_series(iperf_dict, qperf_dict, pcc_dict, config_changes, output_path=None, draw_config=True, bin_width=1.0):
    # Create figure
    fig, ax1 = plt.subplots(1, 1, figsize=(6, 4))
    ax2 = ax1.twinx()
    
    # Line styles
    iperf_style = {'linestyle': '-', 'linewidth': 1.5, 'alpha': 0.8}
    qperf_style = {'linestyle': '-', 'linewidth': 1.5, 'alpha': 0.8}
    pcc_style = {'linestyle': '-', 'linewidth': 1.5, 'alpha': 0.8}
    
    # Colors
    colors = ['r-', 'b-', 'g-', 'm-', 'c-', 'y-']
    color_idx = 0
    
    plotted_lines = []

    # Plot data with appropriate markers based on bin width
    marker_style = {}
    if bin_width == 1.0:
        marker_style = {'marker': 'o', 'markersize': 3, 'markevery': 15}
    elif bin_width == 0.1:
        marker_style = {'marker': '', 'markersize': 0}  # No markers for high-res data

    for name, (times, bws) in iperf_dict.items():
        line = ax1.plot(times, bws, colors[color_idx % len(colors)], 
                        label=name.replace('_', ' '), **{**iperf_style, **marker_style})[0]
        plotted_lines.append((line, times, bws))
        color_idx += 1
        
    for name, (times, bws) in qperf_dict.items():
        line = ax1.plot(times, bws, colors[color_idx % len(colors)], 
                        label=name.replace('_', ' '), **{**qperf_style, **marker_style})[0]
        plotted_lines.append((line, times, bws))
        color_idx += 1
        
    for name, (times, sendrates) in pcc_dict.items():
        line = ax1.plot(times, sendrates, colors[color_idx % len(colors)], 
                        label=f"{name} (PCC)", **{**pcc_style, **marker_style})[0]
        plotted_lines.append((line, times, sendrates))
        color_idx += 1

    if draw_config:
        bw_segs, latency_segs = make_reference_segments(config_changes)
        
        # Plot bandwidth reference
        used_bw_label = False
        for start, end, bw in bw_segs:
            label = 'Bandwidth Reference' if not used_bw_label else None
            ax1.hlines(y=bw, xmin=start, xmax=end, linestyle='--', color='black', 
                       linewidth=2, alpha=0.8, label=label)
            used_bw_label = True
            
        # Plot latency reference
        used_latency_label = False
        for start, end, latency in latency_segs:
            label = 'Latency Reference' if not used_latency_label else None
            ax2.hlines(y=latency, xmin=start, xmax=end, linestyle=':', color='red', 
                      linewidth=1.5, alpha=0.8, label=label)
            used_latency_label = True
            
        # Plot vertical lines at config change points
        for start, _, _ in config_changes[1:]:
            ax1.axvline(x=start, color='gray', linestyle='-', alpha=0.4, linewidth=0.8)

    ax1.set_xlim(0, 120)
    ax1.set_ylim(bottom=0)
    ax2.set_ylim(0, 50)
    
    # Formatting
    ax1.set_xlabel('Time (s)', fontsize=11)
    ax1.set_ylabel('Throughput (Mbps)', fontsize=11)
    ax2.set_ylabel('Latency (ms)', fontsize=11)
    ax2.spines['right'].set_color('red')
    ax2.tick_params(axis='y', colors='red')
    ax2.yaxis.label.set_color('red')
    
    # Legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    legend = ax1.legend(lines1 + lines2, labels1 + labels2,
                       loc='upper center', bbox_to_anchor=(0.5, 1.15), 
                       ncol=4, frameon=True, fancybox=False, shadow=False, fontsize=10)

    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    
    ax1.grid(True, alpha=0.3, linestyle='--')

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {output_path}")
    else:
        plt.show()

def main():
    parser = argparse.ArgumentParser(description='Plot bandwidth logs in given directory')
    parser.add_argument('dir', help='Directory containing .json, .txt and pcc_log files')
    parser.add_argument('--output', '-o', help='Output path for figure')
    parser.add_argument('--no-config', action='store_true', help='Do not plot config change lines or reference')
    parser.add_argument('--interval', '-i', type=float, choices=[0.1, 1.0], default=1.0,
                      help='Time interval for plotting (0.1s or 1.0s)')
    args = parser.parse_args()
    
    if not os.path.isdir(args.dir):
        print(f"Error: '{args.dir}' is not a valid directory.")
        return
    
    iperf_data = parse_iperf_json_files(args.dir, bin_width=args.interval)
    qperf_data = parse_qperf_txt_files(args.dir, bin_width=args.interval)
    pcc_data = parse_pcc_log_files(args.dir, bin_width=args.interval)
    
    if not iperf_data and not qperf_data and not pcc_data:
        print("No data files found.")
        return
    
    plot_all_series(iperf_data, qperf_data, pcc_data, config_changes, 
                   args.output, draw_config=not args.no_config, bin_width=args.interval)

if __name__ == '__main__':
    main()