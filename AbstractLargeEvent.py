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
    def __init__(self, id, order_list, act_time, depot, depot_list) -> None:
        # real-time tracking
        self.location: Loc

        # necessary attributes
        self.id: int = id
        self.outd_time: float = None  # out depot time
        self.act_time: float = act_time  # active time
        self.deli_arr_time: Dict[int, float]
        self.ind_time: float = None  # in depot time
        self.depot: AbstractDepot = depot  # belonging to which depot
        # belonging to which service center
        self.serve_center: AbstractServiceCenter = None
        self.order_list: List[AbstractOrder] = order_list
        self.now_node: Node = depot.node
        self.depot_list: List[AbstractDepot] = depot_list

        # CONSTANTS
        self.TYPE: str  # the type of truck, defining the capacity


class AbstractDepot:
    def __init__(self, id, node, max_order, capacity, serve_time_dist, serve_queue, max_wait_time, order_list, truck_list) -> None:
        self.node: Node = node
        self.order_list: List[AbstractOrder] = order_list
        self.id: int = id
        self.max_order: int = max_order  # maximum order the driver should hold
        self.service_center: AbstractServiceCenter
        self.max_wait_time: float = max_wait_time
        self.truck_list: List[AbstractTruck] = truck_list  # all trucks

    @abstractmethod
    def get_truck_instock(self) -> List[AbstractTruck]:
        pass

    @abstractmethod
    def accept_order(self):
        pass

    @abstractmethod
    def receive_truck(self):
        pass


class AbstractServiceCenter:
    def __init__(self, capacity, serve_time_dist, serve_queue, depot) -> None:
        # self.capacity = capacity  # 服务中心的容量
        self.serve_time_dist: sim.Distribution = serve_time_dist  # 服务时间分布
        self.serve_queue: sim.Queue = serve_queue  # 服务队列
        self.depot: AbstractDepot = depot

    @abstractmethod
    def serve(self):
        pass


@dataclass
class AbstractVenue:
    start_time: float  # event generation time
    duration: sim.Distribution   # sample from distribution############################
    influence_road: List[Road]
    event_scale: int
    node: Node
    affected_node: List[Node]
    cong_level: float = 0
    cong_factor: float = 0


@dataclass
class AbstractOrder:
    generation_time: float  # generation time
    complete_time: float|None 
    destination: Node  # node is a int
    volume: float  # the volume of the good
    depot: AbstractDepot  # From which depot
    is_complete: bool # is completed or not


class AbstractLargeEventGen:
    def __init__(self) -> None:
        self.venues: List[AbstractVenue]
        self.trans_mat: List[List[float]]

    @abstractmethod
    def gen_cong_level(self, venue: AbstractVenue):
        pass

    @abstractmethod
    def gen_cong(self, venue: AbstractVenue):
        pass


class AbstractOrderGen:
    def __init__(self) -> None:
        self.dest_dist: Dict[int, float]
        self.avg_interval_times: Dict[int, float]
        self.depot_dist: Dict[AbstractDepot, float]

    @abstractmethod
    def generate(self):
        pass
