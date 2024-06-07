import matplotlib.pyplot as plt
import numpy as np
import time

class DynamicPlot:
    def __init__(self, get_time, get_variables, sim_time):
        self.get_time = get_time
        self.get_variables = get_variables
        self.sim_time = sim_time
        self.table_data = [["Variable 1", "0"],
                           ["Variable 2", "0"],
                           ["Variable 3", "0"],
                           ["Variable 4", "0"]]

    def draw_table_and_graph(self):
        plt.ion()
        fig, axs = plt.subplots(3, 2, figsize=(10, 8))

        # 表格设置在第一行的两个子图中
        for i in range(2):
            axs[0, i].axis('off')
            table = axs[0, i].table(cellText=self.table_data, loc='center', cellLoc='center')
            table.scale(1, 2)

        # 图表设置在后面的两行中
        lines = []
        for i in range(2):
            for j in range(2):
                ax = axs[i + 1, j]
                ax.set_xlim(0, self.sim_time)
                ax.set_ylim(0, 1)
                ax.set_title(f'Variable {2 * i + j + 1}')
                line, = ax.plot([], [], 'r-')
                lines.append(line)

        # 显示图表
        plt.show()

        while self.get_time() < self.sim_time:
            plt.pause(0.1)

            # 更新表格数据
            variables = self.get_variables()
            for i in range(4):
                self.table_data[i][1] = f"{variables[i]:.2f}"

            # 更新图表数据
            for i, line in enumerate(lines):
                x_data = list(line.get_xdata())
                y_data = list(line.get_ydata())
                x_data.append(self.get_time())
                y_data.append(variables[i])
                line.set_xdata(x_data)
                line.set_ydata(y_data)
                axs[i // 2 + 1, i % 2].relim()
                axs[i // 2 + 1, i % 2].autoscale_view()

            # 更新表格显示
            for i in range(2):
                axs[0, i].cla()
                axs[0, i].axis('off')
                table = axs[0, i].table(cellText=self.table_data, loc='center', cellLoc='center')
                table.scale(1, 2)

        plt.ioff()
        plt.show()
