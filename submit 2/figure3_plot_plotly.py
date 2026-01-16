#!/usr/bin/env python3
"""
Figure 3 重绘脚本 - Plotly版本（更美观的可视化）
修正术语：使用 "Saccade Amplitude (deg)" 而非 "speed"
颜色方案：Control=绿色, MCI=黄色, AD=红色
日期：2026-01-15
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 读取数据
data = pd.read_csv('figure3_data_group_task_level.csv')

# 确保顺序
data['Group'] = pd.Categorical(data['Group'],
                                categories=['Control', 'MCI', 'AD'],
                                ordered=True)
data['Task'] = pd.Categorical(data['Task'],
                               categories=['Q1', 'Q2', 'Q3', 'Q4', 'Q5'],
                               ordered=True)
data = data.sort_values(['Group', 'Task'])

# 创建图表
fig = go.Figure()

# 定义颜色方案（Control=绿色, MCI=黄色, AD=红色）
colors = {
    'Control': '#2E7D32',  # 深绿色
    'MCI': '#FFA726',      # 橙黄色（比纯黄色更好看）
    'AD': '#D32F2F'        # 深红色
}

# 定义标记样式
markers = {
    'Control': 'circle',
    'MCI': 'square',
    'AD': 'triangle-up'
}

# 为每个组添加轨迹
for group in ['Control', 'MCI', 'AD']:
    group_data = data[data['Group'] == group].copy()

    fig.add_trace(go.Scatter(
        x=group_data['Task'].astype(str),
        y=group_data['Mean_Amplitude_deg'],
        name=group,
        mode='lines+markers',
        line=dict(
            color=colors[group],
            width=3,
            shape='spline',  # 平滑曲线
        ),
        marker=dict(
            color=colors[group],
            size=12,
            symbol=markers[group],
            line=dict(color='white', width=2)  # 白色边框
        ),
        error_y=dict(
            type='data',
            array=group_data['SEM_Amplitude_deg'],
            visible=True,
            color=colors[group],
            thickness=2,
            width=6
        ),
        hovertemplate=(
            '<b>%{fullData.name}</b><br>' +
            'Task: %{x}<br>' +
            'Mean Amplitude: %{y:.2f} deg<br>' +
            'SEM: ±%{error_y.array:.2f} deg<br>' +
            '<extra></extra>'
        )
    ))

# 更新布局
fig.update_layout(
    title=dict(
        text='<b>Saccade Amplitude Across VR-MMSE Tasks</b>',
        x=0.5,
        xanchor='center',
        font=dict(size=20, family='Arial, sans-serif')
    ),
    xaxis=dict(
        title=dict(text='<b>VR-MMSE Task</b>', font=dict(size=16, family='Arial, sans-serif')),
        tickfont=dict(size=14),
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(200, 200, 200, 0.3)',
        zeroline=False
    ),
    yaxis=dict(
        title=dict(text='<b>Mean Saccade Amplitude (deg)</b>', font=dict(size=16, family='Arial, sans-serif')),
        tickfont=dict(size=14),
        showgrid=True,
        gridwidth=1,
        gridcolor='rgba(200, 200, 200, 0.3)',
        zeroline=False
    ),
    legend=dict(
        title=dict(text='<b>Group</b>', font=dict(size=14)),
        font=dict(size=13),
        orientation='v',
        yanchor='top',
        y=0.98,
        xanchor='right',
        x=0.98,
        bgcolor='rgba(255, 255, 255, 0.9)',
        bordercolor='rgba(0, 0, 0, 0.3)',
        borderwidth=1
    ),
    plot_bgcolor='white',
    paper_bgcolor='white',
    width=1000,
    height=600,
    hovermode='closest',
    font=dict(family='Arial, sans-serif')
)

# 保存为静态图片（高分辨率）
print("正在生成Figure 3（Plotly版本）...")

# 保存为PNG（高分辨率）
try:
    fig.write_image('Figure3_Saccade_Amplitude_Plotly.png',
                    width=1200, height=800, scale=3)
    print("✓ 已生成: Figure3_Saccade_Amplitude_Plotly.png (3600x2400, 高分辨率)")
except Exception as e:
    print(f"⚠ PNG保存失败: {e}")
    print("  提示: 需要安装kaleido: pip install kaleido")

# 保存为PDF（矢量格式）
try:
    fig.write_image('Figure3_Saccade_Amplitude_Plotly.pdf',
                    width=1200, height=800)
    print("✓ 已生成: Figure3_Saccade_Amplitude_Plotly.pdf (矢量格式)")
except Exception as e:
    print(f"⚠ PDF保存失败: {e}")

# 保存为交互式HTML（可在浏览器中查看）
fig.write_html('Figure3_Saccade_Amplitude_Plotly.html',
               include_plotlyjs='cdn')
print("✓ 已生成: Figure3_Saccade_Amplitude_Plotly.html (交互式版本)")

# 打印统计摘要
print("\n" + "="*60)
print("统计摘要：")
print("="*60)
summary = data.groupby('Group', observed=True)['Mean_Amplitude_deg'].agg(['mean', 'std', 'count'])
summary.columns = ['均值 (deg)', '标准差 (deg)', '任务数']
print(summary.to_string())

print("\n颜色方案：")
print(f"  Control (对照组): 绿色 {colors['Control']}")
print(f"  MCI (轻度认知障碍): 橙黄色 {colors['MCI']}")
print(f"  AD (阿尔兹海默症): 红色 {colors['AD']}")

print("\n" + "="*60)
print("✓ Figure 3 (Plotly版本) 生成完成！")
print("="*60)
