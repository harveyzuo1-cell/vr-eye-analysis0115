# Figure 3 重绘脚本（R语言）
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
cat("\n统计摘要：\n")
print(data %>%
  group_by(Group) %>%
  summarise(
    Mean_Amplitude = mean(Mean_Amplitude_deg),
    SD_Amplitude = sd(Mean_Amplitude_deg)
  ))
