#!/usr/bin/env python3
"""
Participants Master表创建脚本
功能：整合受试者基本信息、分组和MMSE分数
作者：Claude Code
日期：2026-01-15
"""

import pandas as pd
import numpy as np
from pathlib import Path

def create_participants_master(data_dir, output_dir):
    """
    创建Participants Master表
    """
    print("=" * 80)
    print("Participants Master表创建脚本")
    print("=" * 80)

    # 1. 读取subjects.csv（受试者ID和分组）
    print("\n1. 读取受试者分组信息...")
    subjects_file = data_dir / 'normalized_features' / 'subjects.csv'

    if not subjects_file.exists():
        print(f"   ✗ 文件不存在: {subjects_file}")
        return False

    subjects_df = pd.read_csv(subjects_file)
    print(f"   ✓ 已读取 {len(subjects_df)} 名受试者")

    # 2. 读取MMSE分数文件
    print("\n2. 读取MMSE分数...")

    mmse_files = {
        'Control': data_dir / 'MMSE_Score' / '控制组.csv',
        'MCI': data_dir / 'MMSE_Score' / '轻度认知障碍组.csv',
        'AD': data_dir / 'MMSE_Score' / '阿尔兹海默症组.csv'
    }

    # 读取所有MMSE文件
    mmse_data = []

    for group_name, file_path in mmse_files.items():
        if not file_path.exists():
            print(f"   ✗ {group_name}: 文件不存在 - {file_path}")
            continue

        df = pd.read_csv(file_path)

        # 移除统计行（平均、标准差）
        df = df[~df.iloc[:, 0].astype(str).str.contains('平均|标准差', na=False)]

        # 第一列是受试者ID
        id_col = df.columns[0]

        # 标准化ID格式
        df['ParticipantID_original'] = df[id_col]

        # 处理MCI组的大写M
        if group_name == 'MCI':
            df['ParticipantID'] = df[id_col].str.lower()  # M01 -> m01
        else:
            df['ParticipantID'] = df[id_col]

        df['Group'] = group_name

        # 选择需要的列
        columns_to_keep = ['ParticipantID', 'ParticipantID_original', 'Group']

        # MMSE题目列（跳过第一列ID和最后一列总分）
        mmse_columns = df.columns[1:-1].tolist()

        # 定义MMSE各部分
        mmse_q_mapping = {
            'VR_MMSE_Q1_年份': df.columns[1],
            'VR_MMSE_Q1_季节': df.columns[2],
            'VR_MMSE_Q1_月份': df.columns[3],
            'VR_MMSE_Q1_星期': df.columns[4],
            'VR_MMSE_Q2_省市区': df.columns[5],
            'VR_MMSE_Q2_街道': df.columns[6],
            'VR_MMSE_Q2_建筑': df.columns[7],
            'VR_MMSE_Q2_楼层': df.columns[8],
            'VR_MMSE_Q3_即刻记忆': df.columns[9],
            'VR_MMSE_Q4_100-7': df.columns[10],
            'VR_MMSE_Q4_93-7': df.columns[11],
            'VR_MMSE_Q4_86-7': df.columns[12],
            'VR_MMSE_Q4_79-7': df.columns[13],
            'VR_MMSE_Q4_72-7': df.columns[14],
            'VR_MMSE_Q5_词1': df.columns[15],
            'VR_MMSE_Q5_词2': df.columns[16],
            'VR_MMSE_Q5_词3': df.columns[17],
        }

        # ⚠️ 重要：在添加新列之前先保存总分列（列18，即最后一列）
        total_score_col = df[df.columns[18]].copy()

        # 计算各任务得分
        # MMSE列结构：列0=受试者, 列1-18=题目, 列19=总分（共20列）
        # Q1: 时间定向 (年份+季节+月份+星期) = 5分
        # 列1=年份, 列2=季节, 列3=月份, 列4=星期
        df['VR_MMSE_Q1'] = (df[df.columns[1]] + df[df.columns[2]] +
                            df[df.columns[3]] + df[df.columns[4]])

        # Q2: 地点定向 (省市区+街道+建筑+楼层) = 5分
        # 列5=省市区, 列6=街道, 列7=建筑, 列8=楼层
        df['VR_MMSE_Q2'] = (df[df.columns[5]] + df[df.columns[6]] +
                            df[df.columns[7]] + df[df.columns[8]])

        # Q3: 即刻记忆 = 3分
        # 列9=即刻记忆
        df['VR_MMSE_Q3'] = df[df.columns[9]]

        # Q4: 注意力与计算 (100-7, 93-7, 86-7, 79-7, 72-7) = 5分
        # 列10-14: 100-7, 93-7, 86-7, 79-7, 72-7
        df['VR_MMSE_Q4'] = (df[df.columns[10]] + df[df.columns[11]] +
                            df[df.columns[12]] + df[df.columns[13]] + df[df.columns[14]])

        # Q5: 延迟回忆 (词1+词2+词3) = 3分
        # 列15-17: 词1, 词2, 词3
        df['VR_MMSE_Q5'] = (df[df.columns[15]] + df[df.columns[16]] + df[df.columns[17]])

        # MMSE总分（使用之前保存的总分列）
        df['MMSE_paper_total'] = total_score_col

        # VR-MMSE总分（应该与paper总分一致）
        df['VR_MMSE_total'] = total_score_col

        # 保留所需列
        result_cols = ['ParticipantID', 'ParticipantID_original', 'Group',
                       'VR_MMSE_Q1', 'VR_MMSE_Q2', 'VR_MMSE_Q3', 'VR_MMSE_Q4', 'VR_MMSE_Q5',
                       'VR_MMSE_total', 'MMSE_paper_total']

        mmse_data.append(df[result_cols])

        print(f"   ✓ {group_name}: {len(df)} 名受试者")

    # 合并所有MMSE数据
    mmse_df = pd.concat(mmse_data, ignore_index=True)
    print(f"\n   合并后: {len(mmse_df)} 名受试者")

    # 3. 合并subjects和MMSE数据
    print("\n3. 合并分组信息和MMSE分数...")

    # 标准化subjects_df中的Group名称
    subjects_df['Group'] = subjects_df['group_type'].map({
        'control': 'Control',
        'mci': 'MCI',
        'ad': 'AD'
    })

    # 合并数据
    master_df = pd.merge(
        subjects_df[['subject_id', 'Group']],
        mmse_df,
        left_on='subject_id',
        right_on='ParticipantID',
        how='left'
    )

    # 如果合并后ParticipantID为空，使用subject_id
    master_df['ParticipantID'] = master_df['subject_id']

    # 如果MMSE合并后Group_y存在但Group_x不存在，使用Group_y
    if 'Group_y' in master_df.columns:
        master_df['Group'] = master_df['Group_x'].fillna(master_df['Group_y'])
        master_df = master_df.drop(columns=['Group_x', 'Group_y'])
    elif 'Group_x' in master_df.columns and 'Group_y' not in master_df.columns:
        master_df['Group'] = master_df['Group_x']
        master_df = master_df.drop(columns=['Group_x'])

    print(f"   ✓ 合并完成: {len(master_df)} 行")

    # 检查未匹配的记录
    unmatched = master_df[master_df['VR_MMSE_total'].isna()]
    if len(unmatched) > 0:
        print(f"\n   ⚠️  警告: {len(unmatched)} 名受试者未匹配到MMSE数据:")
        for idx, row in unmatched.iterrows():
            group_val = row['Group'] if 'Group' in row and pd.notna(row['Group']) else row.get('group_type', 'Unknown')
            print(f"      {row['ParticipantID']} ({group_val})")

    # 4. 添加缺失字段（标记为NA）
    print("\n4. 添加人口学字段...")

    # 这些字段需要从其他来源补充
    master_df['Age'] = np.nan
    master_df['Sex'] = np.nan
    master_df['EducationYears'] = np.nan
    master_df['MoCA'] = np.nan

    # 排除标记（当前都未排除）
    master_df['Excluded'] = False
    master_df['ExclusionReason'] = np.nan

    print("   ⚠️  以下字段当前为空，需要后续补充:")
    print("      - Age (年龄)")
    print("      - Sex (性别)")
    print("      - EducationYears (受教育年限)")
    print("      - MoCA (蒙特利尔认知评估)")

    # 5. 重新排列列顺序
    print("\n5. 整理最终列顺序...")

    final_columns = [
        'ParticipantID',
        'Group',
        'Age',
        'Sex',
        'EducationYears',
        'MoCA',
        'MMSE_paper_total',
        'VR_MMSE_total',
        'VR_MMSE_Q1',
        'VR_MMSE_Q2',
        'VR_MMSE_Q3',
        'VR_MMSE_Q4',
        'VR_MMSE_Q5',
        'Excluded',
        'ExclusionReason'
    ]

    master_df = master_df[final_columns]

    # 按Group和ParticipantID排序
    master_df = master_df.sort_values(['Group', 'ParticipantID'])
    master_df = master_df.reset_index(drop=True)

    # 6. 数据质量检查
    print("\n6. 数据质量检查...")

    print(f"\n   总受试者数: {len(master_df)}")
    print(f"   各组人数:")
    for group in ['Control', 'MCI', 'AD']:
        n = len(master_df[master_df['Group'] == group])
        print(f"     {group}: {n}")

    print(f"\n   MMSE分数统计:")
    for group in ['Control', 'MCI', 'AD']:
        group_df = master_df[master_df['Group'] == group]
        if not group_df['VR_MMSE_total'].isna().all():
            mean_score = group_df['VR_MMSE_total'].mean()
            std_score = group_df['VR_MMSE_total'].std()
            print(f"     {group}: {mean_score:.1f} ± {std_score:.1f}")

    print(f"\n   各任务得分范围:")
    for q in ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']:
        col = f'VR_MMSE_{q}'
        if col in master_df.columns:
            min_val = master_df[col].min()
            max_val = master_df[col].max()
            print(f"     {q}: [{min_val:.0f}, {max_val:.0f}]")

    # 7. 保存结果
    print("\n7. 保存结果...")
    output_file = output_dir / 'participants_master.csv'
    master_df.to_csv(output_file, index=False)
    print(f"   ✓ 已保存到: {output_file}")
    print(f"   文件大小: {output_file.stat().st_size / 1024:.2f} KB")

    # 8. 生成说明文档
    print("\n8. 生成说明文档...")
    readme_file = output_dir / 'participants_master_README.txt'

    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("Participants Master表说明文档\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"生成日期: 2026-01-15\n")
        f.write(f"文件名: participants_master.csv\n\n")

        f.write("1. 数据概览\n")
        f.write("-" * 80 + "\n")
        f.write(f"总受试者数: {len(master_df)}\n")
        f.write(f"Control组: {len(master_df[master_df['Group'] == 'Control'])}\n")
        f.write(f"MCI组: {len(master_df[master_df['Group'] == 'MCI'])}\n")
        f.write(f"AD组: {len(master_df[master_df['Group'] == 'AD'])}\n\n")

        f.write("2. 字段说明\n")
        f.write("-" * 80 + "\n\n")

        field_descriptions = {
            'ParticipantID': '受试者ID（如 n01, m10, ad3）',
            'Group': '分组（Control/MCI/AD）',
            'Age': '年龄（岁）【当前为空，需补充】',
            'Sex': '性别（M/F）【当前为空，需补充】',
            'EducationYears': '受教育年限（年）【当前为空，需补充】',
            'MoCA': '蒙特利尔认知评估分数【当前为空，需补充】',
            'MMSE_paper_total': '纸质MMSE总分（满分21分）',
            'VR_MMSE_total': 'VR-MMSE总分（满分21分，与纸质版一致）',
            'VR_MMSE_Q1': 'VR-MMSE任务1得分（时间定向，满分5分）',
            'VR_MMSE_Q2': 'VR-MMSE任务2得分（地点定向，满分5分）',
            'VR_MMSE_Q3': 'VR-MMSE任务3得分（即刻记忆，满分3分）',
            'VR_MMSE_Q4': 'VR-MMSE任务4得分（注意力与计算，满分5分）',
            'VR_MMSE_Q5': 'VR-MMSE任务5得分（延迟回忆，满分3分）',
            'Excluded': '是否被排除（True/False）',
            'ExclusionReason': '排除原因（如适用）'
        }

        for field, desc in field_descriptions.items():
            f.write(f"{field}:\n  {desc}\n\n")

        f.write("3. VR-MMSE评分细则\n")
        f.write("-" * 80 + "\n\n")

        f.write("任务1 - 时间定向 (5分):\n")
        f.write("  年份 (1分) + 季节 (1分) + 月份 (1分) + 星期 (2分)\n\n")

        f.write("任务2 - 地点定向 (5分):\n")
        f.write("  省市区 (2分) + 街道 (1分) + 建筑 (1分) + 楼层 (1分)\n\n")

        f.write("任务3 - 即刻记忆 (3分):\n")
        f.write("  记住三个词，每个1分\n\n")

        f.write("任务4 - 注意力与计算 (5分):\n")
        f.write("  100-7, 93-7, 86-7, 79-7, 72-7，每个1分\n\n")

        f.write("任务5 - 延迟回忆 (3分):\n")
        f.write("  回忆任务3的三个词，每个1分\n\n")

        f.write("4. 数据来源\n")
        f.write("-" * 80 + "\n\n")

        f.write("ParticipantID, Group:\n")
        f.write("  来源: data/normalized_features/subjects.csv\n\n")

        f.write("MMSE分数:\n")
        f.write("  来源: data/MMSE_Score/\n")
        f.write("    - 控制组.csv (Control组)\n")
        f.write("    - 轻度认知障碍组.csv (MCI组)\n")
        f.write("    - 阿尔兹海默症组.csv (AD组)\n\n")

        f.write("Age, Sex, EducationYears, MoCA:\n")
        f.write("  状态: 当前为空，需要从以下来源补充:\n")
        f.write("    - 原始招募记录\n")
        f.write("    - 伦理审查文件\n")
        f.write("    - 临床评估记录\n\n")

        f.write("5. MMSE分数统计\n")
        f.write("-" * 80 + "\n\n")

        for group in ['Control', 'MCI', 'AD']:
            group_df = master_df[master_df['Group'] == group]
            if not group_df['VR_MMSE_total'].isna().all():
                f.write(f"{group}组 (n={len(group_df)}):\n")
                f.write(f"  总分: {group_df['VR_MMSE_total'].mean():.1f} ± {group_df['VR_MMSE_total'].std():.1f}\n")
                f.write(f"  Q1: {group_df['VR_MMSE_Q1'].mean():.1f} ± {group_df['VR_MMSE_Q1'].std():.1f}\n")
                f.write(f"  Q2: {group_df['VR_MMSE_Q2'].mean():.1f} ± {group_df['VR_MMSE_Q2'].std():.1f}\n")
                f.write(f"  Q3: {group_df['VR_MMSE_Q3'].mean():.1f} ± {group_df['VR_MMSE_Q3'].std():.1f}\n")
                f.write(f"  Q4: {group_df['VR_MMSE_Q4'].mean():.1f} ± {group_df['VR_MMSE_Q4'].std():.1f}\n")
                f.write(f"  Q5: {group_df['VR_MMSE_Q5'].mean():.1f} ± {group_df['VR_MMSE_Q5'].std():.1f}\n\n")

        f.write("6. 注意事项\n")
        f.write("-" * 80 + "\n\n")

        f.write("⚠️  MCI组ID转换:\n")
        f.write("   MMSE文件中为大写M (M01-M20)\n")
        f.write("   已统一转换为小写m (m01-m20)\n\n")

        f.write("⚠️  缺失的人口学数据:\n")
        f.write("   Age, Sex, EducationYears, MoCA字段当前为空(NaN)\n")
        f.write("   这些字段对于完整的统计分析是必需的\n")
        f.write("   建议尽快从原始记录中补充\n\n")

        f.write("⚠️  数据使用建议:\n")
        f.write("   - 主分析可使用VR_MMSE_total作为认知评估指标\n")
        f.write("   - VR_MMSE_Q1-Q5可用于task-level分析\n")
        f.write("   - 建议补充人口学数据后再进行协变量调整的分析\n")

    print(f"   ✓ 说明文档已保存到: {readme_file}")

    print("\n" + "=" * 80)
    print("✓ Participants Master表创建完成!")
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

    # 执行创建
    success = create_participants_master(data_dir, output_dir)

    if success:
        print("\n✓ 脚本执行成功!")
        return 0
    else:
        print("\n✗ 脚本执行失败!")
        return 1

if __name__ == '__main__':
    exit(main())
