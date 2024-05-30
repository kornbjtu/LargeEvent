import salabim as sim
import random
from typing import List, Tuple
from abc import abstractmethod


class Road:
    def __init__(self, node1=None, node2=None, velocity_limit=None):
        self.node1: Node = node1
        self.node2: Node = node2
        self.velocity_limit: float = velocity_limit
        self.length: float = np.sqrt((self.node1.location.x - self.node2.location.x).pow(2) + (self.node1.location.y - self.node2.location.y).pow(2))
    def get_weight(self):
        return self.length / self.velocity_limit

class AbstractVenue:
    def __init__(self) -> None:
        self.start_time: float
        self.end_time: float
        self.influence_range_level: int
        self.influence_road: List[Road]
        self.cong_level: int
        self.cong_factor: float

class Venue(AbstractVenue):
    def __init__(self, location: Tuple[float, float], event_scale: int, start_time: float, end_time: float, influence_road: List[Road]):
        super().__init__()
        self.location = location
        self.event_scale = event_scale
        self.start_time = start_time
        self.end_time = end_time
        self.influence_road = influence_road
        self.cong_level = 0
        self.cong_factor = 1.0

class AbstractLargeEventGen(sim.Component):
    def setup(self, venues: List[Venue], trans_mat: List[List[float]]) -> None:
        self.venues = venues
        self.trans_mat = trans_mat

    @abstractmethod
    def gen_cong_level(self, venue: Venue):
        pass

    @abstractmethod
    def gen_cong(self, venue: Venue):
        pass

class ConcreteLargeEventGen(AbstractLargeEventGen):
    def setup(self, venues: List[Venue], trans_mat: List[List[float]]):
        self.venues = venues
        self.trans_mat = trans_mat
        self.cong_levels = [0, 1, 2, 3, 4, 5]
        self.cong_factors = {0: 1, 1: 1.05, 2: 1.15, 3: 1.25, 4: 1.35, 5: 1.45}
        self.results = []  # 保存结果的列表

    def gen_cong_level(self, venue: Venue) -> int:
        scale_index = venue.event_scale - 1
        cong_level_probs = self.trans_mat[scale_index]
        return random.choices(self.cong_levels, cong_level_probs)[0]

    def gen_cong(self, venue: Venue) -> float:
        cong_level = self.gen_cong_level(venue)
        return self.cong_factors[cong_level]

    def process(self):
        while True:
            num_venues_to_generate = random.randint(1, len(self.venues))  # 随机选择生成事件的地点数量
            selected_venues = random.sample(self.venues, num_venues_to_generate)  # 随机选择地点
            for venue in selected_venues:
                venue.cong_level = self.gen_cong_level(venue)
                venue.cong_factor = self.cong_factors[venue.cong_level]
                self.results.append((self.env.now(), venue.location, venue.event_scale, venue.cong_level, venue.cong_factor))
                print(f"Time: {self.env.now()}, Venue: {venue.location}, Scale: {venue.event_scale}, Congestion Level: {venue.cong_level}, Congestion Factor: {venue.cong_factor}")
            self.hold(60)  # 每小时生成一次事件

# 示例使用
roads = [Road(1), Road(2), Road(3)]

# 根据你提供的节点数据，定义前五个可能产生事件的节点
venues = [
    Venue((0, 40), 1, start_time=0, end_time=100, influence_road=roads),
    Venue((-10, 10), 2, start_time=0, end_time=100, influence_road=roads),
    Venue((-40, -10), 3, start_time=0, end_time=100, influence_road=roads),
    Venue((-30, -30), 4, start_time=0, end_time=100, influence_road=roads),
    Venue((30, -30), 5, start_time=0, end_time=100, influence_road=roads)
]

trans_mat = [
    [0.9, 0.1, 0, 0, 0, 0],
    [0.1, 0.8, 0.1, 0, 0, 0],
    [0, 0.1, 0.8, 0.1, 0, 0],
    [0, 0, 0.1, 0.8, 0.1, 0],
    [0, 0, 0, 0.1, 0.8, 0.1],
    [0, 0, 0, 0, 0.1, 0.9]
]

env = sim.Environment(trace=True)

event_generator = ConcreteLargeEventGen(venues=venues, trans_mat=trans_mat)
event_generator.activate()

env.run(till=500)

# 打印结果
print("\nResults:")
for result in event_generator.results:
    time, location, scale, cong_level, cong_factor = result
    print(f"Time: {time}, Venue: {location}, Scale: {scale}, Congestion Level: {cong_level}, Congestion Factor: {cong_factor}")
