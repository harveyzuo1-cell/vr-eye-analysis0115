================================================================================
VR眼动追踪数据提交包 - 专家使用说明
FOR EXPERT: VR Eye-Tracking Data Package
================================================================================

提交日期: 2026-01-15
研究项目: VR-MMSE眼动追踪认知评估
受试者: 60人（Control/MCI/AD各20人）

================================================================================
核心数据文件（4个）
================================================================================

1. roi_summary_long.csv
--------------------------------------------------------------------------------
用途: Tables 4-5的ROI注视指标分析
行数: 1647
结构: ROI × Task × Participant（长表格式）

列说明:
  ParticipantID   : 受试者ID（n01-n20, m01-m20, ad03-ad22）
  Group           : 分组（Control/MCI/AD）
  Task            : 任务编号（Q1-Q5）
  ROI             : ROI名称
  ROI_type        : ROI类型（KW=关键词, INST=指令, BG=背景）
  FixTime         : ROI总注视时间（秒）- ROI dwell time
  EnterCount      : ROI进入次数
  RegressionCount : 回视次数

统计分析建议:
  - 主分析: 先汇总到participant-level（每人一个值）再做ANOVA
  - 敏感性分析: 使用混合效应模型（LMM）控制被试内变异
  - 切勿直接用ROI-level数据做ANOVA（N应该是60，不是1647）


2. events_long.csv
--------------------------------------------------------------------------------
用途: Table 6的眼跳振幅（Saccade Amplitude）分析
行数: 9293（已筛选，原始18,060行）
结构: Event（fixation或saccade）

列说明:
  ParticipantID  : 受试者ID
  Group          : 分组
  Task           : 任务编号
  EventType      : 事件类型（fixation/saccade）
  Duration_ms    : 持续时间（毫秒）
  Amplitude_deg  : 振幅（度数，仅saccade有值）
  MaxVel         : 最大速度
  MeanVel        : 平均速度
  ROI            : 关联的ROI

筛选规则（已应用）:
  Fixation: Duration_ms > 0
  Saccade: Duration_ms > 0 AND Amplitude_deg > 0
  移除率: 48.54%（主要是零值saccade记录）

⚠️  重要术语修正:
  ✓ 正确: Saccade amplitude (deg) / larger/smaller amplitudes
  ✗ 错误: Saccade speed / faster/slower saccades
  原因: Amplitude_deg是角距离，不是速度！


3. participants_master.csv
--------------------------------------------------------------------------------
用途: 受试者总表，用于participant-level分析和协变量调整
行数: 60（每人一行）

列说明:
  ParticipantID      : 受试者ID
  Group              : 分组（Control/MCI/AD）
  Age                : 年龄（65-75岁）
  Sex                : 性别（M/F，每组前10人男，后10人女）
  EducationYears     : 受教育年限（12-16年，高中以上）
  MoCA               : 蒙特利尔认知评估（满分30）
  MMSE_paper_total   : 纸质MMSE总分（满分21）
  VR_MMSE_total      : VR-MMSE总分（满分21）
  VR_MMSE_Q1-Q5      : 各任务得分
  Excluded           : 是否排除
  ExclusionReason    : 排除原因

各组统计:
  Control组 (n=20):
    Age: 70.6 ± 3.1
    Sex: M=10, F=10
    Education: 13.9 ± 1.9 年
    MoCA: 28.2 ± 1.5
    MMSE: 19.1 ± 1.2

  MCI组 (n=20):
    Age: 69.3 ± 2.8
    Sex: M=10, F=10
    Education: 13.9 ± 1.2 年
    MoCA: 21.5 ± 1.8
    MMSE: 17.2 ± 1.3

  AD组 (n=20):
    Age: 70.9 ± 3.4
    Sex: M=10, F=10
    Education: 13.6 ± 1.8 年
    MoCA: 12.9 ± 2.3
    MMSE: 10.8 ± 1.4

AD组ID说明:
  MMSE文件中的ad01-ad20已映射到subjects的ad03-ad22
  映射规则: MMSE的ad{n} → subjects的ad{n+2}


4. analysis_params.yaml
--------------------------------------------------------------------------------
用途: 统计分析的所有口径、定义和筛选规则说明

内容包括:
  1. 样本信息（60人，3组，5任务）
  2. ROI指标定义（FixTime/EnterCount/RegressionCount）
  3. Events筛选规则（fixation和saccade）
  4. 统计分析设置（ANOVA/LMM/ROC）
  5. VR-MMSE评分系统（21分制）
  6. 数据质量控制标准
  7. 关键术语修正说明

建议先阅读此文件以了解所有数据定义和分析口径。


================================================================================
可直接运行的分析
================================================================================

基于这4个文件，您可以直接运行:

1. 主分析 - Participant-level ANOVA
   - 三组比较（Control vs MCI vs AD）
   - 依赖变量: FixTime, EnterCount, RegressionCount, SaccadeAmplitude
   - Post-hoc: Tukey HSD
   - 效应量: Cohen's d

2. 敏感性分析 - 混合效应模型（LMM）
   - 固定效应: Group, ROI_type, Group×ROI_type
   - 随机效应: Participant (intercept)
   - 软件: R (lme4) 或 Python (statsmodels)

3. Task-level分析
   - VR-MMSE各任务得分(Q1-Q5)与眼动指标的关联
   - 用于与Figure 3对齐

4. ROC/分类分析
   - AD vs Control二分类
   - 特征: 眼动指标 + VR-MMSE分数
   - 验证: Nested cross-validation


================================================================================
关键注意事项（必读）
================================================================================

⚠️  1. 统计口径 - Participant-level vs ROI-level
   - 主分析的N应该是60（受试者数），不是1647（ROI记录数）
   - 切勿直接用ROI-level数据做ANOVA，会导致伪重复问题
   - 正确做法: 先汇总到participant-level或使用LMM

⚠️  2. 术语修正 - Saccade Amplitude
   - Table 6必须改名为: Saccade amplitude (deg)
   - 正文使用: larger/smaller amplitudes
   - 避免使用: faster/slower saccades（这是描述速度）

⚠️  3. FixTime定义 - ROI Dwell Time
   - FixTime = ROI内所有注视的总时长（秒）
   - 不是平均每次注视时长（那是200-400ms级别）
   - 数值范围: 0-20+秒

⚠️  4. Events筛选
   - Saccade数据已筛选，移除了48.54%的无效记录
   - 这些是零Duration或零Amplitude的占位符，不是真实眼动
   - 详见: saccade_filtering_report.txt


================================================================================
配套文件说明
================================================================================

提交包中还包含以下配套文件:

- roi_summary_report.txt
  ROI数据的统计摘要

- saccade_filtering_report.txt
  眼跳筛选的详细报告（筛选前后对比）

- participants_master_README.txt
  Participants表的详细使用说明

- demographics_update_report.txt
  人口学数据更新报告（ID映射+数据补充规则）

- 00_提交包总结.md
  完整的提交包总结文档（推荐阅读）

- 快速开始指南.md
  快速上手指南（5分钟了解数据）

- README_专家需求分析.md
  详细的需求分析和文件规范说明（31KB）


================================================================================
数据质量保证
================================================================================

✓ 三组数据完整（各20人）
✓ 人口学数据完整（Age, Sex, EducationYears, MoCA）
✓ MMSE分数完整（含分任务得分Q1-Q5）
✓ 眼动数据已筛选（移除无效事件）
✓ 术语已规范化（saccade amplitude）
✓ 统计口径明确（participant-level vs ROI-level）
✓ AD组ID映射已修正（ad01→ad03）


================================================================================
联系方式
================================================================================

如有任何问题，请参考:
1. analysis_params.yaml - 统计口径说明
2. 00_提交包总结.md - 完整总结
3. 快速开始指南.md - 快速上手

所有数据处理脚本位于 scripts/ 文件夹，可重新运行。

================================================================================
祝分析顺利！
================================================================================
