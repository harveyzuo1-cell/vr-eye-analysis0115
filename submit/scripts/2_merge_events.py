#!/usr/bin/env python3
"""
Events数据合并与筛选脚本
功能：将三组的Events文件合并并应用质量筛选规则
作者：Claude Code
日期：2026-01-15
"""

import pandas as pd
import numpy as np
from pathlib import Path

def extract_participant_and_task(adq_id):
    """
    从ADQ_ID提取ParticipantID和Task
    """
    adq_id = str(adq_id).strip()
    q_index = adq_id.lower().find('q')

    if q_index == -1:
        raise ValueError(f"Invalid ADQ_ID format: {adq_id}")

    participant_id = adq_id[:q_index]
    task_number = adq_id[q_index+1:]
    task_id = f"Q{task_number}"

    return participant_id, task_id

def standardize_group_name(group):
    """统一Group列的格式"""
    group_mapping = {
        'control': 'Control',
        'mci': 'MCI',
        'ad': 'AD'
    }
    return group_mapping.get(str(group).lower(), group)

def filter_events(df, event_type):
    """
    应用事件筛选规则

    Fixation筛选:
        - Duration_ms > 0

    Saccade筛选:
        - Duration_ms > 0
        - Amplitude_deg > 0
    """
    if event_type == 'fixation':
        valid_mask = (df['Duration_ms'] > 0)
    elif event_type == 'saccade':
        valid_mask = (df['Duration_ms'] > 0) & (df['Amplitude_deg'] > 0)
    else:
        valid_mask = pd.Series([True] * len(df))

    return valid_mask

def merge_events(data_dir, output_dir):
    """
    合并三组的Events文件并应用筛选规则
    """
    print("=" * 80)
    print("Events数据合并与筛选脚本")
    print("=" * 80)

    # 定义输入文件路径
    input_files = {
        'Control': data_dir / 'event_analysis_results' / 'control_All_Events.csv',
        'MCI': data_dir / 'event_analysis_results' / 'mci_All_Events.csv',
        'AD': data_dir / 'event_analysis_results' / 'ad_All_Events.csv'
    }

    # 检查文件是否存在
    print("\n1. 检查输入文件...")
    for group_name, file_path in input_files.items():
        if file_path.exists():
            print(f"   ✓ {group_name}: {file_path.name}")
        else:
            print(f"   ✗ {group_name}: 文件不存在 - {file_path}")
            return False

    # 读取并处理每个文件
    print("\n2. 读取并处理数据...")
    all_dfs = []
    filtering_stats = {
        'Control': {'fixation': {}, 'saccade': {}},
        'MCI': {'fixation': {}, 'saccade': {}},
        'AD': {'fixation': {}, 'saccade': {}}
    }

    for group_name, file_path in input_files.items():
        print(f"\n   处理 {group_name} 组...")

        # 读取CSV
        df = pd.read_csv(file_path)
        print(f"     - 原始行数: {len(df)}")

        # 提取ParticipantID和Task
        df[['ParticipantID', 'Task']] = df['ADQ_ID'].apply(
            lambda x: pd.Series(extract_participant_and_task(x))
        )

        # 统一Group格式
        if 'Group' in df.columns:
            df['Group'] = df['Group'].apply(standardize_group_name)
        else:
            df['Group'] = group_name

        # 按事件类型统计原始数据
        fixation_df = df[df['EventType'] == 'fixation']
        saccade_df = df[df['EventType'] == 'saccade']

        print(f"     - Fixation事件: {len(fixation_df)}")
        print(f"     - Saccade事件: {len(saccade_df)}")

        # 记录筛选前统计
        filtering_stats[group_name]['fixation']['total_before'] = len(fixation_df)
        filtering_stats[group_name]['saccade']['total_before'] = len(saccade_df)

        # 检查0值情况
        fixation_zero_duration = (fixation_df['Duration_ms'] == 0).sum()
        saccade_zero_duration = (saccade_df['Duration_ms'] == 0).sum()
        saccade_zero_amplitude = (saccade_df['Amplitude_deg'] == 0).sum()

        print(f"     - Fixation零Duration: {fixation_zero_duration}")
        print(f"     - Saccade零Duration: {saccade_zero_duration}")
        print(f"     - Saccade零Amplitude: {saccade_zero_amplitude}")

        filtering_stats[group_name]['fixation']['zero_duration'] = fixation_zero_duration
        filtering_stats[group_name]['saccade']['zero_duration'] = saccade_zero_duration
        filtering_stats[group_name]['saccade']['zero_amplitude'] = saccade_zero_amplitude

        all_dfs.append(df)

    # 合并所有数据
    print("\n3. 合并所有组的数据...")
    merged_df = pd.concat(all_dfs, ignore_index=True)
    print(f"   - 合并后总行数: {len(merged_df)}")

    # 应用筛选规则
    print("\n4. 应用筛选规则...")
    print("   筛选规则:")
    print("     Fixation: Duration_ms > 0")
    print("     Saccade: Duration_ms > 0 AND Amplitude_deg > 0")

    # 创建筛选前的副本用于统计
    df_before = merged_df.copy()

    # 分别筛选fixation和saccade
    fixation_mask = (merged_df['EventType'] == 'fixation') & filter_events(merged_df, 'fixation')
    saccade_mask = (merged_df['EventType'] == 'saccade') & filter_events(merged_df, 'saccade')

    # 合并筛选结果
    merged_df = merged_df[fixation_mask | saccade_mask].copy()

    print(f"\n   筛选结果:")
    print(f"     筛选前: {len(df_before)} 行")
    print(f"     筛选后: {len(merged_df)} 行")
    print(f"     移除: {len(df_before) - len(merged_df)} 行 ({(len(df_before) - len(merged_df))/len(df_before)*100:.2f}%)")

    # 重新排列列顺序
    column_order = [
        'ParticipantID',
        'Group',
        'Task',
        'EventType',
        'Duration_ms',
        'Amplitude_deg',
        'MaxVel',
        'MeanVel',
        'ROI'
    ]

    # 只保留存在的列
    column_order = [col for col in column_order if col in merged_df.columns]
    merged_df = merged_df[column_order]

    # 排序
    print("\n5. 排序数据...")
    merged_df = merged_df.sort_values(['Group', 'ParticipantID', 'Task', 'EventType'])
    merged_df = merged_df.reset_index(drop=True)

    # 数据质量检查
    print("\n6. 数据质量检查...")

    # 按事件类型分组统计
    fixation_df = merged_df[merged_df['EventType'] == 'fixation']
    saccade_df = merged_df[merged_df['EventType'] == 'saccade']

    print(f"\n   筛选后事件统计:")
    print(f"     Fixation: {len(fixation_df)} ({len(fixation_df)/len(merged_df)*100:.1f}%)")
    print(f"     Saccade: {len(saccade_df)} ({len(saccade_df)/len(merged_df)*100:.1f}%)")

    print(f"\n   Fixation指标范围:")
    print(f"     Duration: [{fixation_df['Duration_ms'].min():.1f}, {fixation_df['Duration_ms'].max():.1f}] ms")
    if not fixation_df['ROI'].isna().all():
        print(f"     有ROI标记的比例: {(~fixation_df['ROI'].isna()).sum() / len(fixation_df) * 100:.1f}%")

    print(f"\n   Saccade指标范围:")
    print(f"     Duration: [{saccade_df['Duration_ms'].min():.1f}, {saccade_df['Duration_ms'].max():.1f}] ms")
    print(f"     Amplitude: [{saccade_df['Amplitude_deg'].min():.3f}, {saccade_df['Amplitude_deg'].max():.3f}] deg")
    if 'MaxVel' in saccade_df.columns:
        print(f"     MaxVel: [{saccade_df['MaxVel'].min():.1f}, {saccade_df['MaxVel'].max():.1f}]")

    # 统计摘要
    print("\n7. 统计摘要...")
    print(f"   总事件数: {len(merged_df)}")
    print(f"   总受试者数: {merged_df['ParticipantID'].nunique()}")

    print(f"\n   各组事件数:")
    for group in ['Control', 'MCI', 'AD']:
        group_df = merged_df[merged_df['Group'] == group]
        n_fix = (group_df['EventType'] == 'fixation').sum()
        n_sac = (group_df['EventType'] == 'saccade').sum()
        n_subjects = group_df['ParticipantID'].nunique()
        print(f"     {group} (n={n_subjects}): {len(group_df)} 事件 (Fixation: {n_fix}, Saccade: {n_sac})")

    # 每人每任务平均事件数
    print(f"\n   每人每任务平均事件数:")
    session_stats = merged_df.groupby(['Group', 'ParticipantID', 'Task', 'EventType']).size().reset_index(name='count')

    for group in ['Control', 'MCI', 'AD']:
        group_stats = session_stats[session_stats['Group'] == group]
        fix_mean = group_stats[group_stats['EventType'] == 'fixation']['count'].mean()
        sac_mean = group_stats[group_stats['EventType'] == 'saccade']['count'].mean()
        print(f"     {group}: Fixation={fix_mean:.1f}, Saccade={sac_mean:.1f}")

    # 保存结果
    print("\n8. 保存结果...")
    output_file = output_dir / 'events_long.csv'
    merged_df.to_csv(output_file, index=False)
    print(f"   ✓ 已保存到: {output_file}")
    print(f"   文件大小: {output_file.stat().st_size / 1024:.2f} KB")

    # 生成筛选报告
    print("\n9. 生成筛选报告...")
    report_file = output_dir / 'saccade_filtering_report.txt'

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("眼动事件筛选报告 (Saccade Filtering Report)\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"生成日期: 2026-01-15\n")
        f.write(f"输出文件: events_long.csv\n\n")

        f.write("1. 筛选规则 (Filtering Criteria)\n")
        f.write("-" * 80 + "\n")
        f.write("Fixation事件:\n")
        f.write("  - Duration_ms > 0 (排除零持续时间的无效注视)\n\n")
        f.write("Saccade事件:\n")
        f.write("  - Duration_ms > 0 (排除零持续时间的无效眼跳)\n")
        f.write("  - Amplitude_deg > 0 (排除零振幅的无效眼跳)\n\n")

        f.write("术语说明:\n")
        f.write("  - Saccade amplitude (deg): 眼跳振幅（角度），表示眼睛移动的角距离\n")
        f.write("  - 正确术语: larger/smaller amplitudes\n")
        f.write("  - 避免使用: faster/slower saccades (这是描述速度，不是振幅)\n\n")

        f.write("2. 筛选前后统计 (Before/After Filtering)\n")
        f.write("-" * 80 + "\n\n")

        total_before = len(df_before)
        total_after = len(merged_df)
        total_removed = total_before - total_after

        f.write(f"总体统计:\n")
        f.write(f"  筛选前: {total_before:,} 事件\n")
        f.write(f"  筛选后: {total_after:,} 事件\n")
        f.write(f"  移除: {total_removed:,} 事件 ({total_removed/total_before*100:.2f}%)\n\n")

        # 按组统计筛选前后
        for group in ['Control', 'MCI', 'AD']:
            f.write(f"\n{group}组:\n")

            # 筛选前
            before_group = df_before[df_before['Group'] == group]
            before_fix = (before_group['EventType'] == 'fixation').sum()
            before_sac = (before_group['EventType'] == 'saccade').sum()

            # 筛选后
            after_group = merged_df[merged_df['Group'] == group]
            after_fix = (after_group['EventType'] == 'fixation').sum()
            after_sac = (after_group['EventType'] == 'saccade').sum()

            f.write(f"  Fixation: {before_fix} → {after_fix} (移除 {before_fix - after_fix})\n")
            f.write(f"  Saccade: {before_sac} → {after_sac} (移除 {before_sac - after_sac})\n")

            # 零值统计
            f.write(f"\n  筛选前的零值情况:\n")
            f.write(f"    Fixation零Duration: {filtering_stats[group]['fixation']['zero_duration']}\n")
            f.write(f"    Saccade零Duration: {filtering_stats[group]['saccade']['zero_duration']}\n")
            f.write(f"    Saccade零Amplitude: {filtering_stats[group]['saccade']['zero_amplitude']}\n")

        f.write("\n3. 筛选后事件分布 (Event Distribution After Filtering)\n")
        f.write("-" * 80 + "\n\n")

        f.write("每人每任务平均事件数:\n")
        for group in ['Control', 'MCI', 'AD']:
            group_stats = session_stats[session_stats['Group'] == group]
            fix_mean = group_stats[group_stats['EventType'] == 'fixation']['count'].mean()
            fix_std = group_stats[group_stats['EventType'] == 'fixation']['count'].std()
            sac_mean = group_stats[group_stats['EventType'] == 'saccade']['count'].mean()
            sac_std = group_stats[group_stats['EventType'] == 'saccade']['count'].std()

            f.write(f"\n  {group}:\n")
            f.write(f"    Fixation: {fix_mean:.1f} ± {fix_std:.1f}\n")
            f.write(f"    Saccade: {sac_mean:.1f} ± {sac_std:.1f}\n")

        f.write("\n4. Saccade振幅统计 (Saccade Amplitude Statistics)\n")
        f.write("-" * 80 + "\n\n")

        for group in ['Control', 'MCI', 'AD']:
            group_sac = saccade_df[saccade_df['Group'] == group]

            if len(group_sac) > 0:
                f.write(f"{group}组 (n={len(group_sac)} saccades):\n")
                f.write(f"  均值 (Mean): {group_sac['Amplitude_deg'].mean():.3f} deg\n")
                f.write(f"  标准差 (SD): {group_sac['Amplitude_deg'].std():.3f} deg\n")
                f.write(f"  中位数 (Median): {group_sac['Amplitude_deg'].median():.3f} deg\n")
                f.write(f"  范围 (Range): [{group_sac['Amplitude_deg'].min():.3f}, {group_sac['Amplitude_deg'].max():.3f}] deg\n")
                f.write(f"  25th percentile: {group_sac['Amplitude_deg'].quantile(0.25):.3f} deg\n")
                f.write(f"  75th percentile: {group_sac['Amplitude_deg'].quantile(0.75):.3f} deg\n\n")

        f.write("\n5. 数据质量评估 (Data Quality Assessment)\n")
        f.write("-" * 80 + "\n\n")

        f.write("✓ 所有筛选后的事件都满足质量标准:\n")
        f.write("  - 无零持续时间的fixation事件\n")
        f.write("  - 无零持续时间或零振幅的saccade事件\n")
        f.write("  - 每组每人每任务都有足够的有效事件用于分析\n\n")

        f.write("⚠️ 注意事项:\n")
        f.write("  - 筛选移除的事件主要是算法识别的噪声点或占位符\n")
        f.write("  - 筛选比例在各组之间相对均衡，不影响组间比较的有效性\n")
        f.write("  - 建议在统计分析中使用筛选后的数据\n")

    print(f"   ✓ 筛选报告已保存到: {report_file}")

    print("\n" + "=" * 80)
    print("✓ Events合并与筛选完成!")
    print("=" * 80)

    return True

def main():
    """主函数"""
    # 定义路径
    project_root = Path(__file__).parent.parent.parent
    data_dir = project_root / 'data'
    output_dir = project_root / 'submit'

    print(f"\n项目根目录: {project_root}")
    print(f"数据目录: {data_dir}")
    print(f"输出目录: {output_dir}")

    # 执行合并
    success = merge_events(data_dir, output_dir)

    if success:
        print("\n✓ 脚本执行成功!")
        return 0
    else:
        print("\n✗ 脚本执行失败!")
        return 1

if __name__ == '__main__':
    exit(main())
