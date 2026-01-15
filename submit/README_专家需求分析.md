# VR眼动追踪数据提交包 - 专家需求分析

## 文档概述

本文档详细分析了数据分析专家的需求，并说明了为满足DADM（Dementia and Alzheimer's Disease Medicine）期刊投稿要求所需准备的数据文件和说明文档。

**目标**：完成三组对比（Control vs MCI vs AD）的统计分析、ROC曲线、混合效应模型，并重建Tables 4-6。

**当前日期**：2026-01-15

---

## 一、核心需求概述

专家要求提供以下文件才能完成完整的统计分析：

### 1.1 必须补齐的核心文件

| 文件类型 | 用途 | 状态 |
|---------|------|------|
| ROI Summary（三组） | Tables 4-5的三组ANOVA/混合模型 | ✅ 已有 |
| Events（三组） | Table 6 + 眼跳振幅分析 | ✅ 已有 |
| Participants Master Sheet | 60人总表（人口学+MMSE） | ⚠️ 需整合 |
| 统计口径说明（analysis_params） | 明确指标定义和筛选规则 | ⚠️ 需创建 |

### 1.2 强烈建议准备的补充材料

| 文件类型 | 用途 | 优先级 |
|---------|------|--------|
| ROI字典 | 解释每个ROI对应的文本内容 | 高 |
| 质量控制QC表 | 数据质量指标和排除标准 | 高 |
| 建模用特征宽表 | ROC/分类模型的participant-level特征 | 中 |

---

## 二、数据文件详细需求

### 2.1 ROI Summary数据

#### 当前状态
项目中已有三组分离的ROI Summary文件：

```
data/event_analysis_results/
├── control_All_ROI_Summary.csv  (541行, n01-n20)
├── mci_All_ROI_Summary.csv      (568行, m01-m20)
└── ad_All_ROI_Summary.csv       (541行, ad03-ad22)
```

#### 专家要求

**方案A：三份独立文件（当前已满足）**
- AD_All_Folders_ROI_Summary.csv
- MCI_All_Folders_ROI_Summary.csv
- Control_All_Folders_ROI_Summary.csv

**方案B：合并长表（推荐，需创建）**

创建 `roi_summary_long.csv`，包含以下字段：

| 字段名 | 说明 | 示例值 |
|-------|------|--------|
| ParticipantID | 受试者ID | ad3, m10, n7 |
| Group | 分组 | AD, MCI, Control |
| Task | 任务编号 | Q1, Q2, Q3, Q4, Q5 |
| ROI | ROI名称 | KW_n2q1_1, INST_n2q1_1, BG_n2q1 |
| ROI_type | ROI类型 | KW, INST, BG |
| FixTime_s | 注视时间（秒） | 2.569 |
| EnterCount | 进入次数 | 4 |
| RegressionCount | 回视次数 | 3 |

**关键改进**：
- 将 `ADQ_ID` (如 n1q1) 拆分为 `ParticipantID` (n1) 和 `Task` (Q1)
- 明确添加 `ROI_type` 列（从ROI名称前缀解析）
- 确保Group列统一格式（Control/MCI/AD）

#### 专家关注的统计问题

> **伪重复问题**：当前 All_Folders_ROI_Summary.csv 有540行（20人×27 ROI），这是ROI-level的N，不能直接用于组间比较。

**解决方案**：
- 主分析使用participant-level汇总（每人一行）
- 混合效应模型使用ROI-level数据，但需正确设置随机效应结构

---

### 2.2 Events数据

#### 当前状态
项目中已有三组分离的Events文件：

```
data/event_analysis_results/
├── control_All_Events.csv  (2,879行)
├── mci_All_Events.csv      (6,821行)
└── ad_All_Events.csv       (8,363行)
总计：18,061行眼动事件
```

#### 专家要求

创建 `events_long.csv` 合并长表，包含以下字段：

| 字段名 | 说明 | 示例值 |
|-------|------|--------|
| ParticipantID | 受试者ID | ad3, m10, n7 |
| Group | 分组 | AD, MCI, Control |
| Task | 任务编号 | Q1, Q2, Q3, Q4, Q5 |
| EventType | 事件类型 | fixation, saccade |
| Duration_ms | 持续时间（毫秒） | 253.0 |
| Amplitude_deg | 振幅（度数） | 2.48 |
| MaxVel | 最大速度 | 40.35 |
| MeanVel | 平均速度 | 40.35 |
| ROI | 关联的ROI | KW_n2q1_1（fixation有值，saccade可能为空） |

#### 关键术语修正（非常重要）

**Table 6 必须修改**：
- ❌ 错误：Saccade speed / faster/slower saccades
- ✅ 正确：**Saccade amplitude (deg)** / larger/smaller amplitudes

**原因**：
- Amplitude_deg 是"眼跳的角距离"，单位是度（degrees）
- 不是速度（velocity），虽然数据中也有MaxVel和MeanVel字段
- 文章必须使用正确的术语避免审稿人质疑

#### 数据质量问题（非常重要）

**专家警告**：
> Events数据中可能存在大量 `Duration_ms=0` 且 `Amplitude_deg=0` 的无效saccade记录。

**当前数据验证**（从示例看）：
```
行17: saccade, Duration=0.0, Amplitude=0.0
行18: saccade, Duration=0.0, Amplitude=0.0
行19: saccade, Duration=0.0, Amplitude=0.0
行20: saccade, Duration=0.0, Amplitude=0.0
```

**必须提供的筛选规则**（见第三部分 analysis_params）

---

### 2.3 Participants Master Sheet（最关键）

#### 为什么这是最重要的文件？

专家原话：
> "没有这个master sheet，就无法直接跑出：AUC、nested CV、系数/OR、CI，以及把统计口径从ROI/task正确收敛到participant-level。"

#### 需要创建的文件

`participants_master.csv`（每人1行，共60行）

**必需字段**：

| 字段名 | 说明 | 数据来源 | 示例值 |
|-------|------|---------|--------|
| ParticipantID | 受试者ID | subjects.csv | ad3, m10, n7 |
| Group | 分组 | subjects.csv | AD, MCI, Control |
| Age | 年龄 | ⚠️ 缺失，需补充 | 68 |
| Sex | 性别 | ⚠️ 缺失，需补充 | M, F |
| EducationYears | 受教育年限 | ⚠️ 缺失，需补充 | 12 |
| MoCA | 蒙特利尔认知评估 | ⚠️ 用于分组标准 | 26 |
| MMSE_paper_total | 纸质MMSE总分 | MMSE_Score/*.csv | 19 |
| VR_MMSE_total | VR-MMSE总分 | ⚠️ 需说明21分版 | 19 |

**强烈建议添加**：

| 字段名 | 说明 | 用途 |
|-------|------|------|
| VR_MMSE_Q1 | VR-MMSE任务1得分 | 与Figure 3的task-level建模对齐 |
| VR_MMSE_Q2 | VR-MMSE任务2得分 | 同上 |
| VR_MMSE_Q3 | VR-MMSE任务3得分 | 同上 |
| VR_MMSE_Q4 | VR-MMSE任务4得分 | 同上 |
| VR_MMSE_Q5 | VR-MMSE任务5得分 | 同上 |
| Excluded | 是否被排除 | 敏感性分析 |
| ExclusionReason | 排除原因 | 从72→60的说明 |

#### 当前数据缺失情况

**✅ 已有数据**：
- ParticipantID：`data/normalized_features/subjects.csv`（60人）
- Group：同上
- MMSE_paper_total：`data/MMSE_Score/`下三个CSV文件
  - 控制组.csv（n01-n20，平均19.1分）
  - 轻度认知障碍组.csv（m01-m20，平均17.3分）
  - 阿尔兹海默症组.csv（ad01-ad20，平均10.9分）

**⚠️ 缺失数据**：
- Age（年龄）
- Sex（性别）
- EducationYears（受教育年限）
- MoCA（蒙特利尔认知评估分数）
- VR_MMSE分任务得分（Q1-Q5）
- Excluded/ExclusionReason

**注意**：MMSE文件中的受试者ID需要对齐：
- 控制组：n01-n20（与subjects.csv一致）
- MCI组：M01-M20（需转换为小写m01-m20）
- AD组：ad01-ad20（subjects.csv是ad03-ad22，需核对）

---

## 三、统计口径说明文档（analysis_params）

### 3.1 为什么需要这个文档？

专家原话：
> "为了把'伪重复 / df不匹配 / 统计口径混乱'一次性根治，需要一个1页说明或analysis_params.yaml固定规则。"

### 3.2 必须澄清的问题

#### 问题1：FixTime_s的定义

**当前数据观察**：
- FixTime_s 数值范围：0.122秒 到 20+秒
- 数值特征：秒级，远大于典型注视持续时间（200-400ms）

**可能的定义**：
1. **ROI总注视时间**（sum of fixation durations in ROI）← 更可能
2. **ROI平均注视时间**（mean fixation duration in ROI）

**需要明确**：
- [ ] FixTime_s是"ROI内所有注视的总时长"还是"平均每次注视时长"？
- [ ] Tables 4-5使用什么汇总方式？
  - 方案A：每人5个task的均值（task-weighted）← 推荐
  - 方案B：直接在ROI-level取均值（会给某些task更多ROI的人过多权重）

**建议术语**：
- 如果是总时长：`ROI dwell time (s)` 或 `Total fixation time within ROI (s)`
- 如果是平均时长：`Mean fixation duration in ROI (ms)`

#### 问题2：Saccade有效事件筛选规则

**专家要求的术语修正**：
- Table 6改名：~~"Saccade speed"~~ → **"Saccade amplitude (deg)"**
- 正文描述：~~"faster/slower"~~ → **"larger/smaller amplitudes"**

**筛选规则建议**：

```yaml
saccade_filtering:
  inclusion_criteria:
    - EventType == "saccade"
    - Duration_ms > 0  # 剔除0-duration记录
    - Amplitude_deg > 0  # 剔除无效振幅
  optional_filters:
    - Amplitude_deg < 30  # 合理上限（可选）
    - Apply winsorization at 1st and 99th percentile  # 稳健处理（可选）
```

**需要报告的指标**：
- 筛选前后的saccade事件数（按组统计）
- 每人每task平均有效saccade数
- 证明"组间差异不是因为某组事件更少"

### 3.3 建议的analysis_params.yaml结构

```yaml
# VR眼动追踪数据分析参数
version: "1.0"
date: "2026-01-15"

# 1. 样本信息
sample:
  total_participants: 60
  groups:
    - name: "Control"
      n: 20
      id_prefix: "n"
      id_range: "n01-n20"
    - name: "MCI"
      n: 20
      id_prefix: "m"
      id_range: "m01-m20"
    - name: "AD"
      n: 20
      id_prefix: "ad"
      id_range: "ad03-ad22"

  tasks:
    total: 5
    names: ["Q1", "Q2", "Q3", "Q4", "Q5"]
    max_duration_seconds: 180

# 2. ROI指标定义
roi_metrics:
  FixTime_s:
    full_name: "ROI dwell time"
    definition: "Sum of all fixation durations within the ROI"
    unit: "seconds"
    aggregation_method: "task-weighted mean"
    notes: "Each participant's value is the mean across 5 tasks"

  EnterCount:
    full_name: "ROI entry count"
    definition: "Number of times the gaze entered the ROI"
    unit: "count"
    aggregation_method: "task-weighted mean"

  RegressionCount:
    full_name: "Regression count"
    definition: "Number of times the gaze returned to a previously viewed ROI"
    unit: "count"
    aggregation_method: "task-weighted mean"

# 3. Events筛选规则
event_filtering:
  fixation:
    criteria:
      - "EventType == 'fixation'"
      - "Duration_ms > 0"
    notes: "All fixations with positive duration are retained"

  saccade:
    criteria:
      - "EventType == 'saccade'"
      - "Duration_ms > 0"
      - "Amplitude_deg > 0"
    optional_filters:
      - "Amplitude_deg < 30 (physiological upper limit)"
    terminology:
      metric_name: "Saccade amplitude"
      unit: "degrees of visual angle"
      correct_terms: ["larger amplitudes", "smaller amplitudes"]
      incorrect_terms: ["faster saccades", "slower saccades"]
    notes: "Zero-duration and zero-amplitude saccades are artifacts and must be excluded"

# 4. 统计分析设置
statistical_analysis:
  primary_analysis:
    level: "participant"
    method: "One-way ANOVA (Group: Control/MCI/AD)"
    post_hoc: "Tukey HSD or Bonferroni"
    effect_size: "Cohen's d or partial η²"
    confidence_interval: 0.95

  sensitivity_analysis:
    level: "ROI or task"
    method: "Linear mixed-effects model"
    random_effects: "Participant (intercept), Task (if applicable)"
    fixed_effects: "Group, ROI_type"

  model_validation:
    method: "nested cross-validation"
    outer_folds: 5
    inner_folds: 5
    metrics: ["AUC", "Sensitivity", "Specificity", "Accuracy"]
    bootstrap_ci: 1000

# 5. ROI分类
roi_types:
  KW:
    full_name: "Keyword ROI"
    description: "关键词区域（任务相关的目标词汇）"
  INST:
    full_name: "Instruction ROI"
    description: "指令区域（任务说明文字）"
  BG:
    full_name: "Background ROI"
    description: "背景区域（非任务相关区域）"

# 6. 数据质量控制
quality_control:
  calibration_error_threshold: "< 2 degrees"
  minimum_valid_fixations_per_task: 5
  minimum_valid_saccades_per_task: 3
  data_loss_threshold: "< 20%"
  exclusion_criteria:
    - "Calibration failure (error > 2 deg)"
    - "Excessive data loss (> 20%)"
    - "Task non-completion (< 3 tasks completed)"
```

---

## 四、ROI字典（roi_dictionary.csv）

### 4.1 为什么需要ROI字典？

专家原话：
> "让你在Discussion里解释'关键词区/指令区/背景区'的差异时更有证据支撑，而不是抽象的'task-relevant'描述。"

### 4.2 ROI字典结构

| 字段名 | 说明 | 示例值 |
|-------|------|--------|
| Task | 任务编号 | Q1, Q2, Q3, Q4, Q5 |
| ROI | ROI名称 | KW_n2q1_1, INST_n2q1_1, BG_n2q1 |
| ROI_type | ROI类型 | KW, INST, BG |
| DisplayText_CN | 中文显示文本 | "年份", "请回答当前的年份" |
| DisplayText_EN | 英文翻译（可选） | "Year", "Please answer the current year" |
| ROI_segment_index | ROI片段索引 | 1, 2, 3, 4 |
| Semantic_importance | 语义重要性 | high, medium, low |

### 4.3 任务-ROI映射

基于VR-MMSE的5个任务：

**Q1 - 时间定向（5分）**
- KW: "年份", "季节", "月份", "星期"
- INST: "请回答当前的年份/季节/月份/星期"
- BG: 背景环境

**Q2 - 地点定向（5分）**
- KW: "省", "市", "区", "街道", "建筑", "楼层"
- INST: "请说出当前所在的省份/城市/..."
- BG: 背景环境

**Q3 - 即刻记忆（3分）**
- KW: 三个记忆词（需从数据中提取）
- INST: "请记住以下三个词"
- BG: 背景环境

**Q4 - 注意力与计算（5分）**
- KW: "100-7", "93-7", "86-7", "79-7", "72-7"
- INST: "请从100开始，每次减7"
- BG: 背景环境

**Q5 - 延迟回忆（3分）**
- KW: "词1", "词2", "词3"（与Q3相同）
- INST: "请回忆之前记住的三个词"
- BG: 背景环境

**⚠️ 需要从实际VR界面或任务设计文档中获取准确的DisplayText**

---

## 五、质量控制表（eye_tracking_qc.csv）

### 5.1 为什么需要QC表？

专家原话：
> "DADM常看重质量控制。能让你在Limitations中把'设备/耐受性/数据丢失'说得更精确，防止审稿人怀疑'组间差异来自数据质量差异'。"

### 5.2 QC表结构

**方案A：每人×每任务一行（推荐）**

| 字段名 | 说明 | 示例值 |
|-------|------|--------|
| ParticipantID | 受试者ID | ad3 |
| Group | 分组 | AD |
| Task | 任务 | Q1 |
| CalibrationError_deg | 校准误差（度） | 0.8 |
| DataLoss_percentage | 数据丢失率 | 5.2 |
| TrackingConfidence_mean | 平均追踪置信度 | 0.92 |
| n_fixations_total | 总注视数 | 45 |
| n_saccades_total | 总眼跳数 | 38 |
| n_saccades_valid | 有效眼跳数（筛选后） | 32 |
| TaskDuration_s | 任务时长 | 145 |
| TaskCompleted | 是否完成 | TRUE |
| ExclusionFlag | 排除标记 | FALSE |
| ExclusionReason | 排除原因 | NA |

**方案B：每人一行（汇总版）**

| 字段名 | 说明 |
|-------|------|
| ParticipantID | 受试者ID |
| Group | 分组 |
| CalibrationError_deg_mean | 平均校准误差 |
| DataLoss_percentage_mean | 平均数据丢失率 |
| n_fixations_total | 所有任务总注视数 |
| n_saccades_valid_total | 所有任务有效眼跳数 |
| TasksCompleted | 完成的任务数（最多5个） |
| OverallQuality | 整体质量评级（Good/Fair/Poor） |
| Excluded | 是否排除 |
| ExclusionReason | 排除原因 |

### 5.3 需要从现有数据中提取的信息

**可能的数据源**：
1. 校准误差：可能在原始数据或校准日志中
2. 数据丢失率：从calibrated vs processed数据对比计算
3. 注视/眼跳数：从Events文件统计
4. 任务时长：从game_sessions.csv中的game_duration_seconds

**需要验证**：
- [ ] 原始数据中是否有校准误差记录？
- [ ] 如何定义"数据丢失"？（缺失帧数/总帧数？）
- [ ] 有没有tracking confidence字段？

---

## 六、建模用特征宽表（model_features_participant.csv）

### 6.1 用途

专家原话：
> "如果你还想把ROC/分类升级到'可投DADM的证据等级'，需要建模用宽表。"

### 6.2 宽表结构

**每人一行，共60行**

| 字段类别 | 字段名 | 说明 |
|---------|-------|------|
| **基本信息** | ParticipantID | 受试者ID |
|  | Group | 分组 |
|  | Label_binary | 二分类标签（AD=1, Control=0） |
|  | Label_ternary | 三分类标签（AD=2, MCI=1, Control=0） |
| **人口学** | Age | 年龄 |
|  | Sex_encoded | 性别（0=F, 1=M） |
|  | EducationYears | 受教育年限 |
| **认知评估** | MoCA | 蒙特利尔认知评估 |
|  | MMSE_paper | 纸质MMSE总分 |
|  | VR_MMSE_total | VR-MMSE总分 |
|  | VR_MMSE_Q1 to Q5 | 各任务得分 |
| **ROI特征** | FixTime_KW_mean | KW区域平均注视时间 |
|  | FixTime_INST_mean | INST区域平均注视时间 |
|  | FixTime_BG_mean | BG区域平均注视时间 |
|  | EnterCount_KW_mean | KW区域平均进入次数 |
|  | EnterCount_INST_mean | INST区域平均进入次数 |
|  | EnterCount_BG_mean | BG区域平均进入次数 |
|  | RegressionCount_KW_mean | KW区域平均回视次数 |
|  | RegressionCount_INST_mean | INST区域平均回视次数 |
|  | RegressionCount_BG_mean | BG区域平均回视次数 |
| **Saccade特征** | SaccadeAmplitude_mean | 平均眼跳振幅 |
|  | SaccadeAmplitude_sd | 眼跳振幅标准差 |
|  | SaccadeAmplitude_median | 眼跳振幅中位数 |
| **RQA特征** | RR_2D_xy_mean | 2D递归率 |
|  | DET_2D_xy_mean | 2D确定性 |
|  | ENT_2D_xy_mean | 2D熵 |
|  | RR_1D_x_mean | 1D递归率 |
|  | DET_1D_x_mean | 1D确定性 |
|  | ENT_1D_x_mean | 1D熵 |

### 6.3 特征工程说明

**标准化方式**：
- 在nested CV的训练折内进行z-score标准化
- 避免数据泄露

**特征选择**：
- 可使用LASSO或递归特征消除（RFE）
- 报告最终模型使用的特征子集

---

## 七、文件清单与交付要求

### 7.1 最小可运行包（必须提供）

| 序号 | 文件名 | 描述 | 优先级 |
|-----|--------|------|--------|
| 1 | `roi_summary_long.csv` | 三组ROI汇总（合并长表） | P0 |
| 2 | `events_long.csv` | 三组眼动事件（合并长表） | P0 |
| 3 | `participants_master.csv` | 60人总表（人口学+MMSE） | P0 |
| 4 | `analysis_params.yaml` | 统计口径说明文档 | P0 |

### 7.2 强烈建议提供（显著提升质量）

| 序号 | 文件名 | 描述 | 优先级 |
|-----|--------|------|--------|
| 5 | `roi_dictionary.csv` | ROI字典（ROI→文本映射） | P1 |
| 6 | `eye_tracking_qc.csv` | 质量控制表 | P1 |
| 7 | `model_features_participant.csv` | 建模用特征宽表 | P2 |
| 8 | `README_数据说明.md` | 数据文件使用说明 | P1 |

### 7.3 可选补充材料

| 序号 | 文件名 | 描述 |
|-----|--------|------|
| 9 | `saccade_filtering_report.txt` | 眼跳筛选前后统计 |
| 10 | `exclusion_flowchart.pdf` | 受试者排除流程图 |
| 11 | `data_quality_summary.pdf` | 数据质量可视化报告 |

---

## 八、当前项目数据映射

### 8.1 已有数据文件（可直接使用或稍作整理）

| 需求文件 | 现有文件 | 状态 |
|---------|---------|------|
| ROI Summary（三组） | `data/event_analysis_results/control_All_ROI_Summary.csv` | ✅ 可用 |
|  | `data/event_analysis_results/mci_All_ROI_Summary.csv` | ✅ 可用 |
|  | `data/event_analysis_results/ad_All_ROI_Summary.csv` | ✅ 可用 |
| Events（三组） | `data/event_analysis_results/control_All_Events.csv` | ✅ 可用 |
|  | `data/event_analysis_results/mci_All_Events.csv` | ✅ 可用 |
|  | `data/event_analysis_results/ad_All_Events.csv` | ✅ 可用 |
| 受试者分组 | `data/normalized_features/subjects.csv` | ✅ 可用 |
| MMSE分数 | `data/MMSE_Score/控制组.csv` | ✅ 可用 |
|  | `data/MMSE_Score/轻度认知障碍组.csv` | ✅ 可用 |
|  | `data/MMSE_Score/阿尔兹海默症组.csv` | ✅ 可用 |
| 游戏会话 | `data/normalized_features/game_sessions.csv` | ✅ 可用 |

### 8.2 需要创建的文件

| 文件名 | 创建方式 | 数据来源 |
|-------|---------|---------|
| `roi_summary_long.csv` | Python脚本合并 | control/mci/ad_All_ROI_Summary.csv |
| `events_long.csv` | Python脚本合并+筛选 | control/mci/ad_All_Events.csv |
| `participants_master.csv` | 手动整合+脚本 | subjects.csv + MMSE_Score/*.csv + 需补充人口学数据 |
| `analysis_params.yaml` | 手动创建 | 根据本文档规范 |
| `roi_dictionary.csv` | 手动创建 | 需要VR任务设计文档 |
| `eye_tracking_qc.csv` | Python脚本提取 | Events, game_sessions, 原始数据 |
| `model_features_participant.csv` | Python脚本聚合 | roi_summary_long + events_long + participants_master |

### 8.3 需要补充收集的数据

| 数据项 | 状态 | 建议 |
|-------|------|------|
| 年龄（Age） | ❌ 缺失 | 从原始招募记录或伦理文件中获取 |
| 性别（Sex） | ❌ 缺失 | 同上 |
| 受教育年限（EducationYears） | ❌ 缺失 | 同上 |
| MoCA分数 | ❌ 缺失 | 如果用MoCA分组，必须提供 |
| VR-MMSE分任务得分 | ❌ 缺失 | 从VR系统日志中提取，或从MMSE_Score文件计算 |
| ROI显示文本 | ❌ 缺失 | 从VR任务设计文档或代码中提取 |
| 校准误差 | ⚠️ 可能在原始数据 | 检查calibrated文件或日志 |
| 数据丢失率 | ⚠️ 需计算 | 对比原始vs处理后数据 |

---

## 九、术语标准化建议

### 9.1 ROI相关术语

| 原始术语 | 推荐术语（英文） | 中文 |
|---------|---------------|------|
| FixTime | ROI dwell time / Total fixation time within ROI | ROI总注视时间 |
| EnterCount | ROI entry count | ROI进入次数 |
| RegressionCount | Regression count / Re-fixation count | 回视次数 |

### 9.2 Events相关术语

| 原始术语 | 推荐术语（英文） | 中文 | 单位 |
|---------|---------------|------|------|
| Duration_ms | Fixation duration / Saccade duration | 注视/眼跳持续时间 | milliseconds |
| Amplitude_deg | Saccade amplitude | 眼跳振幅 | degrees of visual angle |
| MaxVel / MeanVel | Peak / Mean velocity | 峰值/平均速度 | deg/s |

**❌ 避免使用**：
- "Saccade speed"（应该用amplitude或velocity）
- "faster/slower saccades"（应该用larger/smaller amplitudes或higher/lower velocities）

### 9.3 统计分析术语

| 分析层级 | 术语 | 说明 |
|---------|------|------|
| Participant-level | 主分析 | N=60（20人/组），每人一个汇总值 |
| ROI-level | 敏感性分析 | 混合效应模型，随机效应控制被试内变异 |
| Task-level | 探索性分析 | 与VR-MMSE任务得分对齐 |

---

## 十、数据处理脚本需求

### 10.1 脚本1：ROI Summary合并

**输入**：
- `control_All_ROI_Summary.csv`
- `mci_All_ROI_Summary.csv`
- `ad_All_ROI_Summary.csv`

**输出**：
- `roi_summary_long.csv`

**处理步骤**：
1. 读取三个文件
2. 统一Group列格式（control/mci/ad → Control/MCI/AD）
3. 从ADQ_ID拆分ParticipantID和Task（n1q1 → n1, Q1）
4. 从ROI名称解析ROI_type（KW_/INST_/BG_前缀）
5. 合并并排序
6. 验证：总行数应为 541+568+541=1650 左右

### 10.2 脚本2：Events合并与筛选

**输入**：
- `control_All_Events.csv`
- `mci_All_Events.csv`
- `ad_All_Events.csv`

**输出**：
- `events_long.csv`
- `saccade_filtering_report.txt`

**处理步骤**：
1. 合并三个文件
2. 拆分ADQ_ID为ParticipantID和Task
3. 应用筛选规则：
   - Fixation: Duration_ms > 0
   - Saccade: Duration_ms > 0 AND Amplitude_deg > 0
4. 统计筛选前后的事件数（按组、按人）
5. 生成筛选报告

### 10.3 脚本3：Participants Master整合

**输入**：
- `subjects.csv`
- `MMSE_Score/控制组.csv`
- `MMSE_Score/轻度认知障碍组.csv`
- `MMSE_Score/阿尔兹海默症组.csv`
- 手动补充的人口学数据（CSV或Excel）

**输出**：
- `participants_master.csv`

**处理步骤**：
1. 从subjects.csv读取ParticipantID和Group
2. 从MMSE文件读取各题得分和总分
3. 处理ID不一致问题（M01→m01, ad01-ad20→ad03-ad22）
4. 合并人口学数据
5. 验证：应有60行，无缺失值（或标记为NA）

### 10.4 脚本4：质量控制表生成

**输入**：
- `events_long.csv`
- `game_sessions.csv`
- 可选：原始数据中的校准日志

**输出**：
- `eye_tracking_qc.csv`

**处理步骤**：
1. 统计每人每任务的注视/眼跳数
2. 计算有效眼跳比例
3. 从game_sessions提取任务时长
4. 标记异常值（如极少事件数、极短任务时长）

### 10.5 脚本5：建模特征宽表

**输入**：
- `roi_summary_long.csv`
- `events_long.csv`
- `participants_master.csv`
- 可选：`rqa_features.csv`

**输出**：
- `model_features_participant.csv`

**处理步骤**：
1. 按ParticipantID分组汇总ROI指标（按ROI_type）
2. 计算saccade amplitude的均值、标准差、中位数
3. 合并RQA特征
4. 合并人口学和认知评估数据
5. 创建标签（二分类、三分类）
6. 验证：60行 × 约40-50列

---

## 十一、关键检查清单

### 11.1 数据完整性检查

- [ ] 三组各20人，共60人（无重复、无遗漏）
- [ ] ParticipantID在所有文件中一致
- [ ] Group标签统一（Control/MCI/AD）
- [ ] 每人有5个任务的数据（Q1-Q5）
- [ ] MMSE总分在合理范围（Control: 18-21, MCI: 15-19, AD: 9-13）

### 11.2 数据质量检查

- [ ] 无异常的FixTime值（如负数、超过180秒）
- [ ] Saccade筛选后仍有足够事件（每人每任务≥3个）
- [ ] 无缺失的ROI_type（所有ROI都能解析为KW/INST/BG）
- [ ] Events中的ROI名称与ROI_Summary中的ROI匹配

### 11.3 术语一致性检查

- [ ] 所有文档和表格使用"Saccade amplitude (deg)"而非"speed"
- [ ] FixTime明确定义为"总时间"或"平均时间"
- [ ] Group标签格式统一（首字母大写）

### 11.4 统计分析准备检查

- [ ] analysis_params.yaml明确了所有指标定义
- [ ] 筛选规则有明确的纳入/排除标准
- [ ] 汇总方法（task-weighted）在文档中说明
- [ ] 随机效应结构在混合模型部分说明

---

## 十二、时间线与优先级

### 12.1 第一阶段：核心文件（1-2天）

**P0优先级**：
1. 创建 `roi_summary_long.csv`（脚本1）
2. 创建 `events_long.csv` + 筛选报告（脚本2）
3. 整合 `participants_master.csv`（需补充人口学数据）
4. 编写 `analysis_params.yaml`

**交付物**：最小可运行包（4个文件）

### 12.2 第二阶段：补充材料（2-3天）

**P1优先级**：
5. 创建 `roi_dictionary.csv`（需VR任务文档）
6. 生成 `eye_tracking_qc.csv`（脚本4）
7. 编写 `README_数据说明.md`

**交付物**：完整提交包（7-8个文件）

### 12.3 第三阶段：建模准备（1-2天）

**P2优先级**：
8. 生成 `model_features_participant.csv`（脚本5）
9. 可选：筛选报告、可视化等

**交付物**：可用于机器学习建模的完整数据集

---

## 十三、常见问题解答

### Q1：为什么不能直接用All_ROI_Summary.csv？

**A**：因为该文件是ROI-level的数据（N=1650行），直接做ANOVA会导致"伪重复"问题（pseudoreplication），即把同一个人的多个ROI当作独立样本，虚增自由度。正确的做法是：
- 主分析：先汇总到participant-level（N=60）
- 敏感性：用混合效应模型控制被试内相关性

### Q2：MMSE文件中的ID不一致怎么办？

**A**：需要创建映射规则：
- 控制组：n01-n20（一致，无需处理）
- MCI组：M01-M20（大写）→ m01-m20（小写）
- AD组：ad01-ad20 → ad03-ad22（编号偏移+2，需仔细核对）

### Q3：如果缺失的人口学数据无法补充怎么办？

**A**：
- 最低要求：保证ParticipantID、Group、MMSE分数完整
- 建议：在participants_master.csv中标记缺失字段为NA，并在README中说明
- 影响：无Age/Sex/Education会影响协变量分析，但不影响基本的组间比较

### Q4：Saccade的0值记录是什么原因？

**A**：可能是：
1. 算法识别的噪声点（非真实眼跳）
2. 数据格式占位符（某些处理流程的中间产物）
3. 阈值下的微小移动（被标记为saccade但实际是drift）

**解决**：必须在筛选规则中剔除，并在QC报告中说明剔除比例。

### Q5：VR-MMSE总分是21分还是30分？

**A**：从现有MMSE文件看：
- 题目结构：5部分（时间定向5分+地点定向5分+即刻记忆3分+计算5分+延迟回忆3分）= 21分
- 实际总分：Control平均19.1分，符合21分制
- 需要确认：VR版本是否与纸质版完全一致，或有改编

**建议**：在analysis_params中明确说明使用的是21分版。

---

## 十四、专家原话摘录（重要提醒）

> "你这套events里，saccade行很可能存在大量Duration_ms=0（并伴随Amplitude_deg=0）的'无效/占位'记录。为了让结果可解释、可复现，建议你同时提供一份明确的筛选规则。"

> "没有这个master sheet，就无法'直接跑出'你希望的：AUC、nested CV、系数/OR、CI，以及把统计口径从ROI/task正确收敛到participant-level。"

> "Table 6改名：'Saccade amplitude (deg)'。正文描述：larger/smaller amplitudes（不要写faster/slower）。"

> "把这四项整理齐，我就可以按你指定的'participant-level主分析 + mixed model敏感性分析'把Tables 4–6、以及与Figure 3对齐的task-level mixed model结果一次性跑出来并给出可直接替换进正文的文本。"

---

## 十五、下一步行动

### 立即行动（今天）
1. ✅ 创建submit文件夹
2. ✅ 创建本README文档
3. ⬜ 运行脚本1：合并ROI Summary
4. ⬜ 运行脚本2：合并Events并筛选

### 短期行动（本周）
5. ⬜ 收集/补充人口学数据（Age, Sex, EducationYears）
6. ⬜ 整合participants_master.csv
7. ⬜ 编写analysis_params.yaml
8. ⬜ 创建ROI字典（需VR任务文档）

### 中期行动（下周）
9. ⬜ 生成quality control表
10. ⬜ 生成建模特征宽表
11. ⬜ 验证所有文件的一致性
12. ⬜ 打包提交给专家

---

## 附录A：目录结构

```
vr-eyetracking-analysis/
├── submit/                              # 提交包文件夹
│   ├── README_专家需求分析.md            # 本文档
│   ├── README_数据说明.md                # 数据使用说明（待创建）
│   ├── roi_summary_long.csv             # ROI汇总（合并长表）
│   ├── events_long.csv                  # 眼动事件（合并长表）
│   ├── participants_master.csv          # 60人总表
│   ├── analysis_params.yaml             # 统计口径说明
│   ├── roi_dictionary.csv               # ROI字典
│   ├── eye_tracking_qc.csv              # 质量控制表
│   ├── model_features_participant.csv   # 建模特征宽表
│   ├── saccade_filtering_report.txt     # 眼跳筛选报告
│   └── scripts/                         # 数据处理脚本
│       ├── 1_merge_roi_summary.py
│       ├── 2_merge_events.py
│       ├── 3_create_participants_master.py
│       ├── 4_generate_qc.py
│       └── 5_create_features_wide.py
└── data/                                # 原始数据（不动）
    ├── event_analysis_results/
    ├── MMSE_Score/
    └── normalized_features/
```

---

## 附录B：参考资料

### 相关论文
- MMSE评分标准（Folstein et al., 1975）
- VR眼动追踪在认知评估中的应用（综述）
- 混合效应模型在重复测量数据中的应用

### 统计软件
- R: lme4包（混合效应模型）, pROC包（ROC曲线）
- Python: statsmodels, scikit-learn, seaborn

### DADM投稿指南
- 数据可用性要求
- 统计报告规范（效应量、CI、exact p值）
- 伦理声明要求

---

**文档版本**：v1.0
**创建日期**：2026-01-15
**最后更新**：2026-01-15
**作者**：Claude Code
**状态**：草稿（待用户确认后定稿）
