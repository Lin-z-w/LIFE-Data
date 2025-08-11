import matplotlib.pyplot as plt
import numpy as np

# Set USENIX paper style
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['grid.linewidth'] = 0.5
plt.rcParams['lines.linewidth'] = 1.5

# Create figure and axis
fig, ax = plt.subplots(1, 1, figsize=(12, 4))

# Define time points with 0.5s intervals
time_points = np.arange(0, 105.5, 0.5)  # 0 to 105 seconds, 0.5s intervals

# Initialize arrays for each algorithm
reno_data = np.zeros(len(time_points))
cubic_data = np.zeros(len(time_points))
bbr_data = np.zeros(len(time_points))
reference_data = np.zeros(len(time_points))

# Define phase boundaries (in terms of array indices)
phase1_end = int(30 / 0.5)    # 0-30s
phase2_end = int(60 / 0.5)    # 30-60s  
phase3_end = int(75 / 0.5)    # 60-75s
phase4_end = int(90 / 0.5)    # 75-90s
phase5_end = len(time_points) # 90-105s

# Phase 1 (0-30s): Initial stable period
reference_data[0:phase1_end] = 85
reno_data[0:phase1_end] = 78 + np.random.normal(0, 2, phase1_end)
cubic_data[0:phase1_end] = 75 + np.random.normal(0, 2, phase1_end)
bbr_data[0:phase1_end] = 80 + np.random.normal(0, 3, phase1_end)

# Phase 2 (30-60s): Critical packet loss period - Reno/Cubic very low
reference_data[phase1_end:phase2_end] = 105
# Reno and Cubic severely impacted by packet loss (6-7 Mbps)
reno_data[phase1_end:phase2_end] = 6.5 + np.random.normal(0, 0.5, phase2_end - phase1_end)
cubic_data[phase1_end:phase2_end] = 6.0 + np.random.normal(0, 0.5, phase2_end - phase1_end)
# BBR handles packet loss better
bbr_data[phase1_end:phase2_end] = 85 + np.random.normal(0, 5, phase2_end - phase1_end)

# Phase 3 (60-75s): Drop period
reference_data[phase2_end:phase3_end] = 65
reno_data[phase2_end:phase3_end] = 60 + np.random.normal(0, 2, phase3_end - phase2_end)
cubic_data[phase2_end:phase3_end] = 62 + np.random.normal(0, 2, phase3_end - phase2_end)
bbr_data[phase2_end:phase3_end] = 55 + np.random.normal(0, 3, phase3_end - phase2_end)

# Phase 4 (75-90s): BBR collapse period
reference_data[phase3_end:phase4_end] = 95
reno_data[phase3_end:phase4_end] = 88 + np.random.normal(0, 3, phase4_end - phase3_end)
cubic_data[phase3_end:phase4_end] = 90 + np.random.normal(0, 2, phase4_end - phase3_end)
# BBR dramatic failure - linear decline then low values
phase4_length = phase4_end - phase3_end
bbr_decline = np.linspace(50, 15, phase4_length) + np.random.normal(0, 2, phase4_length)
bbr_data[phase3_end:phase4_end] = np.clip(bbr_decline, 10, 50)

# Phase 5 (90-105s): Recovery period
reference_data[phase4_end:phase5_end] = 80
reno_data[phase4_end:phase5_end] = 78 + np.random.normal(0, 2, phase5_end - phase4_end)
cubic_data[phase4_end:phase5_end] = 80 + np.random.normal(0, 2, phase5_end - phase4_end)
# BBR rapid recovery
phase5_length = phase5_end - phase4_end
bbr_recovery = np.linspace(20, 85, phase5_length) + np.random.normal(0, 3, phase5_length)
bbr_data[phase4_end:phase5_end] = bbr_recovery

# Ensure data stays within reasonable bounds
reno_data = np.clip(reno_data, 0, 110)
cubic_data = np.clip(cubic_data, 0, 110)
bbr_data = np.clip(bbr_data, 0, 110)

# Plot the curves with straight lines connecting points
ax.plot(time_points, reference_data, 'k--', label='Reference', linewidth=2, alpha=0.8)
ax.plot(time_points, reno_data, 'r-', label='Reno', linewidth=1.5, alpha=0.8)
ax.plot(time_points, cubic_data, 'b-', label='Cubic', linewidth=1.5, alpha=0.8)
ax.plot(time_points, bbr_data, 'g-', label='BBR', linewidth=1.5, alpha=0.8)

# Add vertical lines to separate phases
ax.axvline(x=30, color='gray', linestyle='-', alpha=0.4, linewidth=0.8)
ax.axvline(x=60, color='gray', linestyle='-', alpha=0.4, linewidth=0.8)
ax.axvline(x=75, color='gray', linestyle='-', alpha=0.4, linewidth=0.8)
ax.axvline(x=90, color='gray', linestyle='-', alpha=0.4, linewidth=0.8)



# Formatting
ax.set_xlabel('Time (s)', fontsize=11)
ax.set_ylabel('Throughput (Mbps)', fontsize=11)
ax.grid(True, alpha=0.3, linestyle='--')

# Legend at the top, horizontal
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.12), ncol=4, 
          frameon=True, fancybox=False, shadow=False, fontsize=10)

# Set axis limits
ax.set_xlim(0, 105)
ax.set_ylim(0, 115)

# Remove top and right spines for cleaner look
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Adjust layout
plt.tight_layout()

plt.show()

# Optional: Save the figure
# plt.savefig('tcp_performance_comparison_final.pdf', dpi=300, bbox_inches='tight')
