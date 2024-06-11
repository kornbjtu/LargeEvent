import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

from LargeEvent import *

class DynamicPlot:
    def __init__(self, truck_list, order_list, complete_times, sim_time, consumption):

        self.sim_time = sim_time
        self.table_data = [["Total Consumption", "0"],
                           ["Standby Consumtion", "0"],
                           ["Average Waiting Time", "0"],
                           ["Total Mileage", "0"],
                           ["Meantime", "0"]]
                           
        self.truck_list: List[Truck] = truck_list
        self.order_list: List[Order] = order_list
        self.complete_times:List[Dict[str, float]] = complete_times
        self.time_cons, self.disp_cons = consumption

        self.fps = 24
##############计算函数
    def get_history(self):#计算已经完成的车辆的时间能耗
        history_con = 0.0
        for times in self.complete_times:
            active_time = times['start_deliveery']
            inpot_time = times['to_service_center']
            history_con += self.time_cons * (inpot_time-active_time)
        return history_con

    def get_ing_cons(self, now):#计算正在进行中的时间能耗
        ing_cons = 0.0
        for truck in self.truck_list:
            
            if truck.get_condition() == "serve" or truck.get_condition() == "delivery":
                ing_cons+=(now-truck.times['start_delivery']) * self.time_cons
        return ing_cons
    
    def get_dis_cons(self): #计算距离能耗
        dis_cons = 0.0
        for truck in self.truck_list:
            mile = truck.get_mile()
            dis_cons += self.disp_cons * mile
        return dis_cons
    
    def get_standby_cons(self, now):#计算总闲置能耗
        standby_cons = 0.0
        for times in self.complete_times:
            active_time = times['start_delivery']
            outpot_time = times['to_service_center']
            standby_cons += self.time_cons * (outpot_time - active_time)
        for truck in self.truck_list:
            active_time = truck.times['start_delivery']

            if truck.get_condition == "serve":
                standby_cons += self.time_cons * (now-active_time)
            elif truck.get_condition == "delivery":
                outpot_time = truck.times['to_service_center']
                standby_cons += self.time_cons * (outpot_time-active_time)
        return standby_cons
    
    def get_ave_waiting_time(self):#计算已经完成的订单的平均等待的时间
        waiting_time = 0.0
        num = 0
        ave_waiting_time = 0.0
        for order in self.order_list:
            if order.is_complete == True:
                waiting_time += order.complete_time - order.generation_time
                num+=1
            if num>0:
                ave_waiting_time = waiting_time/num
        return ave_waiting_time

    def get_mile(self):#计算总里程
        mile = 0.0
        for truck in self.truck_list:
            mile += truck.get_mile()
        return mile

    def get_variables(self, now):

        history_cons = self.get_history()
        ing_cons = self.get_ing_cons(now)
        dis_cons = self.get_dis_cons()
        standby_cons = self.get_standby_cons(now)
        ave_waiting_time = self.get_ave_waiting_time()
        mile = self.get_mile()
        total_cons = history_cons + ing_cons + dis_cons
        standby_cons = standby_cons
        waiting_time = ave_waiting_time
        mileage = mile
        variables = [total_cons, standby_cons, waiting_time, mileage, int(now)]
        return variables


        
################
    def draw_graph(self, now):
        plt.ion()
        fig, axs = plt.subplots(3, 2, figsize=(10, 8))

        # 设置表格在弹窗中的位置，并设置初始值
        for i in range(2):
            axs[0, i].axis('off')
            table = axs[0, i].table(cellText=self.table_data, loc='center', cellLoc='center')
            table.scale(1, 2)

        # 设置图在弹窗中的位置
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
        screen_width = fig.canvas.manager.window.winfo_screenwidth()
        screen_height = fig.canvas.manager.window.winfo_screenheight()
        window_width = fig.canvas.manager.window.winfo_width()
        window_height = fig.canvas.manager.window.winfo_height()

        # 计算窗口在右下角时的位置
        x_position = screen_width - window_width
        y_position = screen_height - window_height

        # 移动窗口
        fig.canvas.manager.window.wm_geometry(f"+{x_position}+{y_position}")


        while now < self.sim_time:
            plt.pause(1/self.fps)

            # 更新表格数据
            variables = self.get_variables(now)
            for i in range(4):
                self.table_data[i][1] = f"{variables[i]:.2f}"

            # 更新图表数据
            for i, line in enumerate(lines):
                x_data = list(line.get_xdata())
                y_data = list(line.get_ydata())
                x_data.append(variables[4])
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