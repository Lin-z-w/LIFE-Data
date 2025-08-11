import matplotlib.pyplot as plt
import numpy as np

# 设置USENIX论文风格
plt.rcParams.update({
    'font.family': 'Arial',
    'font.size': 10,
    'axes.labelsize': 10,
    'axes.titlesize': 12,
    'xtick.labelsize': 14,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.titlesize': 12,
    'axes.linewidth': 0.8,
    'grid.linewidth': 0.5,
    'lines.linewidth': 1.5,
    'lines.markersize': 4,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1
})
# 数据
#algorithms = ['Reno', 'Cubic', 'BBR', 'SaTCP', 'LIFE']
algorithms = ['Copa', 'NewReno', 'Cubic', 'BBRv1', "BBRv2",'PCC', 'SaTCP', 'SATPIPE']
life_data = [55.631, 59.217, 54.388, 8.336, 44.010, 68.087, 56.740, 18.610]
tested_ccas_data = [23.666, 21.345, 19.728, 74.286, 37.025, 14.292, 24.781, 63.763]

# 设置图形
fig, ax = plt.subplots(figsize=(10, 5.5))

# 设置条形图位置
x = np.arange(len(algorithms))
width = 0.35

# 绘制条形图
bars1 = ax.bar(x - width/2, life_data, width, label='LIFE', 
               color='#8B4F8B', alpha=0.8, edgecolor='black', linewidth=0.5)
bars2 = ax.bar(x + width/2, tested_ccas_data, width, label='Tested CCAs', 
               color='#4F8B4F', alpha=0.8, edgecolor='black', linewidth=0.5)

# 设置图形属性
#ax.set_xlabel('Algorithm', fontsize=12)
ax.set_ylabel('Throughput (Mbps)', fontsize=18)
#ax.set_title('Performance Comparison: LIFE vs Tested CCAs', fontsize=18)
ax.set_xticks(x)
ax.set_xticklabels(algorithms, rotation=45, ha='right')
ax.legend(fontsize=18)

# 设置y轴范围
ax.set_ylim(0, 80)

# 添加网格
ax.grid(True, alpha=0.3)

# 添加数值标签
for i, (v1, v2) in enumerate(zip(life_data, tested_ccas_data)):
    ax.text(i - width/2, v1 + 1, f'{v1:.1f}', ha='center', va='bottom', fontsize=9)
    ax.text(i + width/2, v2 + 1, f'{v2:.1f}', ha='center', va='bottom', fontsize=9)

plt.tight_layout()
plt.show()
