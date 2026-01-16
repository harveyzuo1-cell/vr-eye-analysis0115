#!/usr/bin/env python3
# Figure 3 重绘脚本（Python）
# 修正术语：使用 "Saccade Amplitude (deg)" 而非 "speed"
# 日期：2026-01-15

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import seaborn as sns

# 设置绘图风格
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 12

# 读取数据
data = pd.read_csv('figure3_data_group_task_level.csv')

# 确保Group和Task的顺序正确
data['Group'] = pd.Categorical(data['Group'],
                                categories=['Control', 'MCI', 'AD'],
                                ordered=True)
data['Task'] = pd.Categorical(data['Task'],
                               categories=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'],
                               ordered=True)
data = data.sort_values(['Group', 'Task'])

# 创建Figure 3
fig, ax = plt.subplots(figsize=(10, 6))

colors = {'Control': '#2E7D32', 'MCI': '#F57C00', 'AD': '#C62828'}
markers = {'Control': 'o', 'MCI': 's', 'AD': '^'}

for group in ['Control', 'MCI', 'AD']:
    group_data = data[data['Group'] == group]
    ax.errorbar(group_data['Task'],
                group_data['Mean_Amplitude_deg'],
                yerr=group_data['SEM_Amplitude_deg'],
                label=group,
                color=colors[group],
                marker=markers[group],
                markersize=8,
                linewidth=2,
                capsize=5,
                capthick=2)

ax.set_xlabel('VR-MMSE Task', fontweight='bold', fontsize=14)
ax.set_ylabel('Mean Saccade Amplitude (deg)', fontweight='bold', fontsize=14)  # 修正！！！
ax.set_title('Saccade Amplitude Across VR-MMSE Tasks',
             fontweight='bold', fontsize=16, pad=20)
ax.legend(title='Group', title_fontsize=12, fontsize=11,
          loc='upper right', frameon=True, shadow=True)
ax.grid(True, alpha=0.3, linestyle='--')

plt.tight_layout()

# 保存图片
plt.savefig('Figure3_Saccade_Amplitude_by_Task.pdf', dpi=300, bbox_inches='tight')
plt.savefig('Figure3_Saccade_Amplitude_by_Task.png', dpi=300, bbox_inches='tight')

print("Figure 3 已生成！")
print("文件名：Figure3_Saccade_Amplitude_by_Task.pdf / .png")

# 打印统计摘要
print("\n统计摘要：")
print(data.groupby('Group', observed=True)['Mean_Amplitude_deg'].agg(['mean', 'std']))

# plt.show()  # 注释掉，避免等待交互窗口
plt.close()
