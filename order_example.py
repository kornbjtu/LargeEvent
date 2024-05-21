import salabim as sim
from typing import Dict, List, Tuple
from abc import ABC, abstractmethod
import random

class Loc:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

class AbstractDepot(ABC):
    def __init__(self, location: Loc, id: int, truck_instock: int, nr_inservice: int, max_order: int) -> None:
        self.location = location
        self.id = id
        self.truck_instock = truck_instock
        self.nr_inservice = nr_inservice
        self.max_order = max_order

    @abstractmethod
    def accept_order(self):
        pass

    @abstractmethod
    def receive_truck(self):
        pass

class Depot(AbstractDepot):
    def __init__(self, location: Loc, id: int, truck_instock: int, nr_inservice: int, max_order: int):
        super().__init__(location, id, truck_instock, nr_inservice, max_order)

    def accept_order(self):
        print(f"Depot {self.id} accepted an order at time {env.now()}.")

    def receive_truck(self):
        print(f"Depot {self.id} received a truck.")

class AbstractOrderGen(ABC):
    def __init__(self, dest_dist: Dict[int, float], avg_interval_times: Dict[int, float], depot_dist: Dict[Depot, float]) -> None:
        self.dest_dist = dest_dist
        self.avg_interval_times = avg_interval_times
        self.depot_dist = depot_dist

class OrderGen(sim.Component, AbstractOrderGen):
    def setup(self, dest_dist: Dict[int, float], avg_interval_times: Dict[int, float], depot_dist: Dict[Depot, float]):
        AbstractOrderGen.__init__(self, dest_dist, avg_interval_times, depot_dist)

    def process(self):
        while True:
            # 选择一个目的地
            destination = self._select_from_distribution(self.dest_dist)
            
            # 选择一个仓库
            depot = self._select_from_distribution(self.depot_dist)
            
            # 生成订单
            order = Order(destination, depot)
            depot.accept_order()  # 仓库接收订单
            
            # 打印订单信息
            print(f"Order generated at time {env.now()}: from Depot {depot.id} to destination {destination}")
            
            # 平均间隔时间
            interval_time = self.avg_interval_times[destination]
            self.hold(sim.Exponential(interval_time).sample())
    
    def _select_from_distribution(self, distribution: Dict):
        keys, values = zip(*distribution.items())
        selected = random.choices(keys, weights=values, k=1)[0]
        return selected

class Order:
    def __init__(self, destination: int, depot: Depot):
        self.destination = destination
        self.depot = depot

# 示例使用
location1 = Loc(10, 20)
location2 = Loc(30, 40)

depot1 = Depot(location1, 1, 10, 5, 50)
depot2 = Depot(location2, 2, 15, 7, 60)

dest_dist = {1: 0.5, 2: 0.3, 3: 0.2}
avg_interval_times = {1: 10, 2: 20, 3: 30}
depot_dist = {depot1: 0.4, depot2: 0.6}

env = sim.Environment(trace=True)

order_gen = OrderGen(dest_dist=dest_dist, avg_interval_times=avg_interval_times, depot_dist=depot_dist)

env.run(till=1500)
