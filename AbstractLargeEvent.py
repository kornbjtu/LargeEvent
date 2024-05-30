from dataclasses import dataclass
from typing import Dict, List
from Graph import *
from abc import abstractmethod, abstractstaticmethod
import salabim as sim

### DATA CLASSES ###

@dataclass
class Loc:
    x: float
    y: float

class AbstractTruck:
    def __init__(self, id, order_list, act_time, depot) -> None:
        #real-time tracking
        self.location: Loc

        # necessary attributes
        self.id: int = id
        self.outd_time: float = None # out depot time
        self.act_time: float = act_time # active time
        self.deli_arr_time: Dict[int, float]
        self.ind_time: float = None # in depot time
        self.depot: AbstractDepot = depot # belonging to which depot
        self.order_list: List[AbstractOrder] = order_list
        self.now_node: Node = depot.node

        ## CONSTANTS
        self.TYPE: str # the type of truck, defining the capacity


    @abstractmethod
    def wait_maintenance(self):
        pass
    
    @abstractmethod
    def move(self, sec: float):
        pass
    
    @abstractstaticmethod
    def plan_route(from_node:int, to_node: int):
        pass
    
    def return_depot(depot: int):
        pass


class AbstractDepot:
    def __init__(self, id, node, truck_instock, max_order, capacity, serve_time_dist, serve_queue) -> None:
        self.node: Node = node
        self.id: int = id
        self.truck_instock: List[AbstractTruck] = truck_instock
        self.max_order: int = max_order # maximum order the driver should hold
        self.service_center: AbstractServiceCenter(capacity, serve_time_dist, serve_queue)

    @abstractmethod
    def accept_order(self):
        pass

    @abstractmethod
    def receive_truck(self):
        pass

class AbstractServiceCenter:
    def __init__(self, capacity, serve_time_dist, serve_queue) -> None:
        self.capacity = capacity  # 服务中心的容量
        self.serve_time_dist = serve_time_dist  # 服务时间分布
        self.serve_queue: sim.Queue = serve_queue  # 服务队列
    
    @abstractmethod
    def serve(self):
        pass

class AbstractOrder:
    def __init__(self) -> None:
        self.start_time: float
        self.time_window: float
        self.destination_node: Node 
        self.volume: float # the volume of the good
        self.arrival_time: float


class AbstractVenue:
    def __init__(self) -> None:
        self.start_time: float
        self.end_time: float
        self.influence_range_level: int
        self.influence_road: List[Road]
        self.cong_level: int
        self.cong_factor: float


class AbstractLargeEventGen:
    def __init__(self) -> None:
        self.venues: List[Venue]
        self.trans_mat: List[List[float]]

    @abstractmethod
    def gen_cong_level(self, venue: Venue):
        pass

    @abstractmethod
    def gen_cong(self, venue: Venue):
        pass


class AbstractOrderGen:
    def __init__(self) -> None:
        self.dest_dist: Dict[int, float]
        self.avg_interval_times: Dict[int, float]
        self.depot_dist: Dict[Depot, float]

    @abstractmethod
    def generate(self):
        pass

    


    