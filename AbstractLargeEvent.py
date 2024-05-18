from dataclasses import dataclass
from typing import Dict, List
from Graph import *
from abc import abstractmethod, abstractstaticmethod


### DATA CLASSES ###

@dataclass
class Loc:
    x: float
    y: float

class Truck:
    def __init__(self) -> None:
        self.location: Loc
        self.id: int
        self.outd_time: float # out depot time
        self.act_time: float # active time
        self.deli_arr_time: Dict[int, float]
        self.ind_time: float # in depot time
        self.depot: int # belonging to which depot

        ## CONSTANTS
        self.DIS_ENER_CON: float # distance energy consumption
        self.TIME_ENER_CON: float # time energy consumption
        self.NR_ORDER: int # number of order


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


class Depot:
    def __init__(self) -> None:
        self.location: Loc
        self.id: int
        self.truck_instock: int
        self.nr_inservice: int
        self.max_order: int # maximum order it can hold?
        self.service_center: ServiceCenter

    @abstractmethod
    def accept_order(self):
        pass

    @abstractmethod
    def receive_truck(self):
        pass

class ServiceCenter:
    def __init__(self) -> None:
        self.cap: int
        self.serve_time: float
        self.serve_queue: List[int]
    
    @abstractmethod
    def serve(self):
        pass

class Order:
    def __init__(self) -> None:
        self.start_time: float
        self.time_window: float
        self.destination: int # node is a int
        self.volume: float # the volume of the good


class Venue:
    def __init__(self) -> None:
        self.start_time: float
        self.end_time: float
        self.influence_range_level: int
        self.influence_road: List[Road]
        self.cong_level: int
        self.cong_factor: float


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
        self.depot_dist: Dict[Depot, float]

    @abstractmethod
    def generate(self):
        pass

    


    