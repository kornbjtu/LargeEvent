import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 从Excel文件加载数据
df = pd.read_excel('data.xlsx')

# 假设'a'列包含y轴的值，'Name'列包含类别标签
y = df['a']
x = df['Name']

# 如果需要，计算置信区间；这里使用占位符值
confidence_intervals = [(70, 90), (60, 80), (50, 70), (40, 60)]

# 创建图形和轴对象
fig, ax = plt.subplots()

# 创建带置信区间的箱形图
parts = ax.boxplot(y, positions=np.arange(len(confidence_intervals)), notch=True)

# 如果需要，手动添加置信区间上下限；相应调整位置
for i in range(len(confidence_intervals)):
    conf_int = confidence_intervals[i]
    ax.plot([i+1,i+1], conf_int,'-', color='purple')

plt.xticks(np.arange(1, len(x)+1), x)
plt.show()
