import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

from LargeEvent import *

class DynamicPlot:
    def __init__(self, truck_list,depot_list, order_list, complete_times, sim_time, consumption):

        self.sim_time = sim_time
        self.table_data = [[["Total Consumption", "0"],
                           ["Standby Consumtion", "0"],
                           ["Orders' Average Waiting", "0"],
                           ["Total Mileage", "0"],
                           ], [["Total Orders", "0"],
                           ["Carbon Emission", "0"],
                           ["Pending Var1", "0"],
                           ["Pengding Var2", "0"],
                           ]]

                                   
        self.truck_list: List[Truck] = truck_list
        self.order_list: List[Order] = order_list
        self.depot_list: List[Depot] = depot_list
        self.complete_times:List[Dict[str, float]] = complete_times
        self.time_cons, self.disp_cons = consumption
        self.lines = []
        self.fps = 24

        self.all_var =[]
        self.variables: Dict[str, float] = {
            "total_cons": None,     #全场总能耗
            "standby_cons": None,   #闲置能耗（排队时的能耗）
            "ave_waiting_time": None,   #每个订单平均等待时间
            "mileage": None,        #所有truck行驶总里程
            "mean_time": 0,          #实时时间（用于检索）
            "truck_in_depot":[],     #每个depot里的truck数量
            "carbon_emission":None,     #碳排放量
            "order_number": 0 ,      #订单总数
            "ave_queue_time": None      #平均排队时间
        }

 

##############计算函数
    def get_history(self):#计算已经完成的车辆的时间能耗
        history_con = 0.0
        for times in self.complete_times:
            active_time = times['to_service_center']
            inpot_time = times['in_depot']
            history_con += self.time_cons * (inpot_time-active_time)
        return history_con

    def get_ing_cons(self, now):#计算正在进行中的时间能耗
        ing_cons = 0.0
        for truck in self.truck_list:
            active_time = truck.times['to_service_center']
            if truck.get_condition() == "serve" or truck.get_condition() == "delivery":
                ing_cons+=(now-active_time) * self.time_cons
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
            active_time = times['to_service_center']
            outpot_time = times['start_delivery']
            standby_cons += self.time_cons * (outpot_time - active_time)
        for truck in self.truck_list:
            active_time = truck.times['to_service_center']

            if truck.get_condition == "serve":
                standby_cons += self.time_cons * (now-active_time)
                
            elif truck.get_condition == "delivery":
                outpot_time = truck.times['start_delivery']
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

    def get_truck_in_depot(self):       #每个depot里的truck数量
        truck_in_depot = []
        for depot in depot_list:
            depot_id = depot.id
            trucks_in_depot = depot.get_truck_instock()
            truck_in_depot[depot_id] = trucks_in_depot

        return truck_in_depot


    def get_order_number(self):
        order_number = len(order_list)
        return order_number



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
        
        # variables = [total_cons, standby_cons, waiting_time, mileage, int(now)]
        return variables

    def initialize_window(self):
        plt.ion()
        self.fig, self.axs = plt.subplots(3, 2, figsize=(10, 8))
        self.fig.subplots_adjust(top=0.85)
        # 设置表格在弹窗中的位置，并设置初始值
        for i in range(2):
            self.axs[0, i].axis('off')
            table = self.axs[0, i].table(cellText=self.table_data[i], loc='center', cellLoc='center')
            table.scale(1, 2)
      

        # 设置图在弹窗中的位置
        colors = ['r-', 'y-', 'b-', 'g-']
        for i in range(2):
            for j in range(2):
                ax = self.axs[i+1 , j]
                # ax.set_xlim(0, self.sim_time)
                index = 2 * i + j  # 计算 self.table_data 的索引
                if index == 0:
                    ax.set_title("Total Consumption", fontsize=8)
                elif index ==1:
                    ax.set_title("Standby Consumtion", fontsize=8)
                elif index ==2:
                    ax.set_title("Orders' Average Waiting", fontsize=8)
                elif index ==3:
                    ax.set_title("Total Mileage", fontsize=8)
                
                # ax.set_title(f'Variable {2 * i + j + 1}')
                line, = ax.plot([], [], colors[2 * i + j])
                self.lines.append(line)

                # 设置 x 坐标为初始值
                x_data = [0]  # 初始 x 坐标
                y_data = [0]  # 初始 y 坐标
                line.set_xdata(x_data)
                line.set_ydata(y_data)
                ax.tick_params(axis='x', labelsize=8)
                ax.tick_params(axis='y', labelsize=8)
        # # 调整子图间距
        # self.fig.subplots_adjust(hspace=0.5)  # 增加垂直间距
        # 显示图表
        plt.show()

       
    def update_graph(self, now):
        # 更新表格数据
        variables = self.get_variables(now)
        for i in range(4):
            self.table_data[0][i][1] = f"{variables[i]:.2f}"
###########################################################################缺少右边数据的更新
        # 更新图表数据

        for i, line in enumerate(self.lines):
            x_data = list(line.get_xdata())
            y_data = list(line.get_ydata())
            x_data.append(variables[4])  # 假设 variables[4] 是新的x值
            y_data.append(variables[i])  # 新的y值
            line.set_xdata(x_data)
            line.set_ydata(y_data)

            # 获取当前线条对应的坐标轴
            ax = self.axs[i // 2 + 1, i % 2]
    
            # 重新计算坐标轴的限制并自动缩放视图
            ax.relim()
            ax.autoscale_view()
            # 更新表格显示
        for i in range(2):
            self.axs[0, i].cla()
            self.axs[0, i].axis('off')
            table = self.axs[0, i].table(cellText=self.table_data[i], loc='center', cellLoc='center')
            table.scale(1, 2)

 

    def draw_graph(self, now):
        
        self.update_graph(now)
        

            
        plt.ioff()
        plt.pause(0.001)  # 使用 plt.draw() 代替 plt.show()

        
