#!/usr/bin/env python3
"""
ROI Summary数据合并脚本
功能：将三组的ROI Summary文件合并成一个长表格式
作者：Claude Code
日期：2026-01-15
"""

import pandas as pd
import os
from pathlib import Path

def extract_participant_and_task(adq_id):
    """
    从ADQ_ID提取ParticipantID和Task
    例如: n1q1 -> (n1, Q1), m10q3 -> (m10, Q3), ad3q2 -> (ad3, Q2)
    """
    # 移除可能的空格
    adq_id = str(adq_id).strip()

    # 查找'q'的位置
    q_index = adq_id.lower().find('q')

    if q_index == -1:
        raise ValueError(f"Invalid ADQ_ID format: {adq_id}")

    participant_id = adq_id[:q_index]
    task_number = adq_id[q_index+1:]
    task_id = f"Q{task_number}"

    return participant_id, task_id

def extract_roi_type(roi_name):
    """
    从ROI名称提取ROI类型
    例如: KW_n2q1_1 -> KW, INST_n2q1_1 -> INST, BG_n2q1 -> BG
    """
    roi_name = str(roi_name).strip()

    if roi_name.startswith('KW_'):
        return 'KW'
    elif roi_name.startswith('INST_'):
        return 'INST'
    elif roi_name.startswith('BG_'):
        return 'BG'
    else:
        return 'UNKNOWN'

def standardize_group_name(group):
    """
    统一Group列的格式
    control/mci/ad -> Control/MCI/AD
    """
    group_mapping = {
        'control': 'Control',
        'mci': 'MCI',
        'ad': 'AD'
    }
    return group_mapping.get(str(group).lower(), group)

def merge_roi_summaries(data_dir, output_dir):
    """
    合并三组的ROI Summary文件
    """
    print("=" * 60)
    print("ROI Summary数据合并脚本")
    print("=" * 60)

    # 定义输入文件路径
    input_files = {
        'Control': data_dir / 'event_analysis_results' / 'control_All_ROI_Summary.csv',
        'MCI': data_dir / 'event_analysis_results' / 'mci_All_ROI_Summary.csv',
        'AD': data_dir / 'event_analysis_results' / 'ad_All_ROI_Summary.csv'
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

    for group_name, file_path in input_files.items():
        print(f"\n   处理 {group_name} 组...")

        # 读取CSV
        df = pd.read_csv(file_path)
        print(f"     - 原始行数: {len(df)}")
        print(f"     - 原始列: {list(df.columns)}")

        # 提取ParticipantID和Task
        print("     - 提取ParticipantID和Task...")
        df[['ParticipantID', 'Task']] = df['ADQ_ID'].apply(
            lambda x: pd.Series(extract_participant_and_task(x))
        )

        # 提取ROI_type
        print("     - 提取ROI_type...")
        df['ROI_type'] = df['ROI'].apply(extract_roi_type)

        # 统一Group格式
        if 'Group' in df.columns:
            df['Group'] = df['Group'].apply(standardize_group_name)
        else:
            df['Group'] = group_name

        # 检查ROI_type分布
        roi_type_counts = df['ROI_type'].value_counts()
        print(f"     - ROI_type分布:")
        for roi_type, count in roi_type_counts.items():
            print(f"       {roi_type}: {count}")

        all_dfs.append(df)

    # 合并所有数据
    print("\n3. 合并所有组的数据...")
    merged_df = pd.concat(all_dfs, ignore_index=True)
    print(f"   - 合并后总行数: {len(merged_df)}")

    # 重新排列列顺序
    column_order = [
        'ParticipantID',
        'Group',
        'Task',
        'ROI',
        'ROI_type',
        'FixTime',
        'EnterCount',
        'RegressionCount'
    ]

    # 只保留存在的列
    column_order = [col for col in column_order if col in merged_df.columns]
    merged_df = merged_df[column_order]

    # 按ParticipantID和Task排序
    print("\n4. 排序数据...")
    merged_df = merged_df.sort_values(['Group', 'ParticipantID', 'Task', 'ROI_type'])
    merged_df = merged_df.reset_index(drop=True)

    # 数据质量检查
    print("\n5. 数据质量检查...")

    # 检查缺失值
    print("   缺失值统计:")
    missing_counts = merged_df.isnull().sum()
    for col, count in missing_counts.items():
        if count > 0:
            print(f"     {col}: {count} ({count/len(merged_df)*100:.2f}%)")

    # 检查异常值
    print("\n   数值范围检查:")
    print(f"     FixTime: [{merged_df['FixTime'].min():.3f}, {merged_df['FixTime'].max():.3f}]")
    print(f"     EnterCount: [{merged_df['EnterCount'].min()}, {merged_df['EnterCount'].max()}]")
    print(f"     RegressionCount: [{merged_df['RegressionCount'].min()}, {merged_df['RegressionCount'].max()}]")

    # 检查负值
    if (merged_df['FixTime'] < 0).any():
        print("     ⚠️  警告: FixTime存在负值!")
    if (merged_df['EnterCount'] < 0).any():
        print("     ⚠️  警告: EnterCount存在负值!")
    if (merged_df['RegressionCount'] < 0).any():
        print("     ⚠️  警告: RegressionCount存在负值!")

    # 统计摘要
    print("\n6. 统计摘要...")
    print(f"   总行数: {len(merged_df)}")
    print(f"   总受试者数: {merged_df['ParticipantID'].nunique()}")
    print(f"   各组人数:")
    for group in ['Control', 'MCI', 'AD']:
        n_subjects = merged_df[merged_df['Group'] == group]['ParticipantID'].nunique()
        print(f"     {group}: {n_subjects}")
    print(f"   任务数: {merged_df['Task'].nunique()}")
    print(f"   总ROI数: {merged_df['ROI'].nunique()}")

    # ROI类型分布
    print("\n   各组ROI_type分布:")
    roi_type_by_group = merged_df.groupby(['Group', 'ROI_type']).size().unstack(fill_value=0)
    print(roi_type_by_group)

    # 保存结果
    print("\n7. 保存结果...")
    output_file = output_dir / 'roi_summary_long.csv'
    merged_df.to_csv(output_file, index=False)
    print(f"   ✓ 已保存到: {output_file}")
    print(f"   文件大小: {output_file.stat().st_size / 1024:.2f} KB")

    # 生成数据摘要报告
    print("\n8. 生成数据摘要报告...")
    report_file = output_dir / 'roi_summary_report.txt'

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("ROI Summary合并数据报告\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"生成日期: 2026-01-15\n")
        f.write(f"输出文件: roi_summary_long.csv\n\n")

        f.write("1. 数据概览\n")
        f.write("-" * 80 + "\n")
        f.write(f"总行数: {len(merged_df)}\n")
        f.write(f"总受试者数: {merged_df['ParticipantID'].nunique()}\n")
        f.write(f"任务数: {merged_df['Task'].nunique()}\n")
        f.write(f"总ROI数: {merged_df['ROI'].nunique()}\n\n")

        f.write("2. 分组统计\n")
        f.write("-" * 80 + "\n")
        for group in ['Control', 'MCI', 'AD']:
            group_df = merged_df[merged_df['Group'] == group]
            f.write(f"\n{group}组:\n")
            f.write(f"  受试者数: {group_df['ParticipantID'].nunique()}\n")
            f.write(f"  数据行数: {len(group_df)}\n")
            f.write(f"  FixTime均值: {group_df['FixTime'].mean():.3f} ± {group_df['FixTime'].std():.3f}s\n")
            f.write(f"  EnterCount均值: {group_df['EnterCount'].mean():.2f} ± {group_df['EnterCount'].std():.2f}\n")
            f.write(f"  RegressionCount均值: {group_df['RegressionCount'].mean():.2f} ± {group_df['RegressionCount'].std():.2f}\n")

        f.write("\n3. ROI类型分布\n")
        f.write("-" * 80 + "\n")
        f.write(roi_type_by_group.to_string())
        f.write("\n\n")

        f.write("4. 数据质量\n")
        f.write("-" * 80 + "\n")
        f.write(f"缺失值: {merged_df.isnull().sum().sum()}\n")
        f.write(f"FixTime范围: [{merged_df['FixTime'].min():.3f}, {merged_df['FixTime'].max():.3f}]s\n")
        f.write(f"EnterCount范围: [{merged_df['EnterCount'].min()}, {merged_df['EnterCount'].max()}]\n")
        f.write(f"RegressionCount范围: [{merged_df['RegressionCount'].min()}, {merged_df['RegressionCount'].max()}]\n\n")

        f.write("5. 受试者列表\n")
        f.write("-" * 80 + "\n")
        for group in ['Control', 'MCI', 'AD']:
            participants = sorted(merged_df[merged_df['Group'] == group]['ParticipantID'].unique())
            f.write(f"\n{group}: {', '.join(participants)}\n")

    print(f"   ✓ 报告已保存到: {report_file}")

    print("\n" + "=" * 60)
    print("✓ ROI Summary合并完成!")
    print("=" * 60)

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
    success = merge_roi_summaries(data_dir, output_dir)

    if success:
        print("\n✓ 脚本执行成功!")
        return 0
    else:
        print("\n✗ 脚本执行失败!")
        return 1

if __name__ == '__main__':
    exit(main())
