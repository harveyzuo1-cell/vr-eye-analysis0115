================================================================================
Figure 3 重绘源数据与脚本说明
================================================================================

目的：
与Table 6统一术语，将"Saccade speed"修正为"Saccade amplitude (deg)"

修正要点：
--------------------------------------------------------------------------------
1. ❌ 错误术语：Saccade speed / faster/slower saccades
2. ✅ 正确术语：Saccade amplitude (deg) / larger/smaller amplitudes
3. Y轴标签：Mean Saccade Amplitude (deg)
4. 图注说明：使用amplitude而非speed

文件清单：
--------------------------------------------------------------------------------
1. figure3_data_participant_task_level.csv
   - Participant-Task级别数据（N=60×5=300行）
   - 用于统计分析和验证

2. figure3_data_group_task_level.csv
   - Group-Task级别数据（3组×5任务=15行）
   - 用于直接绘图（含均值和标准误）

3. figure3_plot_script.R
   - R语言绘图脚本（使用ggplot2）
   - 生成PDF和PNG格式

4. figure3_plot_script.py
   - Python绘图脚本（使用matplotlib）
   - 生成PDF和PNG格式

使用方法：
--------------------------------------------------------------------------------
R语言用户：
  cd submit
  Rscript figure3_plot_script.R

Python用户：
  cd submit
  python3 figure3_plot_script.py

数据说明：
--------------------------------------------------------------------------------
- Amplitude_deg：眼跳的角距离（度数），范围通常0-10度
- 计算方法：从events_long.csv中筛选EventType='saccade'的记录
- 汇总层级：先按participant-task计算均值，再按group-task计算组均值
- 误差棒：使用标准误（SEM = SD / sqrt(N)）

与原Figure 3的区别：
--------------------------------------------------------------------------------
1. 术语修正：amplitude替代speed
2. 单位明确：(deg)角度
3. 数据来源可追溯：基于events_long.csv
4. 统计口径一致：与Table 6使用相同指标

================================================================================
