import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

from LargeEvent import *

class DynamicPlot:
    def __init__(self, truck_list,depot_list, order_list, complete_times, sim_time, consumption):

        self.sim_time = sim_time
        self.table_data = [[["Total Consumption/kwh", "0"],
                           ["Standby Consumtion/kwh", "0"],
                           ["Orders' Average Waiting/s", "0"],
                           ["Total Mileage/km", "0"],], 

                           [["Total Orders", "0"],
                           ["Carbon Emission/kg", "0"],
                           ["Trucks' Average Queue Time", "0"],
                           ["Total Queue Length", "0"],
                           ]]

                                   
        self.truck_list: List[Truck] = truck_list
        self.order_list: List[Order] = order_list
        self.depot_list: List[Depot] = depot_list
        self.complete_times:List[Dict[str, float]] = complete_times
        self.time_cons, self.disp_cons = consumption

        self.fps = 24
        self.lines = []
        self.all_var =[]
        self.variables: Dict[str, float] = {
            "total_cons": 0.0,     #全场总能耗
            "standby_cons": 0.0,   #闲置能耗（排队时的能耗）
            "ave_waiting_time": 0.0,   #每个订单平均等待时间
            "mileage": 0.0,        #所有truck行驶总里程
            "mean_time": 0,          #实时时间（用于检索）
            "truck_in_depot":[],     #每个depot里的truck数量
            "carbon_emission":0.0,     #碳排放量
            "order_number": 0 ,      #订单总数
            "ave_queue_time": 0.0,      #平均排队时间
            "total_queue_length": 0     #所有depot的排队总长
        }


    def clear_variables(self):
        for key in self.variables:
            if key == "mean_time" or key == "order_number":
                self.variables[key]=0
            elif key == "truck_in_depot":
                self.variables[key] = []
            else:
                self.variables[key] = 0.0

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
        for depot in self.depot_list:
            depot_id = depot.id
            dptr_list = depot.get_truck_instock()
            truck_num = len(dptr_list)
            truck_in_depot.append((depot_id, truck_num))

        return truck_in_depot


    def get_order_number(self):
        order_number = len(self.order_list)
        return order_number

    def get_total_queue_length(self):
        length = 0
        for depot in self.depot_list:
            length += depot.service_center.serve_queue.length()
        return length

    def get_variables(self, now):

        # variables=[]   
        self.clear_variables()

        history_cons = self.get_history()
        ing_cons = self.get_ing_cons(now)
        dis_cons = self.get_dis_cons()
        standby_cons = self.get_standby_cons(now)
        ave_waiting_time = self.get_ave_waiting_time()
        truck_in_depot = []
        truck_in_depot = self.get_truck_in_depot()
        order_number = self.get_order_number()
        mile = self.get_mile()
        emission = (history_cons + ing_cons + dis_cons)*0.268
        queue_length = self.get_total_queue_length()

        self.variables["total_cons"] = history_cons + ing_cons + dis_cons
        self.variables["standby_cons"] = standby_cons
        self.variables["ave_waiting_time"] = ave_waiting_time
        self.variables["mileage"] = mile
        self.variables["mean_time"] = now
        self.variables["truck_in_depot"] = truck_in_depot
        self.variables["order_number"] = order_number
        self.variables["carbon_emission"] = emission
        self.variables["total_queue_length"] = queue_length
        self.all_var.append(self.variables)

        
        # variables = [total_cons, standby_cons, waiting_time, mileage, int(now)]
        # return variables
    def take_var(self, time:int):
        for variables in self.all_var:
            if time == variables["mean_time"]:
                return variables
            else:
                print("Fail taking out variables!!!")
                return None


    def initialize_window(self):
        plt.ion()
        self.fig, self.axs = plt.subplots(3, 2, figsize=(10, 8))
        self.fig.subplots_adjust(top=0.99, hspace=0.25, wspace=0.3)
        # 设置表格在弹窗中的位置，并设置初始值
        for i in range(2):
            self.axs[0, i].axis('off')
            table = self.axs[0, i].table(cellText=self.table_data[i], loc='center', cellLoc='center')
            table.scale(1, 2)
      
     
        colors = ['r-', 'y-', 'b-', 'g-', 'r-', 'b-', 'g-', 'k-']  # 每个子图的颜色
        for i in range(2):
            for j in range(2):
                ax = self.axs[i+1 , j]
                # ax.set_xlim(0, self.sim_time)
                index = 2 * i + j  # 计算 self.table_data 的索引
                if index == 0:
                    ax.set_title("Total Consumption", fontsize=8)
                    ax.set_ylabel("(kWh)", fontsize = 8)
                    total_cons_line = ax.plot([], [], 'r-', label='Total Consumption')
                    self.lines.append(total_cons_line[0])  # total_cons, red
                    standby_con_line = ax.plot([], [], 'b-', label = 'Standby Consumption')
                    self.lines.append(standby_con_line[0])  # standby_cons, blue

                elif index ==1:
                    ax.set_title("Truck In Depot", fontsize=8)
                    # ax.set_ylabel("(kWh)", fontsize = 8)
                    depot_one_line = ax.plot([], [], 'r-', label = 'Depot 1')
                    self.lines.append(depot_one_line[0])  # truck_in_depot[0], red
                    depot_two_line = ax.plot([], [], 'g-', label = 'Depot 2')
                    self.lines.append(depot_two_line[0])  # truck_in_depot[1], green
                    depot_three_line = ax.plot([], [], 'y-', label = 'Depot 3')
                    self.lines.append(depot_three_line[0])  # truck_in_depot[2], yellow
                    depot_four_line = ax.plot([], [], 'k-', label = 'Depot 4')
                    self.lines.append(depot_four_line[0])  # truck_in_depot[3], black
                elif index ==2:
                    ax.set_title("Orders' Average Waiting", fontsize=8)
                    ax.set_ylabel("(s)", fontsize = 8)
                    self.lines.append(ax.plot([], [], 'g-')[0])  # ave_waiting_time, green
                elif index ==3:
                    ax.set_title("Average Queue Time", fontsize=8)
                    ax.set_ylabel("(s)", fontsize = 8)
                    self.lines.append(ax.plot([], [], 'k-')[0])  # ave_queue_time, black

                font = {'family': 'serif',
                        'weight': 'normal',
                        'size': 6,
                    }
                ax.legend(prop = font)

         
        plt.show()

    def _update_line(self, line, x, y):
        x_data = list(line.get_xdata())
        y_data = list(line.get_ydata())
        x_data.append(x)
        y_data.append(y)
        line.set_xdata(x_data)
        line.set_ydata(y_data)
        ax = line.axes
        ax.relim()
        ax.autoscale_view()

    def update_graph(self, now):

        # 更新表格数据
        self.get_variables(now)
        self.table_data[0][0][1] = f"{self.variables['total_cons']:.2f}"
        self.table_data[0][1][1] = f"{self.variables['standby_cons']:.2f}"
        self.table_data[0][2][1] = f"{self.variables['ave_waiting_time']:.2f}"
        self.table_data[0][3][1] = f"{self.variables['mileage']:.2f}"
        self.table_data[1][0][1] = f"{self.variables['order_number']:.2f}"
        self.table_data[1][1][1] = f"{self.variables['carbon_emission']:.2f}"
        self.table_data[1][2][1] = f"{self.variables['ave_queue_time']:.2f}"
        self.table_data[1][3][1] = f"{self.variables['total_queue_length']:.2f}"


        # 更新图表数据
        mean_time = self.variables['mean_time']
        self._update_line(self.lines[0], mean_time, self.variables['total_cons'])
        self._update_line(self.lines[1], mean_time, self.variables['standby_cons'])
        
        # Update second subplot
        for i in range(4):
            self._update_line(self.lines[2 + i], mean_time, self.variables['truck_in_depot'][i][1])
        
        # Update third subplot
        self._update_line(self.lines[6], mean_time, self.variables['ave_waiting_time'])
        
        # Update fourth subplot
        self._update_line(self.lines[7], mean_time, self.variables["ave_queue_time"])




       
        for i in range(2):
            self.axs[0, i].cla()
            self.axs[0, i].axis('off')
            table = self.axs[0, i].table(cellText=self.table_data[i], loc='center', cellLoc='center')
            table.scale(1, 2)

 

    def draw_graph(self, now):
        
        self.update_graph(now)
        
        
            
        plt.ioff()
        plt.pause(0.001)  

        
