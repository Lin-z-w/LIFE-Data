#!/usr/bin/env python3
"""
make_suite_summary.py
1) 读取 bandwidth_mean_120s.csv
2) 忽略 parent，按 Suite 聚合
3) 输出 suite_summary.csv
4) 生成 algorithms / life_data / tested_ccas_data（与固定顺序对齐）
"""
import csv
from collections import defaultdict

# 1. 固定顺序与映射
algorithms = ['Copa', 'NewReno', 'Cubic', 'BBRv1', 'BBRv2',
              'PCC', 'SaTCP', 'SATPIPE']

proto2alg = {
    "QUIC Copa": "Copa",
    "QUIC Reno": "NewReno",
    "QUIC Cubic": "Cubic",
    "QUIC BBR":  "BBRv1",
    "QUIC BBRv2":"BBRv2",
    "PCC":       "PCC",
    "SaTCP":     "SaTCP",
    "SATPIPE":   "SATPIPE"
}

# 2. 读入单文件结果
raw = defaultdict(lambda: {"LIFE": [], "Peer": []})

with open("bandwidth_mean_120s.csv", newline='') as f:
    reader = csv.DictReader(f)
    for row in reader:
        full_key = row["key"]          # parent/Suite/Protocol
        bw = float(row["mean_bw_Mbps"])
        *_, suite, proto = full_key.split("/")
        bucket = "LIFE" if proto == "LIFE" else "Peer"
        raw[suite][bucket].append((proto, bw))

# 3. 写 suite_summary.csv
with open("suite_summary.csv", "w", newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["Suite", "LIFE_mean_Mbps", "Peer_mean_Mbps"])
    for suite in sorted(raw):
        life_vals = [b for p, b in raw[suite]["LIFE"]]
        peer_vals = [b for p, b in raw[suite]["Peer"]]
        life_avg = sum(life_vals) / len(life_vals) if life_vals else None
        peer_avg = sum(peer_vals) / len(peer_vals) if peer_vals else None
        writer.writerow([
            suite,
            f"{life_avg:.3f}" if life_avg is not None else "NA",
            f"{peer_avg:.3f}" if peer_avg is not None else "NA"
        ])

# 4. 按 algorithms 顺序生成数组
life_total, peer_total = defaultdict(float), defaultdict(float)
life_cnt,   peer_cnt   = defaultdict(int),   defaultdict(int)

for suite in raw:
    # 取该 Suite 的唯一 Peer 协议名
    peer_proto = next(p for p, _ in raw[suite]["Peer"])
    alg = proto2alg.get(peer_proto, peer_proto)

    # LIFE 与 Peer 分别累加
    for _, bw in raw[suite]["LIFE"]:
        life_total[alg] += bw
        life_cnt[alg]   += 1
    for _, bw in raw[suite]["Peer"]:
        peer_total[alg] += bw
        peer_cnt[alg]   += 1

life_data = [round(life_total[alg] / life_cnt[alg], 3) if life_cnt[alg] else 0.0
             for alg in algorithms]
peer_data = [round(peer_total[alg] / peer_cnt[alg], 3) if peer_cnt[alg] else 0.0
             for alg in algorithms]

# 5. 打印 / 写文件
print("algorithms =", algorithms)
print("life_data =", life_data)
print("tested_ccas_data =", peer_data)

with open("bar_data.py", "w") as f:
    f.write(f"algorithms = {algorithms}\n")
    f.write(f"life_data = {life_data}\n")
    f.write(f"tested_ccas_data = {peer_data}\n")