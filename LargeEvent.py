
from typing import Callable, Dict, List, Union, Tuple

from salabim.salabim import Environment
from Graph import *
from abc import abstractmethod, abstractstaticmethod
import salabim as sim
from AbstractLargeEvent import *


################################## COMPONENTS ##########################################


class Depot(sim.Component, AbstractDepot):
    def setup(self, id, order_list, act_time, depot) -> None:
        AbstractDepot.__init__(self, id, order_list, act_time, depot)

    @abstractmethod
    def accept_order(self):
        pass

    @abstractmethod
    def receive_truck(self):
        pass

    @abstractmethod
    def send_truck(self):
        pass


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
        self.node: int


class LargeEventGen:
    def __init__(self) -> None:
        self.venues: List[Venue]
        self.trans_mat: List[List[float]]

    @abstractmethod
    def gen_cong_level(self, venue: Venue):
        pass

    @abstractmethod
    def gen_cong(self, venue: Venue):
        pass


class OrderGen:
    def __init__(self) -> None:
        self.dest_dist: Dict[int, float]
        self.avg_interval_times: Dict[int, float]

    def assign_depot(self):

    @abstractmethod
    def generate(self):
        pass



env = sim.Environment(trace=True)


################ INITIALIZATION #################
map: Graph = Graph()
depot_list: List[Depot] = []
