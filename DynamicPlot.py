import matplotlib.pyplot as plt

class DynamicPlot:
    def __init__(self,  truck_list, complete_order_list, sim_time, consumption):

        self.sim_time = sim_time
        self.table_data = [["Total Consumption", "0"],
                           ["Standby Consumtion", "0"],
                           ["Average Waiting Time", "0"],
                           ["Total Mileage", "0"]]
        self.truck_list = truck_list
        self.order_list = complete_order_list
        self.consumption = consumption
        
    def draw_table_and_graph(self, now):
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
                ax.set_title(f'Variable {2 * i + j + 1}')
                line, = ax.plot([], [], 'r-')
                lines.append(line)


                # 设置 x 坐标为 self.get_time
                x_data = [now]  # 初始 x 坐标
                y_data = [0]  # 初始 y 坐标
                line.set_xdata(x_data)
                line.set_ydata(y_data)
        # 显示图表
        plt.show()

        while now < self.sim_time:
            plt.pause(1)

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

                # 自动调整图表的显示范围
                ax = axs[i // 2 + 1, i % 2]
                ax.relim()
                ax.autoscale_view()

            # 更新表格显示
            for i in range(2):
                axs[0, i].cla()
                axs[0, i].axis('off')
                table = axs[0, i].table(cellText=self.table_data, loc='center', cellLoc='center')
                table.scale(1, 2)

        plt.ioff()
        plt.show()

if __name__ == "__main__":
    # 示例用法
    def get_time():
        return 0.1  #