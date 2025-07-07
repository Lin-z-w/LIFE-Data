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

# Configure matplotlib for publication-quality figures
plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 6,
    'figure.figsize': (8.0, 5.0),
    'figure.dpi': 600,
    'axes.labelsize': 6,
    'axes.titlesize': 7,
    'axes.linewidth': 0.6,
    'grid.linewidth': 0.3,
    'lines.linewidth': 0.8,
    'legend.fontsize': 5,
    'xtick.labelsize': 7,
    'ytick.labelsize': 7,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.major.width': 0.6,
    'ytick.major.width': 0.6,
    'xtick.minor.width': 0.3,
    'ytick.minor.width': 0.3,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'grid.linestyle': ':',
})

# ACM-style color palette
colors = ['#FF0000', '#FFA500', '#FFD700', '#006400', '#0000FF', '#4B0082', '#800080']
plt.rcParams['axes.prop_cycle'] = cycler(color=colors)

# Bandwidth config changes
config_changes = [
    (0, 85.42),
    (15, 72.80),
    (30, 110.14),
    (45, 105.71),
    (60, 63.93),
    (75, 92.89),
    (90, 80.37),
    (105, 98.54)
]


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


def parse_qperf_txt_files(directory, max_time=120):
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
        idx = np.argsort(times)
        results[name] = ([times[i] for i in idx], [bws[i] for i in idx])
    return results


def make_reference_segments(config_changes, max_time=120):
    segs = []
    cfg = sorted(config_changes, key=lambda x: x[0])
    for i, (t_start, bw_mbps) in enumerate(cfg):
        t_end = cfg[i+1][0] if i+1 < len(cfg) else max_time
        segs.append((t_start, t_end, bw_mbps))
    return segs


def plot_all_series(iperf_dict, qperf_dict, config_changes, output_path=None, draw_config=True):
    fig, ax = plt.subplots()
    iperf_style = {'marker': 'o', 'markersize': 2, 'markevery': 15, 'linewidth': 0.8, 'markeredgewidth': 0.3}
    qperf_style = {'marker': 's', 'markersize': 2, 'markevery': 15, 'linewidth': 0.8, 'markeredgewidth': 0.3}
    plotted_lines = []

    for name, (times, bws) in iperf_dict.items():
        line = ax.plot(times, bws, label=name.replace('_', ' '), **iperf_style)[0]
        plotted_lines.append((line, times, bws))
    for name, (times, bws) in qperf_dict.items():
        line = ax.plot(times, bws, label=name.replace('_', ' '), **qperf_style)[0]
        plotted_lines.append((line, times, bws))

    if draw_config:
        segs = make_reference_segments(config_changes)
        used_label = False
        for start, end, bw in segs:
            label = 'Reference' if not used_label else None
            ax.hlines(y=bw, xmin=start, xmax=end, linestyle='--', color='black', linewidth=0.8, label=label)
            used_label = True
        for start, _ in config_changes[1:]:
            ax.axvspan(start-0.5, start+0.5, color='gray', alpha=0.05)

    for line, times, bws in plotted_lines:
        label = line.get_label()
        if label.strip().upper() == 'LIFE':
            verts = [(times[0], 0)] + list(zip(times, bws)) + [(times[-1], 0)]
            poly = patches.Polygon(verts, closed=True, facecolor='blue', alpha=0.1, zorder=0)
            ax.add_patch(poly)
            break  # 只绘制一次，找到即退出

    ax.set_xlim(0, 120)
    ax.set_ylim(bottom=0)
    ax.xaxis.set_major_locator(MultipleLocator(15))
    ax.xaxis.set_minor_locator(MultipleLocator(5))
    ax.yaxis.set_major_locator(MultipleLocator(20))
    ax.yaxis.set_minor_locator(MultipleLocator(5))

    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Bandwidth (Mbps)', labelpad=4)

    legend = ax.legend(loc='upper center', fontsize=5, framealpha=0.7, bbox_to_anchor=(0.5, 1.18), ncol=9,
                       columnspacing=0.5, handlelength=0.8, handletextpad=0.3)
    legend.get_frame().set_linewidth(0.5)
    legend.get_frame().set_edgecolor('black')
    ax.grid(True, which='major', linestyle='-', alpha=0.2, linewidth=0.3)
    ax.grid(True, which='minor', linestyle=':', alpha=0.1, linewidth=0.2)

    plt.subplots_adjust(left=0.01, top=0.85)
    plt.tight_layout(pad=0.2, rect=[0.01, 0, 1, 0.88])

    if output_path:
        plt.savefig(output_path, dpi=600, bbox_inches='tight')
        print(f"Figure saved to {output_path}")
    else:
        plt.show()


def main():
    parser = argparse.ArgumentParser(description='Plot bandwidth logs in given directory')
    parser.add_argument('dir', help='Directory containing .json and .txt logs (searches recursively)')
    parser.add_argument('--output', '-o', help='Output path for figure')
    parser.add_argument('--no-config', action='store_true', help='Do not plot config change lines or reference')
    args = parser.parse_args()
    if not os.path.isdir(args.dir):
        print(f"Error: '{args.dir}' is not a valid directory.")
        return
    iperf_data = parse_iperf_json_files(args.dir)
    qperf_data = parse_qperf_txt_files(args.dir)
    if not iperf_data and not qperf_data:
        print("No data files found.")
        return
    plot_all_series(iperf_data, qperf_data, config_changes, args.output, draw_config=not args.no_config)


if __name__ == '__main__':
    main()
