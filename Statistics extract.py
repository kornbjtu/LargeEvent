import csv
import os

# 获取脚本所在的文件夹路径
csv_folder = os.path.dirname(os.path.abspath(__file__))
# 要导出结果的新CSV文件路径
output_csv = os.path.join(csv_folder, 'output.csv')

# 准备存储结果的列表
results = []

# 遍历100个CSV文件
for i in range(1, 101):
    filename = f'output_scenario_1_seed_{i}.csv'
    file_path = os.path.join(csv_folder, filename)
    with open(file_path, newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        
        # 跳过前36行
        for _ in range(36000):
            next(csvreader)
        
        # 读取第37行
        row = next(csvreader)
        
        # 获取第1列的值
        value = row[0]
        
        # 添加文件名和值到结果列表
        results.append([value])

# 将结果写入新的CSV文件
with open(output_csv, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    # 写入表头
    csvwriter.writerow(['Value'])
    # 写入数据
    csvwriter.writerows(results)

print(f'Results have been written to {output_csv}')