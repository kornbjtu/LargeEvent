
from typing import Callable, Dict, List, Union, Tuple

from salabim.salabim import Environment
from Graph import *
from abc import abstractmethod, abstractstaticmethod
import salabim as sim
from AbstractLargeEvent import *
import random

################################## DATA CLASS ##########################################

class Order:
    def __init__(self) -> None:
        self.start_time: float
        self.time_window: float
        self.destination: int  # node is a int
        self.volume: float  # the volume of the good
        self.depot: Depot


class Venue:
    def __init__(self) -> None:
        self.start_time: float
        self.end_time: float
        self.influence_range_level: int
        self.influence_road: List[Road]
        self.cong_level: int
        self.cong_factor: float
        self.event_sacle: int
        self.node: int

################################ default nodes settings ##############################
affected_nodes_list = {
    1: [graph.node(33), graph.node(20)],
    2: [graph.node(22), graph.node(21)],
    3: [graph.node(23), graph.node(24), graph.node(25), graph.node(26)],
    4: [graph.node(27), graph.node(28)],
    5: [graph.node(29), graph.node(30)]
}

venues = [
    Venue(node=1, event_scale=2, affected_nodes=affected_nodes_list[1]),
    Venue(node=2, event_scale=3, affected_nodes=affected_nodes_list[2]),
    Venue(node=3, event_scale=1, affected_nodes=affected_nodes_list[3]),
    Venue(node=4, event_scale=4, affected_nodes=affected_nodes_list[4]),
    Venue(node=5, event_scale=5, affected_nodes=affected_nodes_list[5])
]

trans_mat = [
    [0.9, 0.1, 0, 0, 0],
    [0.1, 0.8, 0.1, 0, 0],
    [0, 0.1, 0.8, 0.1, 0],
    [0, 0, 0.1, 0.8, 0.1],
    [0, 0, 0, 0.1, 0.9]
]

################################## COMPONENTS ##########################################


class Depot(sim.Component, AbstractDepot):
    def setup(self, id, order_list, act_time, depot) -> None:
        AbstractDepot.__init__(self, id, order_list, act_time, depot)

    def send_truck(self):
        
        sum_order_volume = sum([order.volume for order in self.order_list])
        if sum_order_volume >= self.max_order: 
            # then we send a truck to take the order
            while len(self.truck_instock) == 0:
                # if no truck in stock
                self.wait(1)

            truck_sent = self.truck_instock.pop(0)
            truck_sent.activate(process="in_queue")

class Truck(sim.Component, AbstractTruck):
    def setup(self, id, order_list, act_time, depot):
        AbstractTruck.__init__(self, id, order_list, act_time, depot)

    def in_queue(self):
        self.depot.service_center.serve_queue.add(self)
        self.passivate()

    def __get_next_order_travel(self, now_node: Node) -> Tuple(AbstractOrder, List[Road], float):
        
        times = []
        for order in self.order_list:
            path, time = map.shortest_path(now_node, order.destination_node)
            times.append((order, path, time))
        
        ind = np.argmax([item[2] for item in times])
        
        return times[ind]
    
    def __decide_return_depot(self) -> Depot:

        # heuristic decision-making is used here, go to the depot with least truck in stock
    
        instock_depots = [depot.truck_instock for depot in depot_list]
        depot_ind = np.argmin(instock_depots)

        return depot_list[depot_ind]

    def deliver(self):
        self.depot = None # detach the depot it belongs
        self.outd_time = env.now()

        ### start delivery ###
        
        while len(self.order_list) > 0:
            order_en_route, path, travel_time = self.__get_next_order_travel(self.now_node)
            self.wait(travel_time)
            ### TODO: update its location in real-time ###
            self.order_list.remove(order_en_route)
            order_en_route.arrival_time = env.now()
            self.now_node = order_en_route.destination_node

        
        ### delivery complete ###

        ### decide to go back to depot ###

        # heuristic decision-making is used here, go to the depot with least truck in stock
        # can be adapted later, refer to  __decide_return_depot method
        return_depot = self.__decide_return_depot()
        path, travel_time = map.shortest_path(self.now_node, return_depot.node)

        self.wait(travel_time)

        ### arrive depot ###

        self.depot = return_depot
        self.depot.truck_instock.append(self)
        self.passivate()

class ServiceCenter(sim.Component, AbstractServiceCenter):
    def setup(self, capacity, serve_time_dist, serve_queue):
        AbstractServiceCenter.__init__(self, capacity, serve_time_dist, serve_queue)
        self.active_trucks = []  # 当前正在服务的卡车列表

    def process(self):
        while True:
            while len(self.serve_queue) == 0 or len(self.active_trucks) >= self.capacity:
                self.passivate()
            self.truck = self.serve_queue.pop()
            self.active_trucks.append(self.truck)
            service_time = self.serve_time_dist.sample()  # 使用分布生成服务时间
            self.hold(service_time)
            self.truck.activate()
            self.active_trucks.remove(self.truck)
            if len(self.serve_queue) > 0 and len(self.active_trucks) < self.capacity:
                self.activate()


class LargeEventGen(sim.Component):
    def setup(self, venues: List[Venue], trans_mat: List[List[float]], env):
        self.venues = venues
        self.trans_mat = trans_mat
        self.cong_levels = [0, 1, 2, 3, 4, 5]
        self.cong_factors = {0: 1, 1: 1.05, 2: 1.15, 3: 1.25, 4: 1.35, 5: 1.45}
        self.results = []  # 保存结果的列表
        self.env = env

    def gen_cong_level(self, venue: Venue) -> int:
        scale_index = venue.event_scale
        cong_level_probs = self.trans_mat[scale_index]
        return random.choices(self.cong_levels, cong_level_probs)[0]
    
    def update_road_weights(self, venue: Venue):
            for road in venue.influence_road:
                road.cong = venue.cong_factor

    def process(self):
        while True:
            num_venues_to_generate = random.randint(1, len(self.venues))  
            selected_venues = random.sample(self.venues, num_venues_to_generate)  
            for venue in selected_venues:
                venue.cong_level = self.gen_cong_level(venue)
                venue.cong_factor = self.cong_factors[venue.cong_level]
                self.results.append((self.env.now, venue.location, venue.event_scale, venue.cong_level, venue.cong_factor))
                print(f"Time: {self.env.now}, Venue: {venue.location}, Scale: {venue.event_scale}, Congestion Level: {venue.cong_level}, Congestion Factor: {venue.cong_factor}")
            yield self.env.timeout(20) #定义event生成分布

class OrderGen(sim.Component):
    def setup(self, dest_dist: Dict[int, float], avg_interval_times: Dict[int, float], depot_dist: Dict[Depot, float], event_gen: LargeEventGen, env):
        self.dest_dist = dest_dist
        self.avg_interval_times = avg_interval_times
        self.depot_dist = depot_dist
        self.event_gen = event_gen
        self.env = env

    def process(self):
        while True:
            # 选择一个目的地
            destination = self._select_from_distribution(self.dest_dist)
            
            # 获取目的地的拥堵等级和拥堵因子
            venue = next((venue for venue in self.event_gen.venues if venue.location == destination), None)
            if venue:
                congestion_factor = venue.cong_factor
            else:
                congestion_factor = 1
            
            # 选择一个仓库
            depot = self._select_from_distribution(self.depot_dist)
            
            # 生成订单
            order = Order(destination, depot)
            depot.accept_order()  # 仓库接收订单
            
            # 打印订单信息
            print(f"Order generated at time {self.env.now}: from Depot {depot.id} to destination {destination}")
            
            # 平均间隔时间
            base_interval_time = self.avg_interval_times[destination]
            adjusted_interval_time = base_interval_time / congestion_factor
            yield self.env.timeout(sim.Exponential(adjusted_interval_time).sample())
    
    def _select_from_distribution(self, distribution: Dict):
        keys, values = zip(*distribution.items())
        selected = random.choices(keys, weights=values, k=1)[0]

        return selected




env = sim.Environment(trace=True)


################ INITIALIZATION #################
map: Graph = Graph()
depot_list: List[Depot] = []
