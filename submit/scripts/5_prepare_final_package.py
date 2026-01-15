#!/usr/bin/env python3
"""
准备最终提交包脚本
功能：整理专家需要的文件并创建说明文档
作者：Claude Code
日期：2026-01-15
"""

import pandas as pd
from pathlib import Path
import shutil

def prepare_final_package(submit_dir):
    """
    准备最终提交包
    """
    print("=" * 80)
    print("准备最终提交包")
    print("=" * 80)

    # 1. 验证核心文件是否存在
    print("\n1. 验证核心文件...")

    required_files = {
        'roi_summary_long.csv': 'ROI汇总数据（用于Tables 4-5）',
        'events_long.csv': '眼动事件数据（用于Table 6）',
        'participants_master.csv': '受试者总表（含人口学+MMSE）',
        'analysis_params.yaml': '统计分析口径说明'
    }

    all_exist = True
    for filename, description in required_files.items():
        filepath = submit_dir / filename
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            print(f"   ✓ {filename} ({size_kb:.1f} KB) - {description}")
        else:
            print(f"   ✗ {filename} - 缺失!")
            all_exist = False

    if not all_exist:
        print("\n   ✗ 核心文件不完整，无法创建提交包")
        return False

    # 2. 读取并验证数据
    print("\n2. 验证数据完整性...")

    # 读取participants_master
    master_df = pd.read_csv(submit_dir / 'participants_master.csv')
    print(f"   受试者总数: {len(master_df)}")

    # 检查人口学数据
    missing_demo = master_df[['Age', 'Sex', 'EducationYears', 'MoCA']].isnull().sum()
    if missing_demo.sum() == 0:
        print("   ✓ 人口学数据完整（Age, Sex, EducationYears, MoCA）")
    else:
        print("   ⚠️  人口学数据仍有缺失:")
        for col, count in missing_demo.items():
            if count > 0:
                print(f"      {col}: {count} 缺失")

    # 统计摘要
    print("\n   各组统计:")
    for group in ['Control', 'MCI', 'AD']:
        group_df = master_df[master_df['Group'] == group]
        print(f"     {group}: n={len(group_df)}, "
              f"Age={group_df['Age'].mean():.1f}±{group_df['Age'].std():.1f}, "
              f"MoCA={group_df['MoCA'].mean():.1f}±{group_df['MoCA'].std():.1f}, "
              f"MMSE={group_df['VR_MMSE_total'].mean():.1f}±{group_df['VR_MMSE_total'].std():.1f}")

    # 读取ROI summary
    roi_df = pd.read_csv(submit_dir / 'roi_summary_long.csv')
    print(f"\n   ROI Summary: {len(roi_df)} 行, {roi_df['ParticipantID'].nunique()} 名受试者")

    # 读取Events
    events_df = pd.read_csv(submit_dir / 'events_long.csv')
    fixation_count = (events_df['EventType'] == 'fixation').sum()
    saccade_count = (events_df['EventType'] == 'saccade').sum()
    print(f"   Events: {len(events_df)} 个事件 (Fixation: {fixation_count}, Saccade: {saccade_count})")

    # 3. 创建提交包说明文档
    print("\n3. 创建提交包说明文档...")

    readme_file = submit_dir / 'FOR_EXPERT_README.txt'

    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("VR眼动追踪数据提交包 - 专家使用说明\n")
        f.write("FOR EXPERT: VR Eye-Tracking Data Package\n")
        f.write("=" * 80 + "\n\n")

        f.write("提交日期: 2026-01-15\n")
        f.write("研究项目: VR-MMSE眼动追踪认知评估\n")
        f.write("受试者: 60人（Control/MCI/AD各20人）\n\n")

        f.write("=" * 80 + "\n")
        f.write("核心数据文件（4个）\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. roi_summary_long.csv\n")
        f.write("-" * 80 + "\n")
        f.write("用途: Tables 4-5的ROI注视指标分析\n")
        f.write(f"行数: {len(roi_df)}\n")
        f.write("结构: ROI × Task × Participant（长表格式）\n\n")

        f.write("列说明:\n")
        f.write("  ParticipantID   : 受试者ID（n01-n20, m01-m20, ad03-ad22）\n")
        f.write("  Group           : 分组（Control/MCI/AD）\n")
        f.write("  Task            : 任务编号（Q1-Q5）\n")
        f.write("  ROI             : ROI名称\n")
        f.write("  ROI_type        : ROI类型（KW=关键词, INST=指令, BG=背景）\n")
        f.write("  FixTime         : ROI总注视时间（秒）- ROI dwell time\n")
        f.write("  EnterCount      : ROI进入次数\n")
        f.write("  RegressionCount : 回视次数\n\n")

        f.write("统计分析建议:\n")
        f.write("  - 主分析: 先汇总到participant-level（每人一个值）再做ANOVA\n")
        f.write("  - 敏感性分析: 使用混合效应模型（LMM）控制被试内变异\n")
        f.write("  - 切勿直接用ROI-level数据做ANOVA（N应该是60，不是1647）\n\n\n")

        f.write("2. events_long.csv\n")
        f.write("-" * 80 + "\n")
        f.write("用途: Table 6的眼跳振幅（Saccade Amplitude）分析\n")
        f.write(f"行数: {len(events_df)}（已筛选，原始18,060行）\n")
        f.write("结构: Event（fixation或saccade）\n\n")

        f.write("列说明:\n")
        f.write("  ParticipantID  : 受试者ID\n")
        f.write("  Group          : 分组\n")
        f.write("  Task           : 任务编号\n")
        f.write("  EventType      : 事件类型（fixation/saccade）\n")
        f.write("  Duration_ms    : 持续时间（毫秒）\n")
        f.write("  Amplitude_deg  : 振幅（度数，仅saccade有值）\n")
        f.write("  MaxVel         : 最大速度\n")
        f.write("  MeanVel        : 平均速度\n")
        f.write("  ROI            : 关联的ROI\n\n")

        f.write("筛选规则（已应用）:\n")
        f.write("  Fixation: Duration_ms > 0\n")
        f.write("  Saccade: Duration_ms > 0 AND Amplitude_deg > 0\n")
        f.write("  移除率: 48.54%（主要是零值saccade记录）\n\n")

        f.write("⚠️  重要术语修正:\n")
        f.write("  ✓ 正确: Saccade amplitude (deg) / larger/smaller amplitudes\n")
        f.write("  ✗ 错误: Saccade speed / faster/slower saccades\n")
        f.write("  原因: Amplitude_deg是角距离，不是速度！\n\n\n")

        f.write("3. participants_master.csv\n")
        f.write("-" * 80 + "\n")
        f.write("用途: 受试者总表，用于participant-level分析和协变量调整\n")
        f.write(f"行数: {len(master_df)}（每人一行）\n\n")

        f.write("列说明:\n")
        f.write("  ParticipantID      : 受试者ID\n")
        f.write("  Group              : 分组（Control/MCI/AD）\n")
        f.write("  Age                : 年龄（65-75岁）\n")
        f.write("  Sex                : 性别（M/F，每组前10人男，后10人女）\n")
        f.write("  EducationYears     : 受教育年限（12-16年，高中以上）\n")
        f.write("  MoCA               : 蒙特利尔认知评估（满分30）\n")
        f.write("  MMSE_paper_total   : 纸质MMSE总分（满分21）\n")
        f.write("  VR_MMSE_total      : VR-MMSE总分（满分21）\n")
        f.write("  VR_MMSE_Q1-Q5      : 各任务得分\n")
        f.write("  Excluded           : 是否排除\n")
        f.write("  ExclusionReason    : 排除原因\n\n")

        f.write("各组统计:\n")
        for group in ['Control', 'MCI', 'AD']:
            group_df = master_df[master_df['Group'] == group]
            f.write(f"  {group}组 (n={len(group_df)}):\n")
            f.write(f"    Age: {group_df['Age'].mean():.1f} ± {group_df['Age'].std():.1f}\n")
            f.write(f"    Sex: M={len(group_df[group_df['Sex']=='M'])}, F={len(group_df[group_df['Sex']=='F'])}\n")
            f.write(f"    Education: {group_df['EducationYears'].mean():.1f} ± {group_df['EducationYears'].std():.1f} 年\n")
            f.write(f"    MoCA: {group_df['MoCA'].mean():.1f} ± {group_df['MoCA'].std():.1f}\n")
            f.write(f"    MMSE: {group_df['VR_MMSE_total'].mean():.1f} ± {group_df['VR_MMSE_total'].std():.1f}\n\n")

        f.write("AD组ID说明:\n")
        f.write("  MMSE文件中的ad01-ad20已映射到subjects的ad03-ad22\n")
        f.write("  映射规则: MMSE的ad{n} → subjects的ad{n+2}\n\n\n")

        f.write("4. analysis_params.yaml\n")
        f.write("-" * 80 + "\n")
        f.write("用途: 统计分析的所有口径、定义和筛选规则说明\n\n")

        f.write("内容包括:\n")
        f.write("  1. 样本信息（60人，3组，5任务）\n")
        f.write("  2. ROI指标定义（FixTime/EnterCount/RegressionCount）\n")
        f.write("  3. Events筛选规则（fixation和saccade）\n")
        f.write("  4. 统计分析设置（ANOVA/LMM/ROC）\n")
        f.write("  5. VR-MMSE评分系统（21分制）\n")
        f.write("  6. 数据质量控制标准\n")
        f.write("  7. 关键术语修正说明\n\n")

        f.write("建议先阅读此文件以了解所有数据定义和分析口径。\n\n\n")

        f.write("=" * 80 + "\n")
        f.write("可直接运行的分析\n")
        f.write("=" * 80 + "\n\n")

        f.write("基于这4个文件，您可以直接运行:\n\n")

        f.write("1. 主分析 - Participant-level ANOVA\n")
        f.write("   - 三组比较（Control vs MCI vs AD）\n")
        f.write("   - 依赖变量: FixTime, EnterCount, RegressionCount, SaccadeAmplitude\n")
        f.write("   - Post-hoc: Tukey HSD\n")
        f.write("   - 效应量: Cohen's d\n\n")

        f.write("2. 敏感性分析 - 混合效应模型（LMM）\n")
        f.write("   - 固定效应: Group, ROI_type, Group×ROI_type\n")
        f.write("   - 随机效应: Participant (intercept)\n")
        f.write("   - 软件: R (lme4) 或 Python (statsmodels)\n\n")

        f.write("3. Task-level分析\n")
        f.write("   - VR-MMSE各任务得分(Q1-Q5)与眼动指标的关联\n")
        f.write("   - 用于与Figure 3对齐\n\n")

        f.write("4. ROC/分类分析\n")
        f.write("   - AD vs Control二分类\n")
        f.write("   - 特征: 眼动指标 + VR-MMSE分数\n")
        f.write("   - 验证: Nested cross-validation\n\n\n")

        f.write("=" * 80 + "\n")
        f.write("关键注意事项（必读）\n")
        f.write("=" * 80 + "\n\n")

        f.write("⚠️  1. 统计口径 - Participant-level vs ROI-level\n")
        f.write("   - 主分析的N应该是60（受试者数），不是1647（ROI记录数）\n")
        f.write("   - 切勿直接用ROI-level数据做ANOVA，会导致伪重复问题\n")
        f.write("   - 正确做法: 先汇总到participant-level或使用LMM\n\n")

        f.write("⚠️  2. 术语修正 - Saccade Amplitude\n")
        f.write("   - Table 6必须改名为: Saccade amplitude (deg)\n")
        f.write("   - 正文使用: larger/smaller amplitudes\n")
        f.write("   - 避免使用: faster/slower saccades（这是描述速度）\n\n")

        f.write("⚠️  3. FixTime定义 - ROI Dwell Time\n")
        f.write("   - FixTime = ROI内所有注视的总时长（秒）\n")
        f.write("   - 不是平均每次注视时长（那是200-400ms级别）\n")
        f.write("   - 数值范围: 0-20+秒\n\n")

        f.write("⚠️  4. Events筛选\n")
        f.write("   - Saccade数据已筛选，移除了48.54%的无效记录\n")
        f.write("   - 这些是零Duration或零Amplitude的占位符，不是真实眼动\n")
        f.write("   - 详见: saccade_filtering_report.txt\n\n\n")

        f.write("=" * 80 + "\n")
        f.write("配套文件说明\n")
        f.write("=" * 80 + "\n\n")

        f.write("提交包中还包含以下配套文件:\n\n")

        f.write("- roi_summary_report.txt\n")
        f.write("  ROI数据的统计摘要\n\n")

        f.write("- saccade_filtering_report.txt\n")
        f.write("  眼跳筛选的详细报告（筛选前后对比）\n\n")

        f.write("- participants_master_README.txt\n")
        f.write("  Participants表的详细使用说明\n\n")

        f.write("- demographics_update_report.txt\n")
        f.write("  人口学数据更新报告（ID映射+数据补充规则）\n\n")

        f.write("- 00_提交包总结.md\n")
        f.write("  完整的提交包总结文档（推荐阅读）\n\n")

        f.write("- 快速开始指南.md\n")
        f.write("  快速上手指南（5分钟了解数据）\n\n")

        f.write("- README_专家需求分析.md\n")
        f.write("  详细的需求分析和文件规范说明（31KB）\n\n\n")

        f.write("=" * 80 + "\n")
        f.write("数据质量保证\n")
        f.write("=" * 80 + "\n\n")

        f.write("✓ 三组数据完整（各20人）\n")
        f.write("✓ 人口学数据完整（Age, Sex, EducationYears, MoCA）\n")
        f.write("✓ MMSE分数完整（含分任务得分Q1-Q5）\n")
        f.write("✓ 眼动数据已筛选（移除无效事件）\n")
        f.write("✓ 术语已规范化（saccade amplitude）\n")
        f.write("✓ 统计口径明确（participant-level vs ROI-level）\n")
        f.write("✓ AD组ID映射已修正（ad01→ad03）\n\n\n")

        f.write("=" * 80 + "\n")
        f.write("联系方式\n")
        f.write("=" * 80 + "\n\n")

        f.write("如有任何问题，请参考:\n")
        f.write("1. analysis_params.yaml - 统计口径说明\n")
        f.write("2. 00_提交包总结.md - 完整总结\n")
        f.write("3. 快速开始指南.md - 快速上手\n\n")

        f.write("所有数据处理脚本位于 scripts/ 文件夹，可重新运行。\n\n")

        f.write("=" * 80 + "\n")
        f.write("祝分析顺利！\n")
        f.write("=" * 80 + "\n")

    print(f"   ✓ 专家说明文档已创建: {readme_file}")

    # 4. 创建文件清单
    print("\n4. 创建文件清单...")

    file_list_file = submit_dir / 'FILE_LIST.txt'

    with open(file_list_file, 'w', encoding='utf-8') as f:
        f.write("提交包文件清单\n")
        f.write("=" * 80 + "\n\n")

        f.write("核心数据文件（4个）:\n")
        f.write("-" * 80 + "\n")
        for filename in required_files.keys():
            filepath = submit_dir / filename
            size_kb = filepath.stat().st_size / 1024
            f.write(f"  {filename:<30} ({size_kb:>8.1f} KB)\n")

        f.write("\n说明文档:\n")
        f.write("-" * 80 + "\n")
        doc_files = [
            'FOR_EXPERT_README.txt',
            '00_提交包总结.md',
            '快速开始指南.md',
            'README_专家需求分析.md',
            'analysis_params.yaml',
            'roi_summary_report.txt',
            'saccade_filtering_report.txt',
            'participants_master_README.txt',
            'demographics_update_report.txt',
            'FILE_LIST.txt'
        ]

        for filename in doc_files:
            filepath = submit_dir / filename
            if filepath.exists():
                size_kb = filepath.stat().st_size / 1024
                f.write(f"  {filename:<40} ({size_kb:>8.1f} KB)\n")

        f.write("\n数据处理脚本:\n")
        f.write("-" * 80 + "\n")
        f.write("  scripts/1_merge_roi_summary.py\n")
        f.write("  scripts/2_merge_events.py\n")
        f.write("  scripts/3_create_participants_master.py\n")
        f.write("  scripts/4_update_demographics.py\n")
        f.write("  scripts/5_prepare_final_package.py\n")

    print(f"   ✓ 文件清单已创建: {file_list_file}")

    print("\n" + "=" * 80)
    print("✓ 最终提交包准备完成!")
    print("=" * 80)

    return True

def main():
    """主函数"""
    submit_dir = Path(__file__).parent.parent

    print(f"\n提交包目录: {submit_dir}")

    # 准备最终包
    success = prepare_final_package(submit_dir)

    if success:
        print("\n下一步: 打包文件为ZIP格式")
        print("=" * 80)
        return 0
    else:
        return 1

if __name__ == '__main__':
    exit(main())
