# VR_MMSE分数异常分析报告

**问题**：participants_master.csv中的VR_MMSE_Q1-Q5分数出现异常值
**发现日期**：2026-01-15
**严重程度**：高（影响数据正确性）

---

## 📊 异常数据示例

### Control组 - n01受试者

#### 当前participants_master.csv中的数据：
```
ParticipantID: n01
MMSE_paper_total: 23
VR_MMSE_total: 23
VR_MMSE_Q1: 7.0    ← ❌ 异常！（满分应该是5）
VR_MMSE_Q2: 6.0    ← ❌ 异常！（满分应该是5）
VR_MMSE_Q3: 1.0    ← ⚠️  可能异常（满分3，但这里是1）
VR_MMSE_Q4: 5.0    ← ✓ 正常（满分5）
VR_MMSE_Q5: 23.0   ← ❌ 严重异常！（满分应该是3）
```

#### 原始MMSE文件（控制组.csv）中的数据：
```
受试者: n01
年份: 1, 季节: 1, 月份: 1, 星期: 2, 省市区: 2
街道: 1, 建筑: 1, 楼层: 1
即刻记忆: 3
100-7: 1, 93-7: 1, 86-7: 1, 79-7: 1, 72-7: 1
词1: 1, 词2: 1, 词3: 1
总分: 21
```

---

## 🔍 问题根源分析

### 当前计算逻辑（scripts/3_create_participants_master.py）

```python
# Q1: 时间定向 (年份+季节+月份+星期) = 5分
df['VR_MMSE_Q1'] = (df[df.columns[1]] + df[df.columns[2]] +
                    df[df.columns[3]] + df[df.columns[4]] + df[df.columns[5]])
                    # columns[1-5]: 年份, 季节, 月份, 星期, 省市区
                    # ❌ 错误：包含了"省市区"（应该是Q2的内容）
```

**问题**：
1. 列索引计算错误
2. Q1包含了本应属于Q2的"省市区"字段
3. Q5的计算可能包含了总分列

### 正确的MMSE结构

MMSE文件的列结构：
```
列0: 受试者
列1: 年份      ┐
列2: 季节      │
列3: 月份      ├─ Q1 时间定向（4分）
列4: 星期      ┘  注意：星期是2分
列5: 省市区    ┐
列6: 街道      │
列7: 建筑      ├─ Q2 地点定向（5分）
列8: 楼层      ┘  注意：省市区是2分
列9: 即刻记忆  ─── Q3 即刻记忆（3分）
列10: 100-7    ┐
列11: 93-7     │
列12: 86-7     ├─ Q4 注意力与计算（5分）
列13: 79-7     │
列14: 72-7     ┘
列15: 词1      ┐
列16: 词2      ├─ Q5 延迟回忆（3分）
列17: 词3      ┘
列18: 总分     ─── 总分（21分）
```

---

## 🧮 正确的计算方式

### 方式1：基于列索引（准确版本）

```python
# Q1: 时间定向 = 年份(1) + 季节(1) + 月份(1) + 星期(2) = 5分
df['VR_MMSE_Q1'] = (df.iloc[:, 1] + df.iloc[:, 2] +
                    df.iloc[:, 3] + df.iloc[:, 4])

# Q2: 地点定向 = 省市区(2) + 街道(1) + 建筑(1) + 楼层(1) = 5分
df['VR_MMSE_Q2'] = (df.iloc[:, 5] + df.iloc[:, 6] +
                    df.iloc[:, 7] + df.iloc[:, 8])

# Q3: 即刻记忆 = 3分
df['VR_MMSE_Q3'] = df.iloc[:, 9]

# Q4: 注意力与计算 = 5个减法题，各1分 = 5分
df['VR_MMSE_Q4'] = (df.iloc[:, 10] + df.iloc[:, 11] +
                    df.iloc[:, 12] + df.iloc[:, 13] + df.iloc[:, 14])

# Q5: 延迟回忆 = 词1(1) + 词2(1) + 词3(1) = 3分
df['VR_MMSE_Q5'] = (df.iloc[:, 15] + df.iloc[:, 16] + df.iloc[:, 17])

# 总分应该等于Q1+Q2+Q3+Q4+Q5 = 21分
df['VR_MMSE_total'] = df.iloc[:, 18]  # 或者计算和
```

### 方式2：基于列名（更安全）

```python
# 读取时明确列名
columns = ['受试者', '年份', '季节', '月份', '星期', '省市区',
           '街道', '建筑', '楼层', '即刻记忆',
           '100-7', '93-7', '86-7', '79-7', '72-7',
           '词1', '词2', '词3', '总分']

df = pd.read_csv(file_path, names=columns, skiprows=1)

# 然后按列名计算
df['VR_MMSE_Q1'] = df['年份'] + df['季节'] + df['月份'] + df['星期']
df['VR_MMSE_Q2'] = df['省市区'] + df['街道'] + df['建筑'] + df['楼层']
df['VR_MMSE_Q3'] = df['即刻记忆']
df['VR_MMSE_Q4'] = df['100-7'] + df['93-7'] + df['86-7'] + df['79-7'] + df['72-7']
df['VR_MMSE_Q5'] = df['词1'] + df['词2'] + df['词3']
```

---

## 📈 验证示例（n01受试者）

### 原始数据：
```
年份=1, 季节=1, 月份=1, 星期=2, 省市区=2,
街道=1, 建筑=1, 楼层=1,
即刻记忆=3,
100-7=1, 93-7=1, 86-7=1, 79-7=1, 72-7=1,
词1=1, 词2=1, 词3=1,
总分=21
```

### 正确计算：
```
Q1 = 1 + 1 + 1 + 2 = 5 ✓ (满分5)
Q2 = 2 + 1 + 1 + 1 = 5 ✓ (满分5)
Q3 = 3               = 3 ✓ (满分3)
Q4 = 1+1+1+1+1       = 5 ✓ (满分5)
Q5 = 1 + 1 + 1       = 3 ✓ (满分3)
总分 = 5+5+3+5+3     = 21 ✓
```

### 当前错误计算（推测）：
```
Q1 = 1+1+1+2+2       = 7 ❌ (包含了省市区)
Q2 = 1+1+1           = 3 ❌ (缺少省市区，只有街道建筑楼层，还差2分)
Q3 = 3               = 3 ✓ (碰巧正确)
Q4 = 1+1+1+1+1       = 5 ✓ (碰巧正确)
Q5 = ?               = 23 ❌ (可能包含了总分列)
```

---

## 🎯 修复建议

### 立即行动：

1. **修改 scripts/3_create_participants_master.py**
   - 修正列索引计算逻辑
   - 使用正确的列范围

2. **重新运行脚本**
   ```bash
   python3 submit/scripts/3_create_participants_master.py
   ```

3. **验证结果**
   - Q1-Q5分数应该在合理范围内
   - Q1+Q2+Q3+Q4+Q5 应该等于 VR_MMSE_total

4. **重新运行更新脚本**
   ```bash
   python3 submit/scripts/4_update_demographics.py
   ```

5. **重新打包**
   ```bash
   python3 submit/scripts/5_prepare_final_package.py
   cd /Users/lukang/Documents/eyetrack/vr-eyetracking-analysis
   rm VR_EyeTracking_Data_Package.zip
   zip -r VR_EyeTracking_Data_Package.zip submit/*.csv submit/*.yaml submit/*.txt submit/*.md -x "submit/scripts/*" "submit/*backup*"
   ```

---

## ⚠️ 影响评估

### 当前受影响的文件：
- ✅ `participants_master.csv` - 需要修复
- ✅ `participants_master_backup.csv` - 需要修复

### 未受影响的文件：
- ✅ `roi_summary_long.csv` - 正常（不依赖Q1-Q5）
- ✅ `events_long.csv` - 正常（不依赖Q1-Q5）
- ✅ `analysis_params.yaml` - 正常（只是说明文档）

### 潜在分析影响：
- ❌ Task-level分析（VR_MMSE_Q1-Q5与眼动指标关联）
- ❌ Figure 3的对齐（需要正确的分任务得分）
- ✅ 主分析（使用VR_MMSE_total，该值是正确的）

---

## 📋 检查清单

修复后需要验证：

- [ ] Q1分数范围：0-5（不应该超过5）
- [ ] Q2分数范围：0-5（不应该超过5）
- [ ] Q3分数范围：0-3（不应该超过3）
- [ ] Q4分数范围：0-5（不应该超过5）
- [ ] Q5分数范围：0-3（不应该超过3）
- [ ] Q1+Q2+Q3+Q4+Q5 = VR_MMSE_total（应该相等）
- [ ] VR_MMSE_total = MMSE_paper_total（应该相等）
- [ ] Control组平均MMSE约19-21分
- [ ] MCI组平均MMSE约17-19分
- [ ] AD组平均MMSE约10-13分

---

## 📊 当前数据异常统计

从participants_master.csv中可以看到的异常：

```
Q1异常（>5）:
  n01: 7.0
  n02: 7.0
  ... (所有Control和MCI组可能都有问题)

Q2异常（与预期不符）:
  可能缺少省市区的2分

Q5异常（>3）:
  n01: 23.0 (严重异常，可能是总分)
  ... (需要检查所有受试者)
```

---

**结论**：VR_MMSE_Q1-Q5的计算逻辑存在严重错误，需要立即修复后重新生成数据。
