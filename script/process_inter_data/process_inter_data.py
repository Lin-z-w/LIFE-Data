#!/usr/bin/env python3
"""
Step1：把 parent 目录也写进 key，避免跨目录覆盖
输出：bandwidth_mean_120s.csv
列  ：key, mean_bw_Mbps
key  : <parent>/<suite>/<protocol>
"""
import os, glob, csv, numpy as np

root_dirs = [
    "/home/cnic/LIFE-Data/origin_data/inter-protocol/groud",
    "/home/cnic/LIFE-Data/origin_data/inter-protocol/rain",
    "/home/cnic/LIFE-Data/origin_data/inter-protocol/random_loss",
    "/home/cnic/LIFE-Data/origin_data/inter-protocol/reconfig&hadover",
    "/home/cnic/LIFE-Data/origin_data/inter-protocol/standard",
]

# ---------- 下面 parse 函数与之前相同，略 ----------
def parse_pcc_for_suite(suite_dir, max_time=120):
    pcc_file = os.path.join(suite_dir, "PCC", "PCC")
    if not os.path.isfile(pcc_file):
        return {}
    times, sendrates = [], []
    with open(pcc_file) as f:
        next(f)
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            try:
                sendrate = float(parts[0])  # bps
                t = len(times)
                if t >= max_time:
                    continue
                times.append(t)
                sendrates.append(sendrate)
            except ValueError:
                continue
    if not sendrates:
        return {}
    bins = np.arange(0, max_time + 1, 1)
    inds = np.digitize(times, bins)
    avg_per_bin = [np.mean(np.array(sendrates)[inds == i])
                   for i in range(1, len(bins))
                   if np.any(inds == i)]
    if not avg_per_bin:
        return {}
    return {"PCC": np.mean(avg_per_bin)}

def _parse_qperf_txt(txt_path, max_time):
    times, bws = [], []
    with open(txt_path) as f:
        for line in f:
            if not line.startswith('[qperf]'):
                continue
            parts = line.strip().split('|')
            fields = {kv.split(':', 1)[0]: kv.split(':', 1)[1]
                      for kv in parts[1:] if ':' in kv}
            t = float(fields.get('log_cnt', 0)) + 1.0
            if t > max_time:
                continue
            bw_str = fields.get('qperf_speed', '0').rstrip('Kbit/s')
            try:
                bw = float(bw_str) / 1e3
            except ValueError:
                bw = 0.0
            times.append(t)
            bws.append(bw)
    if not bws:
        return None
    idx = np.argsort(times)
    return np.mean([bws[i] for i in idx])

def parse_suite(suite_dir, max_time=120):
    """返回 dict {protocol: mean_bw_Mbps}"""
    res = {}
    # PCC
    res.update(parse_pcc_for_suite(suite_dir))

    # LIFE
    life_path = os.path.join(suite_dir, "LIFE", "LIFE.txt")
    if os.path.isfile(life_path):
        bw = _parse_qperf_txt(life_path, max_time)
        if bw is not None:
            res["LIFE"] = bw

    # 其余协议 txt
    for sub_item in os.listdir(suite_dir):
        sub_dir = os.path.join(suite_dir, sub_item)
        if not (os.path.isdir(sub_dir) and sub_item != "LIFE"):
            continue
        txt_path = os.path.join(sub_dir, f"{sub_item}.txt")
        if os.path.isfile(txt_path):
            bw = _parse_qperf_txt(txt_path, max_time)
            if bw is not None:
                res[sub_item] = bw
    return res
# ----------------------------------------------------------

single_results = {}
for root in root_dirs:
    parent = os.path.basename(root.rstrip("/"))   # groud / rain / ...
    for suite in os.listdir(root):
        suite_dir = os.path.join(root, suite)
        if not (os.path.isdir(suite_dir) and suite.startswith("LIFE+")):
            continue
        suite_res = parse_suite(suite_dir)
        for proto, bw in suite_res.items():
            key = f"{parent}/{suite}/{proto}"
            single_results[key] = bw

# 写出
with open("bandwidth_mean_120s.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["key", "mean_bw_Mbps"])
    for k, v in single_results.items():
        writer.writerow([k, f"{v:.3f}"])

print("Step1 完成，共 %d 条记录" % len(single_results))