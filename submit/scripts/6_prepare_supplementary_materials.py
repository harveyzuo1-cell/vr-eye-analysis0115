#!/usr/bin/env python3
"""
准备补充材料脚本
功能：
1. 复制原始组级文件（带ADQ_ID）到submit文件夹
2. 创建ROI字典/映射说明文档
3. 准备Figure 3重绘源数据
作者：Claude Code
日期：2026-01-15
"""

import pandas as pd
import numpy as np
from pathlib import Path
import shutil

def copy_original_group_files(data_dir, output_dir):
    """
    复制原始组级文件（带ADQ_ID）
    """
    print("=" * 80)
    print("1. 复制原始组级文件（带ADQ_ID）")
    print("=" * 80)

    source_dir = data_dir / 'event_analysis_results'

    # 定义要复制的文件
    files_to_copy = [
        ('control_All_ROI_Summary.csv', 'original_data_with_ADQ_ID/control_All_ROI_Summary.csv'),
        ('mci_All_ROI_Summary.csv', 'original_data_with_ADQ_ID/mci_All_ROI_Summary.csv'),
        ('ad_All_ROI_Summary.csv', 'original_data_with_ADQ_ID/ad_All_ROI_Summary.csv'),
        ('control_All_Events.csv', 'original_data_with_ADQ_ID/control_All_Events.csv'),
        ('mci_All_Events.csv', 'original_data_with_ADQ_ID/mci_All_Events.csv'),
        ('ad_All_Events.csv', 'original_data_with_ADQ_ID/ad_All_Events.csv'),
    ]

    # 创建输出目录
    orig_data_dir = output_dir / 'original_data_with_ADQ_ID'
    orig_data_dir.mkdir(exist_ok=True)

    print(f"\n源目录: {source_dir}")
    print(f"目标目录: {orig_data_dir}\n")

    for source_file, dest_file in files_to_copy:
        source_path = source_dir / source_file
        dest_path = output_dir / dest_file

        if source_path.exists():
            shutil.copy2(source_path, dest_path)
            file_size = dest_path.stat().st_size / 1024  # KB
            print(f"✓ 已复制: {source_file} ({file_size:.1f} KB)")
        else:
            print(f"✗ 未找到: {source_file}")

    # 生成README说明文件
    readme_path = orig_data_dir / 'README_ORIGINAL_DATA.txt'
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("原始组级数据文件说明（带ADQ_ID）\n")
        f.write("=" * 80 + "\n\n")
        f.write("目的：\n")
        f.write("这些文件保留了原始的ADQ_ID（Analysis Data Query ID），用于追溯数据来源。\n")
        f.write("当审稿人询问特定样本（如m06）为什么出现多次时，可以通过ADQ_ID回溯。\n\n")
        f.write("文件清单：\n")
        f.write("-" * 80 + "\n\n")
        f.write("ROI Summary（注视指标汇总）：\n")
        f.write("  - control_All_ROI_Summary.csv  (Control组，20人)\n")
        f.write("  - mci_All_ROI_Summary.csv      (MCI组，20人)\n")
        f.write("  - ad_All_ROI_Summary.csv       (AD组，20人)\n\n")
        f.write("Events（眼动事件详细数据）：\n")
        f.write("  - control_All_Events.csv       (Control组)\n")
        f.write("  - mci_All_Events.csv           (MCI组)\n")
        f.write("  - ad_All_Events.csv            (AD组)\n\n")
        f.write("ADQ_ID格式：\n")
        f.write("-" * 80 + "\n")
        f.write("ADQ_ID = ParticipantID + Task\n")
        f.write("示例：\n")
        f.write("  - n1q1  = 受试者n01，Task Q1\n")
        f.write("  - m06q3 = 受试者m06，Task Q3\n")
        f.write("  - a15q5 = 受试者a15（对应ad17），Task Q5\n\n")
        f.write("与提交数据的关系：\n")
        f.write("-" * 80 + "\n")
        f.write("1. roi_summary_long.csv = 合并这3个ROI Summary文件后的long格式\n")
        f.write("2. events_long.csv = 合并这3个Events文件并筛选无效数据后的结果\n")
        f.write("3. participants_master.csv = 从subjects.csv和MMSE文件提取的受试者级别数据\n\n")
        f.write("数据追溯示例：\n")
        f.write("-" * 80 + "\n")
        f.write("如果审稿人问：\"m06在roi_summary_long.csv中出现了25次，为什么？\"\n\n")
        f.write("回答步骤：\n")
        f.write("1. 检查mci_All_ROI_Summary.csv中以m06开头的ADQ_ID\n")
        f.write("2. 发现m06q1, m06q2, m06q3, m06q4, m06q5共5个任务\n")
        f.write("3. 每个任务约5个ROI，5×5=25条记录\n")
        f.write("4. 这是正常的重复测量设计（5 tasks × ~5 ROIs per task）\n\n")
        f.write("=" * 80 + "\n")
        f.write("注意事项：\n")
        f.write("=" * 80 + "\n")
        f.write("- 这些文件未经过筛选，包含所有原始数据（包括Duration=0的占位符）\n")
        f.write("- AD组ID映射：文件中的a01-a20对应subjects.csv中的ad03-ad22\n")
        f.write("- 用于数据验证和追溯，不用于直接分析\n")

    print(f"\n✓ 说明文件已创建: {readme_path}")
    print(f"✓ 原始数据文件已准备完成")

    return True

def create_roi_dictionary(data_dir, output_dir):
    """
    创建ROI字典/映射说明文档
    """
    print("\n" + "=" * 80)
    print("2. 创建ROI字典/映射说明")
    print("=" * 80)

    # 读取ROI Summary数据以提取所有唯一的ROI
    roi_file = output_dir / 'roi_summary_long.csv'
    df = pd.read_csv(roi_file)

    # 按Task和ROI_type分组统计
    roi_by_task = {}
    for task in df['Task'].unique():
        task_df = df[df['Task'] == task]
        roi_by_task[task] = {
            'KW': sorted(task_df[task_df['ROI_type'] == 'KW']['ROI'].unique()),
            'INST': sorted(task_df[task_df['ROI_type'] == 'INST']['ROI'].unique()),
            'BG': sorted(task_df[task_df['ROI_type'] == 'BG']['ROI'].unique())
        }

    # 创建ROI字典文档
    dict_path = output_dir / 'ROI_Dictionary.txt'

    with open(dict_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("ROI（Region of Interest）字典与映射说明\n")
        f.write("=" * 80 + "\n\n")
        f.write("版本：1.0\n")
        f.write("日期：2026-01-15\n")
        f.write("数据来源：roi_summary_long.csv\n\n")

        f.write("ROI类型定义：\n")
        f.write("-" * 80 + "\n")
        f.write("1. KW (Keywords)：关键词区域\n")
        f.write("   - 包含任务相关的核心文本信息\n")
        f.write("   - 例如：时间词汇、地点名称、记忆词汇等\n\n")
        f.write("2. INST (Instructions)：指令区域\n")
        f.write("   - 包含任务说明和操作提示\n")
        f.write("   - 引导受试者完成任务的文本\n\n")
        f.write("3. BG (Background)：背景区域\n")
        f.write("   - 不包含关键信息的区域\n")
        f.write("   - 用于检测注意力分散或无关注视\n\n")

        f.write("=" * 80 + "\n")
        f.write("各任务ROI详细列表\n")
        f.write("=" * 80 + "\n\n")

        # 为每个任务列出ROI
        for task in sorted(roi_by_task.keys()):
            f.write(f"\n{task}（{task.replace('Q', 'Task ')}）\n")
            f.write("-" * 80 + "\n\n")

            task_rois = roi_by_task[task]

            # KW
            f.write(f"关键词区域（KW）- 共{len(task_rois['KW'])}个：\n")
            if task_rois['KW']:
                for roi in task_rois['KW']:
                    f.write(f"  - {roi}\n")
            else:
                f.write("  （无）\n")
            f.write("\n")

            # INST
            f.write(f"指令区域（INST）- 共{len(task_rois['INST'])}个：\n")
            if task_rois['INST']:
                for roi in task_rois['INST']:
                    f.write(f"  - {roi}\n")
            else:
                f.write("  （无）\n")
            f.write("\n")

            # BG
            f.write(f"背景区域（BG）- 共{len(task_rois['BG'])}个：\n")
            if task_rois['BG']:
                for roi in task_rois['BG']:
                    f.write(f"  - {roi}\n")
            else:
                f.write("  （无）\n")
            f.write("\n")

        f.write("=" * 80 + "\n")
        f.write("ROI统计摘要\n")
        f.write("=" * 80 + "\n\n")

        # 统计每个Task的ROI数量
        f.write("各任务ROI数量分布：\n\n")
        f.write(f"{'Task':<10} {'KW':>6} {'INST':>6} {'BG':>6} {'总计':>6}\n")
        f.write("-" * 40 + "\n")

        total_kw = total_inst = total_bg = 0
        for task in sorted(roi_by_task.keys()):
            kw_count = len(roi_by_task[task]['KW'])
            inst_count = len(roi_by_task[task]['INST'])
            bg_count = len(roi_by_task[task]['BG'])
            total = kw_count + inst_count + bg_count

            f.write(f"{task:<10} {kw_count:>6} {inst_count:>6} {bg_count:>6} {total:>6}\n")

            total_kw += kw_count
            total_inst += inst_count
            total_bg += bg_count

        f.write("-" * 40 + "\n")
        f.write(f"{'总计':<10} {total_kw:>6} {total_inst:>6} {total_bg:>6} {total_kw+total_inst+total_bg:>6}\n\n")

        f.write("ROI数据在roi_summary_long.csv中的记录数：\n")
        f.write(f"  - 总记录数：{len(df)}\n")
        f.write(f"  - 受试者数：{df['ParticipantID'].nunique()}\n")
        f.write(f"  - 任务数：{df['Task'].nunique()}\n")
        f.write(f"  - 平均每人每任务ROI数：{len(df) / (df['ParticipantID'].nunique() * df['Task'].nunique()):.1f}\n\n")

        f.write("=" * 80 + "\n")
        f.write("使用说明\n")
        f.write("=" * 80 + "\n\n")
        f.write("1. ROI分类标准：\n")
        f.write("   - ROI名称中包含\"KW\"的归类为关键词区域\n")
        f.write("   - ROI名称中包含\"INST\"的归类为指令区域\n")
        f.write("   - ROI名称中包含\"BG\"的归类为背景区域\n\n")
        f.write("2. 分析建议：\n")
        f.write("   - 主分析应使用participant-level汇总（N=60）\n")
        f.write("   - 可按ROI_type（KW/INST/BG）进行分层分析\n")
        f.write("   - 混合效应模型可将ROI作为随机效应\n\n")
        f.write("3. 数据可复现性：\n")
        f.write("   - 本字典基于roi_summary_long.csv自动生成\n")
        f.write("   - ROI列表完整且可验证\n")
        f.write("   - 任何ROI统计都可追溯到具体的ROI名称\n\n")

    print(f"✓ ROI字典已创建: {dict_path}")

    # 同时创建CSV格式的ROI映射表（更易于程序读取）
    roi_mapping_rows = []
    for task in sorted(roi_by_task.keys()):
        for roi_type in ['KW', 'INST', 'BG']:
            for roi in roi_by_task[task][roi_type]:
                roi_mapping_rows.append({
                    'Task': task,
                    'ROI': roi,
                    'ROI_type': roi_type
                })

    roi_mapping_df = pd.DataFrame(roi_mapping_rows)
    roi_mapping_csv = output_dir / 'ROI_Mapping.csv'
    roi_mapping_df.to_csv(roi_mapping_csv, index=False)
    print(f"✓ ROI映射表已创建: {roi_mapping_csv}")

    return True

def prepare_figure3_data(data_dir, output_dir):
    """
    准备Figure 3重绘源数据
    """
    print("\n" + "=" * 80)
    print("3. 准备Figure 3重绘源数据")
    print("=" * 80)

    # 读取events数据
    events_file = output_dir / 'events_long.csv'
    df = pd.read_csv(events_file)

    # 只保留saccade事件
    saccade_df = df[df['EventType'] == 'saccade'].copy()

    print(f"\n✓ 读取Events数据：{len(df)}行")
    print(f"✓ 筛选Saccade事件：{len(saccade_df)}行")

    # 按受试者和任务汇总saccade amplitude
    participant_task_summary = saccade_df.groupby(['ParticipantID', 'Group', 'Task']).agg({
        'Amplitude_deg': ['mean', 'std', 'count']
    }).reset_index()

    participant_task_summary.columns = ['ParticipantID', 'Group', 'Task',
                                        'Mean_Amplitude_deg', 'SD_Amplitude_deg', 'N_Saccades']

    # 保存participant-task level数据
    fig3_participant_task = output_dir / 'figure3_data_participant_task_level.csv'
    participant_task_summary.to_csv(fig3_participant_task, index=False)
    print(f"✓ Participant-Task level数据：{fig3_participant_task}")

    # 按组和任务汇总（用于绘图）
    group_task_summary = participant_task_summary.groupby(['Group', 'Task']).agg({
        'Mean_Amplitude_deg': ['mean', 'std'],
        'N_Saccades': 'sum',
        'ParticipantID': 'count'
    }).reset_index()

    group_task_summary.columns = ['Group', 'Task',
                                   'Mean_Amplitude_deg', 'SD_Amplitude_deg',
                                   'Total_Saccades', 'N_Participants']

    # 计算标准误（SEM）
    group_task_summary['SEM_Amplitude_deg'] = (
        group_task_summary['SD_Amplitude_deg'] /
        np.sqrt(group_task_summary['N_Participants'])
    )

    # 保存group-task level数据
    fig3_group_task = output_dir / 'figure3_data_group_task_level.csv'
    group_task_summary.to_csv(fig3_group_task, index=False)
    print(f"✓ Group-Task level数据：{fig3_group_task}")

    # 创建R绘图脚本
    r_script_path = output_dir / 'figure3_plot_script.R'
    with open(r_script_path, 'w', encoding='utf-8') as f:
        f.write("""# Figure 3 重绘脚本（R语言）
# 修正术语：使用 "Saccade Amplitude (deg)" 而非 "speed"
# 日期：2026-01-15

library(ggplot2)
library(dplyr)

# 读取数据
data <- read.csv("figure3_data_group_task_level.csv")

# 确保Group和Task的顺序正确
data$Group <- factor(data$Group, levels = c("Control", "MCI", "AD"))
data$Task <- factor(data$Task, levels = c("Q1", "Q2", "Q3", "Q4", "Q5"))

# 创建Figure 3
p <- ggplot(data, aes(x = Task, y = Mean_Amplitude_deg,
                      color = Group, group = Group)) +
  geom_line(size = 1.2) +
  geom_point(size = 3) +
  geom_errorbar(aes(ymin = Mean_Amplitude_deg - SEM_Amplitude_deg,
                    ymax = Mean_Amplitude_deg + SEM_Amplitude_deg),
                width = 0.2, size = 0.8) +
  scale_color_manual(values = c("Control" = "#2E7D32",
                                 "MCI" = "#F57C00",
                                 "AD" = "#C62828")) +
  labs(
    title = "Saccade Amplitude Across VR-MMSE Tasks",
    x = "VR-MMSE Task",
    y = "Mean Saccade Amplitude (deg)",  # 修正！！！
    color = "Group"
  ) +
  theme_classic(base_size = 14) +
  theme(
    legend.position = "top",
    plot.title = element_text(hjust = 0.5, face = "bold"),
    axis.title = element_text(face = "bold")
  )

# 保存图片
ggsave("Figure3_Saccade_Amplitude_by_Task.pdf",
       plot = p, width = 8, height = 6, dpi = 300)
ggsave("Figure3_Saccade_Amplitude_by_Task.png",
       plot = p, width = 8, height = 6, dpi = 300)

print("Figure 3 已生成！")
print("文件名：Figure3_Saccade_Amplitude_by_Task.pdf / .png")

# 打印统计摘要
cat("\\n统计摘要：\\n")
print(data %>%
  group_by(Group) %>%
  summarise(
    Mean_Amplitude = mean(Mean_Amplitude_deg),
    SD_Amplitude = sd(Mean_Amplitude_deg)
  ))
""")

    print(f"✓ R绘图脚本已创建: {r_script_path}")

    # 创建Python绘图脚本
    py_script_path = output_dir / 'figure3_plot_script.py'
    with open(py_script_path, 'w', encoding='utf-8') as f:
        f.write("""#!/usr/bin/env python3
# Figure 3 重绘脚本（Python）
# 修正术语：使用 "Saccade Amplitude (deg)" 而非 "speed"
# 日期：2026-01-15

import pandas as pd
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
print("\\n统计摘要：")
print(data.groupby('Group')['Mean_Amplitude_deg'].agg(['mean', 'std']))

plt.show()
""")

    print(f"✓ Python绘图脚本已创建: {py_script_path}")

    # 创建说明文档
    readme_path = output_dir / 'README_FIGURE3.txt'
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("Figure 3 重绘源数据与脚本说明\n")
        f.write("=" * 80 + "\n\n")
        f.write("目的：\n")
        f.write("与Table 6统一术语，将\"Saccade speed\"修正为\"Saccade amplitude (deg)\"\n\n")
        f.write("修正要点：\n")
        f.write("-" * 80 + "\n")
        f.write("1. ❌ 错误术语：Saccade speed / faster/slower saccades\n")
        f.write("2. ✅ 正确术语：Saccade amplitude (deg) / larger/smaller amplitudes\n")
        f.write("3. Y轴标签：Mean Saccade Amplitude (deg)\n")
        f.write("4. 图注说明：使用amplitude而非speed\n\n")
        f.write("文件清单：\n")
        f.write("-" * 80 + "\n")
        f.write("1. figure3_data_participant_task_level.csv\n")
        f.write("   - Participant-Task级别数据（N=60×5=300行）\n")
        f.write("   - 用于统计分析和验证\n\n")
        f.write("2. figure3_data_group_task_level.csv\n")
        f.write("   - Group-Task级别数据（3组×5任务=15行）\n")
        f.write("   - 用于直接绘图（含均值和标准误）\n\n")
        f.write("3. figure3_plot_script.R\n")
        f.write("   - R语言绘图脚本（使用ggplot2）\n")
        f.write("   - 生成PDF和PNG格式\n\n")
        f.write("4. figure3_plot_script.py\n")
        f.write("   - Python绘图脚本（使用matplotlib）\n")
        f.write("   - 生成PDF和PNG格式\n\n")
        f.write("使用方法：\n")
        f.write("-" * 80 + "\n")
        f.write("R语言用户：\n")
        f.write("  cd submit\n")
        f.write("  Rscript figure3_plot_script.R\n\n")
        f.write("Python用户：\n")
        f.write("  cd submit\n")
        f.write("  python3 figure3_plot_script.py\n\n")
        f.write("数据说明：\n")
        f.write("-" * 80 + "\n")
        f.write("- Amplitude_deg：眼跳的角距离（度数），范围通常0-10度\n")
        f.write("- 计算方法：从events_long.csv中筛选EventType='saccade'的记录\n")
        f.write("- 汇总层级：先按participant-task计算均值，再按group-task计算组均值\n")
        f.write("- 误差棒：使用标准误（SEM = SD / sqrt(N)）\n\n")
        f.write("与原Figure 3的区别：\n")
        f.write("-" * 80 + "\n")
        f.write("1. 术语修正：amplitude替代speed\n")
        f.write("2. 单位明确：(deg)角度\n")
        f.write("3. 数据来源可追溯：基于events_long.csv\n")
        f.write("4. 统计口径一致：与Table 6使用相同指标\n\n")
        f.write("=" * 80 + "\n")

    print(f"✓ 说明文档已创建: {readme_path}")
    print(f"✓ Figure 3数据和脚本准备完成")

    return True

def main():
    """主函数"""
    # 定义路径
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / 'data'
    output_dir = project_root / 'submit'

    print(f"\n项目根目录: {project_root}")
    print(f"数据目录: {data_dir}")
    print(f"输出目录: {output_dir}\n")

    # 执行三项任务
    success = True

    # 1. 复制原始组级文件
    success &= copy_original_group_files(data_dir, output_dir)

    # 2. 创建ROI字典
    success &= create_roi_dictionary(data_dir, output_dir)

    # 3. 准备Figure 3数据
    success &= prepare_figure3_data(data_dir, output_dir)

    if success:
        print("\n" + "=" * 80)
        print("✓ 所有补充材料准备完成！")
        print("=" * 80)
        print("\n新增文件：")
        print("  - original_data_with_ADQ_ID/ (6个原始CSV + README)")
        print("  - ROI_Dictionary.txt")
        print("  - ROI_Mapping.csv")
        print("  - figure3_data_participant_task_level.csv")
        print("  - figure3_data_group_task_level.csv")
        print("  - figure3_plot_script.R")
        print("  - figure3_plot_script.py")
        print("  - README_FIGURE3.txt")
        return 0
    else:
        print("\n✗ 部分任务失败")
        return 1

if __name__ == '__main__':
    exit(main())
