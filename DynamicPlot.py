import matplotlib.pyplot as plt
from LargeEvent import *

class DynamicPlot:
    def __init__(self, truck_list, complete_order_list, sim_time, consumption):

        self.sim_time = sim_time
        self.table_data = [["Total Consumption", "0"],
                           ["Standby Consumtion", "0"],
                           ["Average Waiting Time", "0"],
                           ["Total Mileage", "0"],
                           ["Meantime", "0"]]
                           
        self.truck_list: List[Truck] = truck_list
        self.order_list: List[Order] = complete_order_list
        self.truck_list: List[Truck] = truck_list
        self.time_cons, self.disp_cons = consumption
        self.total_cons = 0.0
        self.standby_cons = 0.0
        self.walking_cons = 0.0
        self.wfridge_cons = 0.0
        self.waiting_time = 0.0
        self.mileage = 0.0
        self.variables = [self.total_cons, self.standby_cons, self.waiting_time, self.mileage, 0.0]

        self.fps = 24
##############计算函数
    def get_variables(self, now):
        self.variables[4] = int(now)
        
        for truck in self.truck_list:
            self.standby_cons = 

################
    def draw_graph(self, now):
        plt.ion()
        fig, axs = plt.subplots(3, 2, figsize=(10, 8))

        # 设置表格在弹窗中的位置，并设置初始值
        for i in range(2):
            axs[0, i].axis('off')
            table = axs[0, i].table(cellText=self.table_data, loc='center', cellLoc='center')
            table.scale(1, 2)

        # 设置图表在弹窗中的位置
        lines = []
        colors = ['r-', 'y-', 'b-', 'g-']
        for i in range(2):
            for j in range(2):
                ax = axs[i + 1, j]
                ax.set_xlim(0, self.sim_time)
                ax.set_title(f'Variable {2 * i + j + 1}')
                line, = ax.plot([], [], colors[2 * i + j])
                lines.append(line)


                # 设置 x 坐标为 self.get_time
                x_data = [0]  # 初始 x 坐标
                y_data = [0]  # 初始 y 坐标
                line.set_xdata(x_data)
                line.set_ydata(y_data)
        # 显示图表
        plt.show()

        while now < self.sim_time:
            plt.pause(1/self.fps)

            # 更新表格数据
            variables = self.get_variables()
            for i in range(4):
                self.table_data[i][1] = f"{variables[i]:.2f}"

            # 更新图表数据
            for i, line in enumerate(lines):
                x_data = list(line.get_xdata())
                y_data = list(line.get_ydata())
#这里有get_time()
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

# if __name__ == "__main__":
#     # 示例用法
#     def get_time():
#         return 0.1  #