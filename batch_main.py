## 1. read default file, find out the difference

## 2. a file storing scenarios & configurations

## 3. read this file


## 4. for seed for scenario

##      5. revoke batch_main's main programe -> return csv with filename of "scenario+seed+output.csv"



import Window
from Graph import *
import json
from DynamicPlot import *
import random
from typing import Callable, Dict, List, Union, Tuple

from salabim.salabim import Environment
from Graph import *
from abc import abstractmethod, abstractstaticmethod
import salabim as sim
from AbstractLargeEvent import *
import random
from Vis import *
from DynamicPlot import *


################################## DATA CLASS ##########################################


@dataclass
class Venue:
    start_time: float  # event generation time
    duration: sim.Distribution   # sample from distribution############################
    influence_road: List[Road]
    event_scale: int
    node: Node
    affected_node: List[Node]
    cong_level: float = 0
    cong_factor: float = 0
    last_update_time : float = 0
    initial : int = 0
    map: Graph = map
    prev_cong_level : int = 0

@dataclass
class Order:
    generation_time: float  # generation time
    complete_time: float|None # complete time, when order is delivered.
    destination: Node  # node is a int
    volume: float  # the volume of the good
    depot: AbstractDepot  # From which depot
    is_complete: bool # is completed or not
    


################################## COMPONENTS ##########################################


class Depot(sim.Component, AbstractDepot):
    def setup(self, id, node, max_order, capacity, serve_time_dist, serve_queue, max_wait_time, order_list, truck_list, extra_energy) -> None:
        AbstractDepot.__init__(self, id, node, max_order, capacity,
                               serve_time_dist, serve_queue, max_wait_time, order_list, truck_list)
        self.service_center = ServiceCenter(
            capacity=capacity, serve_time_dist=serve_time_dist, serve_queue=serve_queue, depot=self, extra_energy=extra_energy)

    def get_truck_instock(self):
        return [truck for truck in self.truck_list if truck.depot == self]

    def process(self):

        while True:
            sum_order_volume = sum([order.volume for order in self.order_list])
            if (self.__get_time_wait() >= self.max_wait_time) or (sum_order_volume >= self.max_order):
                
                truck_instock = self.get_truck_instock()

                # then we send a truck to take the order
                while len(truck_instock) == 0:
                    # if no truck in stock
                    truck_instock = self.get_truck_instock()
                    self.hold(1)

                # clear order it takes, we assume it takes the order at first come first serve principle
                # in time order
                clear_order_list = []
                total_volume = 0
                for order in self.order_list:
                    if total_volume > self.max_order:
                        break

                    clear_order_list.append(order)
                    total_volume += order.volume

                # clear the list

                self.order_list = [
                    item for item in self.order_list if item not in clear_order_list]

                # send truck

                truck_sent = truck_instock[0]

                truck_sent.activate(process="in_queue")

                truck_sent.order_list = clear_order_list

            self.hold(1)

    def accept_order(self, order):

        self.order_list.append(order)

    def __get_time_wait(self):

        now = env.now()

        if len(self.order_list) == 0:
            return 0

        first_order_arrival_time = self.order_list[0].generation_time

        return now - first_order_arrival_time


class Truck(sim.Component, AbstractTruck):
    def setup(self, id, order_list, act_time, depot, depot_list, consumption):
        AbstractTruck.__init__(self, id, order_list,
                               act_time, depot, depot_list)

        ### track data ###
        self.path: None | List[Node] = None
        self.travel_time: None | float = None
        self.departure_time: None | float = None
        self.consumption: List[float] = consumption # [time_consumption, distance_consumption]

        self.times: Dict[str, float] = {
            "start_delivery": None,
            "to_service_center": None,
            "in_depot": None,
            "start_service": None,
            "factors": self.consumption
        }

    def in_queue(self):
        self.times["to_service_center"] = env.now()
        self.depot.service_center.serve_queue.add(self)
        self.serve_center = self.depot.service_center
        self.depot = None
        self.passivate()

    def __get_next_order_travel(self, now_node: Node) -> Tuple[AbstractOrder, List[Node], float]:

        times = []
        for order in self.order_list:
            path, time = map.shortest_path(now_node, order.destination)
            times.append((order, path, time))

        # TODO if overlapping order

        ind = np.argmin([item[2] for item in times])

        return times[ind]

    def __decide_return_depot(self) -> Depot:

        # heuristic decision-making is used here, go to the depot with least truck in stock

        instock_depots = [len(depot.get_truck_instock())
                          for depot in self.depot_list]
     # special case: no vehicles avaliable in all depots
        if np.sum(instock_depots) == 0:
            return self.depot_list[random.randint(0, len(self.depot_list) - 1)]

        depot_ind = np.argmin(instock_depots)

        return self.depot_list[depot_ind]

    def deliver(self):
        self.depot = None  # detach the depot it belongs
        self.serve_center = None  # detach the service center it belongs
        self.times["start_delivery"] = env.now()

        ### start delivery ###

        while len(self.order_list) > 0:
            order_en_route, path, travel_time = self.__get_next_order_travel(
                self.now_node)

            self.__update_truck_state(
                path=path, travel_time=travel_time, departure_time=env.now())
            self.hold(travel_time)

            ### order complete ###
            self.order_list.remove(order_en_route)
            order_en_route.is_complete = True
            order_en_route.complete_time = env.now()
            self.now_node = order_en_route.destination

        ### delivery complete ###

        ### decide to go back to depot ###

        # heuristic decision-making is used here, go to the depot with least truck in stock
        # can be adapted later, refer to  __decide_return_depot method
        return_depot = self.__decide_return_depot()
        path, travel_time = map.shortest_path(self.now_node, return_depot.node)

        self.__update_truck_state(
            path=path, travel_time=travel_time, departure_time=env.now())

        self.hold(travel_time)

        ### arrive depot ###

        self.__update_truck_state(
            path=None, travel_time=None, departure_time=None)

        self.depot = return_depot
        self.times["in_depot"] = env.now()

        ### save data ###

        complete_times.append(self.times)
        self.__clear()


        self.passivate()

    ######### Truck data ########

    def __clear(self):
        self.times = {
            "start_delivery": None,
            "to_service_center": None,
            "in_depot": None,
            "start_service": None,
            "factors": self.consumption
        }

    def __update_truck_state(self, path, travel_time, departure_time):
        self.path = path
        self.travel_time = travel_time
        self.departure_time = departure_time

        # get travel distance
        if self.path is not None:
            distance = np.sum([map.get_road(self.path[ind], self.path[ind + 1]).length 
                            for ind in range(len(self.path) - 1)])
            self.miles += distance

    def get_truck_pos(self):
        if self.depot:  # in depot
            return (self.depot.node.x, self.depot.node.y)
        elif self.serve_center:
            return (self.serve_center.depot.node.x, self.serve_center.depot.node.y)
        else:  # out in delivery

            assert self.path != None and self.travel_time != None and self.departure_time != None

            road_dict: Dict[Road, Node] = {map.get_road(
                self.path[ind], self.path[ind + 1]): self.path[ind] for ind in range(len(self.path) - 1)}

            spent_time_list = [road.get_weight() for road in road_dict.keys()]

            cumsum_time = np.cumsum(spent_time_list) + self.departure_time

            # determine which road its on
            for ind in range(len(cumsum_time)):
                if cumsum_time[ind] > env.now():
                    road_ind = ind
                    from_node_time = self.departure_time if ind == 0 else cumsum_time[ind - 1]
                    break

            on_road: Road = list(road_dict.keys())[road_ind]
            from_node: Node = road_dict[on_road]
            spent_time_on_road = env.now() - from_node_time

            assert spent_time_on_road >= 0

            # track accurate position on road
            return on_road.get_pos(spent_time_on_road, from_node)
        
    def get_mile(self):
        return self.miles
    
    def get_condition(self):
        if self.depot != None:
            return "depot"
        if self.serve_center != None:
            return "serve"
        else:
            return "delivery"


class ServiceCenter(sim.Component, AbstractServiceCenter):
    def setup(self, capacity, serve_time_dist, serve_queue, depot, extra_energy):
        AbstractServiceCenter.__init__(
            self, capacity, serve_time_dist, serve_queue, depot)
        self.active_trucks = []  # 当前正在服务的卡车列表
        

        #### data ####
        self.extra_energy = extra_energy
        self.total_service_time = 0


    def process(self):
        while True:
            while len(self.serve_queue) == 0:
                self.hold(1)
            self.truck = self.serve_queue.pop()
            self.active_trucks.append(self.truck)
            service_time = self.serve_time_dist.sample()  # 使用分布生成服务时间
            self.truck.times["start_service"] = env.now()
            self.hold(service_time)
            self.total_service_time += service_time # update total service time
            self.truck.activate(process='deliver')
            self.active_trucks.remove(self.truck)
            if len(self.serve_queue) > 0:
                self.activate()
    
    def get_service_time(self):
        return self.total_service_time


class LargeEventGen(sim.Component):
    def setup(self, venues, trans_mat, cong_levels, cong_factors, stage_duration):
        self.venue: List[Venue] = venues
        self.trans_mat: List[List[float]] = trans_mat
        self.cong_levels: List[int] = cong_levels
        self.cong_factors: Dict[int, float] = cong_factors
        self.stage_duration: int =  stage_duration
        
    def gen_cong_level(self, venue: Venue) -> int:
        scale_index = venue.event_scale
        if venue.prev_cong_level == 0 :
             cong_level_probs = self.trans_mat[scale_index]
        else :
             cong_level_probs = self.trans_mat[venue.prev_cong_level]
        return random.choices(self.cong_levels, cong_level_probs)[0]

    def update_road_weights(self, venue: Venue):
        for road in venue.influence_road:
            road.cong = venue.cong_level
            # print(road.cong)
    def process(self):
        while True:
            current_time = env.now()
            for venue in self.venue:
                start_time = venue.start_time
                duration = venue.duration
                end_time = start_time + duration
                
                # 检查当前时间是否在事件的开始时间和结束时间之间
                if start_time <= current_time < end_time:
                    if venue.initial == 0 : 
                        venue.cong_level = self.gen_cong_level(venue)  # 初始阶段没有上一个拥堵水平，使用0
                        venue.cong_factor = self.cong_factors[venue.cong_level]
                        self.update_road_weights(venue)
                        venue.last_update_time = current_time
                        venue.initial += 1
                    else: 
                        if current_time - venue.last_update_time >= self.stage_duration:  # 每个阶段开始时更新拥堵水平
                            venue.prev_cong_level = venue.cong_level
                            venue.cong_level = self.gen_cong_level(venue)
                            venue.cong_factor = self.cong_factors[venue.cong_level]
                            self.update_road_weights(venue)
                            venue.last_update_time = current_time  
                else: 
                     venue.cong_level = 0
                     venue.cong_factor = 0
                     self.update_road_weights(venue)
                     venue.initial=0
            self.hold(1)  # 每单位时间检查一次



class OrderGen(sim.Component):
    def setup(self, event_gen: LargeEventGen, dest_dist, depot_dist, volume_dist, gap_dist):
        self.original_dest_dist: Dict[int, float] = dest_dist
        self.gap_dist: sim.Distribution = gap_dist
        self.depot_dist: Dict[Depot, float] = depot_dist
        self.event_gen: LargeEventGen = event_gen
        self.dest_dist: Dict[int, float] = dest_dist
        self.volume_dist: sim.Distribution = volume_dist

    def process(self):
        while True:
            #清尾时间
            if SIM_TIME - env.now() <= CLEARANCE_TIME:
                print('Order genereation is over.')
                break  

            # 动态调整目的地分布
            self.dest_dist, adjustment_factor = self.adjust_dest_distribution(self.original_dest_dist, self.event_gen)

            # 选择一个目的地
            destination = self._select_from_distribution(self.dest_dist)

            # 选择一个仓库
            origin_node = self._select_from_distribution(self.depot_dist)
            depot = DEPOTS[origin_node]
            # generate time
            generation_time = env.now()

            # generate volume
            volume = np.abs(self.volume_dist.sample())

            # 生成订单
            order = Order(generation_time=generation_time, complete_time=None, destination=destination, volume=volume, depot=depot, is_complete=False)
            order_list.append(order)

            depot.accept_order(order)  # 仓库接收订单

            # 调整后的订单间隔时间
            adjusted_gap = self.adjust_gap_time(self.gap_dist.sample(), adjustment_factor)

            self.hold(adjusted_gap)

    def adjust_dest_distribution(self, dest_dist: Dict[int, float], event_gen: LargeEventGen):
        adjusted_dest_dist = dest_dist.copy()
        adjustment_factor = 1.0
        current_time = env.now()  # 获取当前时间

        for venue in event_gen.venue:
            if venue.start_time <= current_time < venue.start_time + venue.duration:
                adjustment_factor *= venue.cong_factor
                for node in venue.affected_node:
                    if node in adjusted_dest_dist:
                        adjusted_dest_dist[node] *=  venue.cong_level * 10


        total = sum(adjusted_dest_dist.values())
        if total > 0:
            for key in adjusted_dest_dist:
                adjusted_dest_dist[key] /= total

        return adjusted_dest_dist, adjustment_factor

    def adjust_gap_time(self, gap_time, adjustment_factor):
        if adjustment_factor > 1.0:
            return gap_time / adjustment_factor
        else:
            return gap_time

    def _select_from_distribution(self, distribution: Dict[int, float]):
        keys, values = zip(*distribution.items())
        selected = random.choices(keys, weights=values, k=1)[0]
        return selected

############################### VISUALIZATION COMPONENTS ####################
#                                                                           #
#       This part, even if as a salabim component, is a visualizor which    #
#       gets data from the system components and visualize the process      #
#                                                                           #
#                   THIS IS NOT A PART OF SIMULATION SYSTEM.                #
#                                                                           #
#############################################################################

class Visual(sim.Component):

    def setup(self, vis, dynamic_plot, if_dashboard, if_vis):
        self.vis: Plotter = vis
        self.dp: DynamicPlot = dynamic_plot
        self.if_dashboard = if_dashboard
        self.if_vis = if_vis

    def process(self):
        if self.if_dashboard:
            self.dp.initialize_window()

        while True:

            # when program is terminated:
            if env.now() == SIM_TIME:

                # save data
                # 调用函数并生成CSV文件
                Window.convert_data_to_csv(self.dp.all_var, OUTPUT_FILE)
                
                # pop up message box
                if self.if_dashboard or self.if_vis:
                    Window.show_completion_dialog()

                
                

            # track data
            self.dp.get_variables(env.now())
    
            if self.if_dashboard:
            
                self.dp.update_graph()

                if env.now() % 100 == 0:
                    self.dp.draw_graph()

            if self.if_vis:
                self.vis.draw_canvas(env.now())

            # it always runs at the first priority in each event time.
            self.hold(duration=1, priority=1)

            
                


##########################################################
#                                                        #
#                   UTENSILS FUNCTION                    #
#                                                        #
##########################################################


def h2s(x): return x * 60 * 60  # convert hours to seconds

def m2s(x): return x * 60  # convert minutes to seconds

def save_data(): 
    pass


if __name__ == "__main__":


    ############## GET USER-DEFINED PARAMS ###########

   
        # 从 JSON 文件中读取参数
    def load_params(json_files):
        params = {}
        for file in json_files:
            with open(file, 'r') as f:
                data = json.load(f)
                params.update(data)
        return params

    # 从Excel文件中读取测试参数
    def read_excel_params(file_path):
        df = pd.read_excel(file_path)
        params = {}
        for _, row in df.iterrows():
            keys = row['Parameter'].split('.')
            values = row[1:].dropna().tolist()
            d = params
            for key in keys[:-1]:
                if key not in d:
                    d[key] = {}
                d = d[key]
            d[keys[-1]] = values[0] if len(values) == 1 else values
        return params


    def merge_params(default, updates):
        for key, value in updates.items():
            if isinstance(value, dict) and key in default:
                default[key] = merge_params(default[key], value)
            else:
                default[key] = value
        return default

    def get_param_names(nested_dict, parent_key=''):
        param_names = []
        for k, v in nested_dict.items():
            full_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                param_names.extend(get_param_names(v, full_key))
            else:
                param_names.append(full_key)
        return param_names   


    json_files = ["batch_default_parm.json", "batch_general_params.json"]
    default_params = load_params(json_files)


    excel_file_path = "scenarios.xlsx"
    excel_params = read_excel_params(excel_file_path)

        # 获取随机种子数量
    seed_number = excel_params.get('Simulation & KPI-related Settings', {}).get('Seed Number', 1)

    # 获取参数名
    param_names = get_param_names(excel_params)
    # 过滤掉随机种子参数名
    param_names = [param for param in param_names if not param.endswith('Seed Number')]
    # 获取组合数量
    num_combinations = len(next(iter(excel_params.values())))
          
            
    # 生成随机种子
    seeds = np.random.randint(0, 10000, seed_number)

    # 生成所有实验场景的参数组合
    keys_values = {}
    max_length = 0
    for parameter, values in excel_params.items():
        if parameter == 'Simulation & KPI-related Settings' and 'Seed Number' in values:
            continue  # 跳过已经处理的随机种子参数         
        for key, value_set in values.items():
            combined_parameter = f"{parameter}.{key}"  # 将parameter和key结合成新的层级结构
            keys_values[combined_parameter] = value_set
            max_length = max(max_length, len(value_set))

    # 遍历参数组合
    for i in range(max_length):
        test_params = {}
        for combined_parameter, value_set in keys_values.items():
            if i < len(value_set):
                value = value_set[i]
                keys = combined_parameter.split('.')
                d = test_params
                for k in keys[:-1]:
                    d = d.setdefault(k, {})
                d[keys[-1]] = value
                # print(f"Preparing scenario with {combined_parameter} set to {value}")
        
        # 生成随机种子并运行仿真
        seeds = np.random.randint(0, 10000, seed_number)
   
        for seed_index, seed in enumerate(seeds):
            output_file_name = f"output/output_scenario_{i+1}_seed_{seed_index+1}.csv"
            print(f"Running simulation with seed {seed} and parameters: {test_params}")
            params = merge_params(default_params.copy(), test_params)
            params['Simulation & KPI-related Settings']["Output file"] = output_file_name
            params['Simulation & KPI-related Settings']["Random Seed"] = int(seed)
            # print(f"- Output file set to {output_file_name}")





 ########################################     主程序   ############################################################       
 # 
 ####################################################################################################################        

            data_file = params["Behavioral Settings"]["Map"]

            # 路线设置
            ROAD_SL = {
                True: params["Behavioral Settings"]["Speed on Motorway"], 
                False: params["Behavioral Settings"]["Speed on City Street"]
            }

            map = init_graph(data_file, ROAD_SL)

            # 读取每个节点
            DEPOT_LIST = map.get_type_nodes("Depot")  # 所有depot节点
            ORDER_DES_LIST = map.get_type_nodes("Order_dest") + map.get_type_nodes("Affectted_node")

            # 分布设置
            SERVE_TIME_DIS = sim.Exponential(m2s(params["Distributions Parameters"]["Service time mean"]))
            GAP_DIST = sim.Exponential(m2s(params["Distributions Parameters"]["Order generation IAT mean"]))
            DURATION_DIST = sim.Normal(h2s(params["Distributions Parameters"]["Event Duration Shift mean"]), params["Distributions Parameters"]["Event Duration Shift sigma"])
            VOLUME_DIST = sim.Normal(params["Distributions Parameters"]["Volume mean"], params["Distributions Parameters"]["Volume sigma"])

            DEPOT_DIST = {}
            DEST_DIST = {}

            for node in ORDER_DES_LIST:
                DEST_DIST[node] = 1.0 / len(ORDER_DES_LIST)

            for depot_node in DEPOT_LIST:
                DEPOT_DIST[depot_node] = 1.0 / len(DEPOT_LIST)

            # 读取场地设置
            with open(params["Distributions Parameters"]["Venue-related parameters"]) as file:
                general_params = json.load(file)

            VENUES = []

            for venue in general_params["venues"]:
                VENUES.append(Venue(
                    node=map.node(venue["Node"]), 
                    start_time=h2s(venue["StartTime"]), 
                    duration=np.abs(DURATION_DIST.sample() + venue["Duration"]),
                    event_scale=venue["Scale"], 
                    influence_road=[map.get_road(venue["Node"], x) for x in venue["AffectedNodes"]],
                    affected_node=[map.node(x) for x in venue["AffectedNodes"]]
                ))

            TRANS_MAT = general_params["TransMat"]
            CONG_LEVELS = general_params["CongLevel"]
            CONG_FACTORS = {int(key): item for key, item in general_params["CongFactor"].items()}
            STAGE_DURATION = m2s(params["Behavioral Settings"]["Stage Duration"])
            CLEARANCE_TIME = params["Behavioral Settings"]["Clearance time"]

            NUM_TRUCK_TYPES = {
                0: params["Behavioral Settings"]["Number of Ritsch Truck"],
                1: params["Behavioral Settings"]["Number of Dongfeng Truck"],
                2: params["Behavioral Settings"]["Number of Isuzu Truck"],
                3: params["Behavioral Settings"]["Number of Volvo Truck"]
            }

            NUM_DEPOT = len(DEPOT_LIST)
            TRIGGER_VOLUME = params["Behavioral Settings"]["Start delivery threshold"]
            MAX_WAIT_TIME = m2s(params["Behavioral Settings"]["Maximum waiting time"])
            SIM_TIME = params["Simulation & KPI-related Settings"]["Simulation time"]
            OUTPUT_FILE = params["Simulation & KPI-related Settings"]["Output file"]

            # 仿真环境
            env = sim.Environment(random_seed=params["Simulation & KPI-related Settings"]["Random Seed"])

            # 初始化
            truck_list = []
            depot_list = []
            order_list = []
            complete_times = []

            DEPOTS = {}

            for ind in range(len(DEPOT_LIST)):
                depot = Depot(
                    id=ind, node=DEPOT_LIST[ind], max_order=TRIGGER_VOLUME,
                    capacity=0, serve_time_dist=SERVE_TIME_DIS, serve_queue=sim.Queue(), max_wait_time=MAX_WAIT_TIME, 
                    order_list=[], truck_list=truck_list, extra_energy=general_params["ExtraEneServe"]
                )
                depot_list.append(depot)
                DEPOTS[depot.node] = depot

            counter = 0
            for ind, item in NUM_TRUCK_TYPES.items():
                for number in range(int(item)):
                    assigned_depot = depot_list[counter % NUM_DEPOT]
                    truck_list.append(Truck(
                        id=counter, order_list=[], act_time=None,
                        depot=assigned_depot, depot_list=depot_list, 
                        consumption=[general_params["TruckProfiles"][ind]["EneConTime"], general_params["TruckProfiles"][ind]["EneConMile"]]
                    ))
                    counter += 1

            event_gen = LargeEventGen(venues=VENUES, trans_mat=TRANS_MAT, cong_levels=CONG_LEVELS, cong_factors=CONG_FACTORS, stage_duration=STAGE_DURATION)
            OrderGen(event_gen=event_gen, dest_dist=DEST_DIST, depot_dist=DEPOT_DIST, volume_dist=VOLUME_DIST, gap_dist=GAP_DIST)

            Visual(vis=Plotter(
                truck_list=truck_list, depot_list=depot_list, venue_list=VENUES, map=map, order_list=order_list), 
                dynamic_plot=DynamicPlot(
                    truck_list=truck_list, order_list=order_list, depot_list=depot_list, complete_times=complete_times, 
                    sim_time=SIM_TIME, time_window=params["Visualization Settings"]["Average time window"]
                ), if_dashboard=params["Visualization Settings"]["Real-time dashboard"], 
                if_vis=params["Visualization Settings"]["Real-time process visualization"]
            )

            env.run(till=SIM_TIME)

