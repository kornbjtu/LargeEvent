import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')
import copy

from DONTUSELargeEvent import *

class DynamicPlot:
    def __init__(self, truck_list,depot_list, order_list, complete_times, sim_time, time_window = 3600):

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
        
        self.time_window = time_window

        self.fps = 24
        self.lines = []
        self.all_var =[]
        self.variables: Dict[str, float] = {
            "total_cons": 0.0,     #全场总能耗
            "standby_cons": 0.0,   #闲置能耗（排队&service时的能耗）
            "ave_waiting_time": 0.0,   #每个订单平均等待时间
            "mileage": 0.0,        #所有truck行驶总里程
            "mean_time": 0,          #实时时间（用于检索）
            "truck_in_depot":[],     #每个depot里的truck数量
            "carbon_emission":0.0,     #碳排放量
            "order_number": 0 ,      #订单总数
            "completed_order_num":0,    #已完成订单总数
            "ave_queue_time": 0.0,      #平均排队时间
            "total_queue_length": 0,     #所有depot的排队总长
            "service_cons": 0.0,         #service center产生的能耗
            "time_window_ave_queue_time":0.0  ,    #带time window的平均排队时间（按完成排队时间统计）
            "time_window_ave_waiting_time":0.0  ,    #带time window的order平均等待时间
            "unfinished_order":[],       #每个depot里积压的订单数，[depot_id, unfinished_order]
            "unfinished_volume":[],     #每个depot里积压的volume总数， [depot_id, unfinished_order_volume]
            "truck_total_time": [] , #实时所有车的时长结果, [parking_time, queue_time, service_time, delivery_time]
            "time_window_truck_total_time":[]      #带time window实时所有车的时长结果, [parking_time, queue_time, service_time, delivery_time]
        }

    def clear_variables(self):
        for key in self.variables:
            if key == "mean_time" or key == "order_number":
                self.variables[key]=0
            elif key == "truck_in_depot":
                self.variables[key] = []
            else:
                self.variables[key] = 0.0

    def truck_num(self):
        num = 0
        for truck in self.truck_list:
            num+=1
        return num

    def truck_condition(self,truck):
        active_time = truck.times["to_service_center"]
        start_service_time = truck.times["start_service"]
        output_time = truck.times["start_delivery"]
        inpot_time = truck.times["in_depot"]
        if active_time and (start_service_time==None or active_time > start_service_time):
            return 0        #means truck is in the queue
        elif start_service_time and (output_time==None or start_service_time>output_time):
            return 1        #means truck is serving
        elif output_time and (inpot_time==None or output_time>inpot_time):
            return 2        #means truck is delivering
        elif active_time==None or (inpot_time>output_time and output_time>start_service_time and start_service_time>=active_time):
            return 3        #means truck is parking and passive
        else:
            raise Exception("无法判断卡车状态，出现错误。")




##############计算函数
    def get_history(self):#计算已经完成的车辆的时间能耗
        history_con = 0.0
        for times in self.complete_times:
            active_time = times['to_service_center']
            inpot_time = times['in_depot']
            time_cons, disp_cons = times['factors']
            history_con += time_cons * (inpot_time-active_time)
        return history_con

    def get_ing_cons(self, now):#计算正在进行中的时间能耗
        ing_cons = 0.0
        for truck in self.truck_list:
            active_time = truck.times['to_service_center']
            time_cons, disp_cons = truck.times['factors']
            if self.truck_condition(truck)==1 or self.truck_condition(truck)==2:
                ing_cons+=(now-active_time) * time_cons
        return ing_cons
    
    def get_dis_cons(self): #计算距离能耗
        dis_cons = 0.0
        for truck in self.truck_list:
            mile = truck.get_mile()
            time_cons, disp_cons = truck.times['factors']
            dis_cons += disp_cons * mile
        return dis_cons

    def get_standby_cons(self, now):#计算总闲置能耗
        standby_cons = 0.0
        for times in self.complete_times:
            active_time = times['to_service_center']
            outpot_time = times['start_delivery']
            time_cons, disp_cons = times['factors']
            standby_cons += time_cons * (outpot_time - active_time)
        for truck in self.truck_list:
            active_time = truck.times['to_service_center']
            time_cons, disp_cons = truck.times['factors']
            if self.truck_condition(truck) == 1:
                standby_cons += time_cons * (now-active_time)
                
            elif self.truck_condition(truck) == 2:

                outpot_time = truck.times['start_delivery']
                standby_cons += time_cons * (outpot_time-active_time)
                

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

    def get_order_number(self):     #订单数量
        order_number = len(self.order_list)
        return order_number

    def get_completed_order_num(self):  #已完成订单总数
        comp_num = 0
        for order in self.order_list:
            if order.is_complete==True:
                comp_num+=1
        return comp_num

    def get_total_queue_length(self):       #总排队长度
        length = 0
        for depot in self.depot_list:
            length += depot.service_center.serve_queue.length()
        return length

    def get_ave_queue_time(self):       #每趟车平均排队时间
        queue_time = 0.0
        num = 0
        for times in self.complete_times:
            active_time = times['to_service_center']
            start_service_time = times['start_service']
            queue_time += start_service_time - active_time
            num+=1
        for truck in self.truck_list:
            active_time = truck.times['to_service_center']
            start_service_time = truck.times['start_service']
            if self.truck_condition(truck) == 2 or self.truck_condition(truck) == 1:
                queue_time += start_service_time - active_time
                num+=1
            
        if num == 0:
            return queue_time
        else:
            ave_queue_time = queue_time/num
            return ave_queue_time

    def get_service_cons(self):        #service center的能耗
        service_time = 0.0
        service_cons = 0.0
        for depot in self.depot_list:
            service_time += depot.service_center.get_service_time()
            service_cons = service_time * depot.service_center.extra_energy
        return service_cons

    def get_tw_ave_queue_time(self, now):       #每趟车平均排队时间with time window
        queue_time = 0.0
        num = 0
        for times in self.complete_times:
            active_time = times['to_service_center']
            start_service_time = times['start_service']
            if start_service_time + self.time_window >= now:
                queue_time += start_service_time - active_time
                num+=1
        for truck in self.truck_list:

            if self.truck_condition(truck) == 2:

                active_time = truck.times['to_service_center']
                start_service_time = truck.times['start_service']
                if start_service_time + self.time_window >= now:
                    queue_time += start_service_time - active_time
                    num+=1

        if num == 0:
            return queue_time
        else:
            ave_queue_time = queue_time/num
            return ave_queue_time
        
    def get_tw_ave_waiting_time(self,now):#计算已经完成的订单的平均等待的时间with time window
        waiting_time = 0.0
        num = 0
        ave_waiting_time = 0.0
        for order in self.order_list:
            if order.is_complete == True and order.complete_time + self.time_window >= now:
                waiting_time += order.complete_time - order.generation_time
                num+=1
            if num>0:
                ave_waiting_time = waiting_time/num
        return ave_waiting_time

    def get_unfinished_order(self):
        unfinished_order = []
        for depot in self.depot_list:
            volume = 0
            id = depot.id
            for order in depot.order_list:
                volume+=1
            unfinished_order.append((id, volume))
        return unfinished_order
    
    def get_unfinished_volume(self):
        unfinished_volume = []
        for depot in self.depot_list:
            volume = 0
            id = depot.id
            for order in depot.order_list:
                volume+=order.volume
            unfinished_volume.append((id, volume))
        return unfinished_volume

    def get_total_time(self, now):
        num = self.truck_num()

        total_time = now * num
        delivery_time = 0.0
        parking_time = 0.0
        queue_time = 0.0
        service_time = 0.0
        for times in self.complete_times:
            active_time = times["to_service_center"]
            start_service_time = times["start_service"]
            output_time = times["start_delivery"]
            inpot_time = times["in_depot"]
            delivery_time+=inpot_time-output_time
            queue_time+=start_service_time-active_time
            service_time+=output_time-start_service_time
        for truck in self.truck_list:
            active_time = truck.times["to_service_center"]
            start_service_time = truck.times["start_service"]
            output_time = truck.times["start_delivery"]
            inpot_time = truck.times["in_depot"]
            if self.truck_condition(truck) == 0:
                queue_time+=now-active_time
            elif self.truck_condition(truck) == 1:
                queue_time += start_service_time-active_time
                service_time += now-start_service_time
            elif self.truck_condition(truck) == 2:
                queue_time += start_service_time-active_time
                service_time += output_time-start_service_time
                delivery_time += now-output_time
        parking_time = total_time-delivery_time-queue_time-service_time
        truck_time = [parking_time, queue_time, service_time, delivery_time]
        return truck_time

    def get_tw_total_time(self, now):
        num = self.truck_num()

        total_time = now if now<self.time_window else self.time_window
        addition_time = total_time*num
        delivery_time = 0.0
        parking_time = 0.0
        queue_time = 0.0
        service_time = 0.0
        for times in self.complete_times:
            active_time = times["to_service_center"]
            start_service_time = times["start_service"]
            output_time = times["start_delivery"]
            inpot_time = times["in_depot"]
            if active_time>now-total_time:
                delivery_time+=inpot_time-output_time
                queue_time+=start_service_time-active_time
                service_time+=output_time-start_service_time
            elif active_time<now-total_time and start_service_time>now-total_time:
                queue_time+=start_service_time-(now-total_time)
                service_time+=output_time-start_service_time
                delivery_time+=inpot_time-output_time
            elif start_service_time<now-total_time and output_time>now-total_time:
                service_time+=output_time-(now-total_time)
                delivery_time+=inpot_time-output_time
            elif output_time<now-total_time and inpot_time>now-total_time:
                delivery_time+=inpot_time-(now-total_time)
        for truck in self.truck_list:
            active_time = truck.times["to_service_center"]
            start_service_time = truck.times["start_service"]
            output_time = truck.times["start_delivery"]
            inpot_time = truck.times["in_depot"]
            if self.truck_condition(truck) == 0:
                if active_time>now-total_time:
                    queue_time+=now-active_time
                elif active_time<now-total_time:
                    queue_time+=now-(now-total_time)
            elif self.truck_condition(truck) == 1:
                if active_time>now-total_time:
                    queue_time += start_service_time-active_time
                    service_time += now-start_service_time
                elif active_time<now-total_time and start_service_time>now-total_time:
                    queue_time+=start_service_time-(now-total_time)
                    service_time+=now-start_service_time
                elif service_time<now-total_time:
                    service_time+=now-(now-total_time)
            elif self.truck_condition(truck) == 2:
                if active_time>now-total_time:
                    queue_time += start_service_time-active_time
                    service_time += output_time-start_service_time
                    delivery_time += now-output_time
                elif active_time<now-total_time and start_service_time>now-total_time:
                    queue_time+=start_service_time-(now-total_time)
                    service_time+=output_time-start_service_time
                    delivery_time+=now-output_time
                elif service_time<now-total_time and output_time>now-total_time:
                    service_time+=output_time-(now-total_time)
                    delivery_time+=now-output_time
                elif output_time<now-total_time:
                    delivery_time+=now-(now-total_time)


                
        parking_time = addition_time-delivery_time-queue_time-service_time
        truck_time = [parking_time, queue_time, service_time, delivery_time]
        return truck_time

    def get_variables(self, now):

 
        self.clear_variables()
        history_cons = self.get_history()
        ing_cons = self.get_ing_cons(now)
        dis_cons = self.get_dis_cons()
        standby_cons = self.get_standby_cons(now)
        ave_waiting_time = self.get_ave_waiting_time()
        truck_in_depot = []
        truck_in_depot = self.get_truck_in_depot()
        order_number = self.get_order_number()
        comp_order_num = self.get_completed_order_num()
        mile = self.get_mile()
        queue_length = self.get_total_queue_length()
        ave_queue_time = self.get_ave_queue_time()
        service_cons = self.get_service_cons()
        emission = (history_cons + ing_cons + dis_cons + service_cons) * 0.268
        time_window_ave_queue_time = self.get_tw_ave_queue_time(now)
        time_window_ave_waiting_time = self.get_tw_ave_waiting_time(now)
        unfinished_order = []
        unfinished_order = self.get_unfinished_order()
        unfinished_volume = []
        unfinished_volume = self.get_unfinished_volume()
        truck_time = []
        truck_time = self.get_total_time(now)
        tw_truck_time = []
        tw_truck_time=self.get_tw_total_time(now)

        self.variables["total_cons"] = history_cons + ing_cons + dis_cons+service_cons
        self.variables["standby_cons"] = standby_cons
        self.variables["ave_waiting_time"] = ave_waiting_time
        self.variables["mileage"] = mile
        self.variables["mean_time"] = now
        self.variables["truck_in_depot"] = truck_in_depot
        self.variables["order_number"] = order_number
        self.variables["completed_order_num"]=comp_order_num
        self.variables["carbon_emission"] = emission
        self.variables['ave_queue_time'] = ave_queue_time
        self.variables["total_queue_length"] = queue_length
        self.variables["service_cons"] = service_cons
        self.variables["time_window_ave_queue_time"] = time_window_ave_queue_time
        self.variables["time_window_ave_waiting_time"] = time_window_ave_waiting_time
        self.variables["unfinished_order"] = unfinished_order
        self.variables["unfinished_volume"] = unfinished_volume
        self.variables["truck_total_time"] = truck_time
        self.variables["time_window_truck_total_time"] = tw_truck_time
        
        new_variables = copy.deepcopy(self.variables)
        self.all_var.append(new_variables)

        

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
                    ax.set_title("Orders' Average Waiting in TW", fontsize=8)
                    ax.set_ylabel("(s)", fontsize = 8)
                    self.lines.append(ax.plot([], [], 'g-')[0])  # ave_waiting_time, green
                elif index ==3:
                    ax.set_title("Average Queue Time in TW", fontsize=8)
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

    def update_graph(self):

        # 更新表格数据
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
        self._update_line(self.lines[6], mean_time, self.variables["time_window_ave_waiting_time"])
        
        # Update fourth subplot
        self._update_line(self.lines[7], mean_time, self.variables['time_window_ave_queue_time'])




       
        for i in range(2):
            self.axs[0, i].cla()
            self.axs[0, i].axis('off')
            table = self.axs[0, i].table(cellText=self.table_data[i], loc='center', cellLoc='center')
            table.scale(1, 2)

 

    def draw_graph(self):   
        plt.ioff()
        plt.pause(0.001)  

        
