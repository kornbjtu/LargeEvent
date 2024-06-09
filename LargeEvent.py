
from typing import Callable, Dict, List, Union, Tuple

from salabim.salabim import Environment
from Graph import *
from abc import abstractmethod, abstractstaticmethod
import salabim as sim
from AbstractLargeEvent import *
import random
from Vis import *

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


@dataclass
class Order:
    generation_time: float  # generation time
    destination: Node  # node is a int
    volume: float  # the volume of the good
    depot: AbstractDepot  # From which depot
    is_complete: bool # is completed or not


################################## COMPONENTS ##########################################


class Depot(sim.Component, AbstractDepot):
    def setup(self, id, node, max_order, capacity, serve_time_dist, serve_queue, max_wait_time, order_list, truck_list) -> None:
        AbstractDepot.__init__(self, id, node, max_order, capacity,
                               serve_time_dist, serve_queue, max_wait_time, order_list, truck_list)
        self.service_center = ServiceCenter(
            capacity=capacity, serve_time_dist=serve_time_dist, serve_queue=serve_queue, depot=self)

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
    def setup(self, id, order_list, act_time, depot, depot_list):
        AbstractTruck.__init__(self, id, order_list,
                               act_time, depot, depot_list)

        ### track data ###
        self.path: None | List[Node] = None
        self.travel_time: None | float = None
        self.departure_time: None | float = None

    def in_queue(self):
        self.depot.service_center.serve_queue.add(self)
        self.serve_center = self.depot.service_center
        self.depot = None
        self.passivate()

    def __get_next_order_travel(self, now_node: Node) -> Tuple[AbstractOrder, List[Road], float]:

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
        self.outd_time = env.now()

        ### start delivery ###

        while len(self.order_list) > 0:
            order_en_route, path, travel_time = self.__get_next_order_travel(
                self.now_node)

            self.update_truck_state(
                path=path, travel_time=travel_time, departure_time=env.now())
            self.hold(travel_time)

            ### order complete ###
            self.order_list.remove(order_en_route)
            order_en_route.is_complete = True
            order_en_route.arrival_time = env.now()
            self.now_node = order_en_route.destination

        ### delivery complete ###

        ### decide to go back to depot ###

        # heuristic decision-making is used here, go to the depot with least truck in stock
        # can be adapted later, refer to  __decide_return_depot method
        return_depot = self.__decide_return_depot()
        path, travel_time = map.shortest_path(self.now_node, return_depot.node)

        self.update_truck_state(
            path=path, travel_time=travel_time, departure_time=env.now())

        self.hold(travel_time)

        ### arrive depot ###

        self.update_truck_state(
            path=None, travel_time=None, departure_time=None)

        self.depot = return_depot
        # self.depot.truck_instock.append(self)
        self.passivate()

    ######### Truck data ########

    def update_truck_state(self, path, travel_time, departure_time):
        self.path = path
        self.travel_time = travel_time
        self.departure_time = departure_time

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



class ServiceCenter(sim.Component, AbstractServiceCenter):
    def setup(self, capacity, serve_time_dist, serve_queue, depot):
        AbstractServiceCenter.__init__(
            self, capacity, serve_time_dist, serve_queue, depot)
        self.active_trucks = []  # 当前正在服务的卡车列表

    def process(self):
        while True:
            while len(self.serve_queue) == 0:
                self.hold(1)
            self.truck = self.serve_queue.pop()
            self.active_trucks.append(self.truck)
            service_time = self.serve_time_dist.sample()  # 使用分布生成服务时间
            self.hold(service_time)
            self.truck.activate(process='deliver')
            self.active_trucks.remove(self.truck)
            if len(self.serve_queue) > 0:
                self.activate()


class LargeEventGen(sim.Component):
    def setup(self):
        self.venue: List[Venue] = VENUES
        self.trans_mat: List[List[float]] = TRANS_MAT
        self.cong_levels: List[int] = CONG_LEVELS
        self.cong_factors: Dict[int, float] = CONG_FACTORS

    def gen_cong_level(self, venue: Venue) -> int:
        scale_index = venue.event_scale
        cong_level_probs = self.trans_mat[scale_index]
        return random.choices(self.cong_levels, cong_level_probs)[0]

    def update_road_weights(self, venue: Venue):
        for road in venue.influence_road:
            road.cong = self.cong_factors[venue.node.id]

    def process(self):
        while True:
            num_venues_to_generate = random.randint(1, len(self.venue))
            selected_venues = random.sample(self.venue, num_venues_to_generate)
            for venue in selected_venues:
                venue.cong_level = self.gen_cong_level(venue)
                venue.cong_factor = self.cong_factors[venue.cong_level]

            self.hold(1)


class OrderGen(sim.Component):
    def setup(self, event_gen: LargeEventGen):
        self.original_dest_dist: Dict[int, float] = DEST_DIST
        self.gap_dist: sim.Distribution = GAP_DIST
        self.depot_dist: Dict[Depot, float] = DEPOT_DIST
        self.event_gen: LargeEventGen = event_gen
        self.dest_dist: Dict[int, float] = DEST_DIST
        self.volume_dist = sim.Distrubtion = VOLUME_DIST

    def process(self):
        while True:
            # 动态调整目的地分布
            self.dest_dist = self.adjust_dest_distribution(
                self.original_dest_dist, self.event_gen)

            # 选择一个目的地
            destination = self._select_from_distribution(self.dest_dist)

            # 选择一个仓库
            origin_node = self._select_from_distribution(self.depot_dist)
            depot = DEPOTS[origin_node]
            # generate time
            generation_time = env.now()

            # generate volume
            volume = self.volume_dist.sample()

            # 生成订单
            order = Order(generation_time, destination, volume, depot, is_complete=False)
            order_list.append(order)

            depot.accept_order(order)  # 仓库接收订单

            # 订单间隔时间

            self.hold(GAP_DIST.sample())

    def adjust_dest_distribution(self, dest_dist: Dict[int, float], event_gen: LargeEventGen):
        adjusted_dest_dist = dest_dist.copy()
        current_time = env.now()  # 获取当前时间

        for venue in event_gen.venue:
            if venue.start_time <= current_time < venue.start_time + venue.duration:
                for node in venue.affected_node:
                    if node in adjusted_dest_dist:
                        adjusted_dest_dist[node] *= venue.cong_factor

        total = sum(adjusted_dest_dist.values())
        if total > 0:
            for key in adjusted_dest_dist:
                adjusted_dest_dist[key] /= total

        return adjusted_dest_dist

    def _select_from_distribution(self, distribution: Dict[int, float]):
        keys, values = zip(*distribution.items())
        selected = random.choices(keys, weights=values, k=1)[0]
        return selected


############################### VISUALIZATION COMPONENTS ##################
#
#       This part, even if a salabim component, is a visualizor which
#       get data from the system components and visualize the process
#       THIS IS NOT A PART OF SIMULATION SYSTEM.
#
###########################################################################

class Visual(sim.Component):

    def setup(self, vis):
        self.vis: Plotter = vis

    def process(self):
        while True:
            self.vis.draw_canvas(env.now())

            # it always runs at the first priority in each event time.
            self.hold(duration=1, priority=1)


################################ SETTINGS ##############################
if __name__ == '__main__':

    ############## UTENTILS #######################
    def h2s(x): return x * 60 * 60  # convert hours to seconds

    def m2s(x): return x * 60  # convert minutes to seconds

    ############## GRAPH SETTING ###################

    # 1. Graph generation
    data_file = "node_matrix.xlsx"

    # road setting

    # Road type, True: expressway, False: Cityway
    ROAD_SL = {True: 60, False: 30}

    map: Graph = init_graph(data_file, ROAD_SL)

    # read each nodes

    DEPOT_LIST = map.get_type_nodes("Depot")  # all the nodes which are depots

    ORDER_DES_LIST = map.get_type_nodes("Order_dest")

    ##################### DISTRIBUTION ###################
    SERVE_TIME_DIS = sim.Uniform(m2s(1), m2s(2))

    GAP_DIST = sim.Uniform(m2s(0.5), m2s(1))  # 订单生成时间的分布

    DURATION_DIST = sim.Uniform(h2s(0.5), h2s(1.5))  # event持续时间的

    VOLUME_DIST = sim.Uniform(1, 4)  # 订单生成的load的分布

    DEPOT_DIST = {}  # table density for order generation's depot
    DEST_DIST = {}  # table density for order generation's dedstination

    for node in ORDER_DES_LIST:
        DEST_DIST[node.id] = 1.0 / len(ORDER_DES_LIST)  # 每个节点的概率均等

    for depot_node in DEPOT_LIST:
        DEPOT_DIST[depot_node] = 1.0 / len(DEPOT_LIST)

    ############# VENUE SETTING #################
    AFFECT_ROAD = {
        1: [map.get_road(1, x) for x in [33, 20]],
        2: [map.get_road(2, x) for x in [22, 21]],
        3: [map.get_road(3, x) for x in [23, 24, 25, 26]],
        4: [map.get_road(4, x) for x in [27, 28]],
        5: [map.get_road(5, x) for x in [29, 30]]
    }

    ORDER_AFFECT_NODE = {
        1: [map.node(33), map.node(20), map.node(31), map.node(32)],
        2: [map.node(22), map.node(21), map.node(6), map.node(14), map.node(8)],
        3: [map.node(23), map.node(24), map.node(25), map.node(26), map.node(7), map.node(9), map.node(10)],
        4: [map.node(27), map.node(28), map.node(15)],
        5: [map.node(29), map.node(30), map.node(11), map.node(12), map.node(13)]
    }

    # 一天按12小时算总共43200s
    VENUES = [
        Venue(node=map.node(1), start_time=h2s(3), duration=DURATION_DIST.sample(
        ), event_scale=2, influence_road=AFFECT_ROAD[1], affected_node=ORDER_AFFECT_NODE[1]),
        Venue(node=map.node(2), start_time=h2s(6), duration=DURATION_DIST.sample(
        ), event_scale=3, influence_road=AFFECT_ROAD[2], affected_node=ORDER_AFFECT_NODE[2]),
        Venue(node=map.node(3), start_time=h2s(9), duration=DURATION_DIST.sample(
        ), event_scale=1, influence_road=AFFECT_ROAD[3], affected_node=ORDER_AFFECT_NODE[3]),
        Venue(node=map.node(4), start_time=h2s(6), duration=DURATION_DIST.sample(
        ), event_scale=4, influence_road=AFFECT_ROAD[4], affected_node=ORDER_AFFECT_NODE[4]),
        Venue(node=map.node(5), start_time=h2s(6.5), duration=DURATION_DIST.sample(
        ), event_scale=5, influence_road=AFFECT_ROAD[5], affected_node=ORDER_AFFECT_NODE[5])
    ]

    TRANS_MAT = [
        [1,     0,     0,      0,      0,      0],
        [0,     0.9,   0.1,    0,      0,      0],
        [0,     0.1,   0.8,    0.1,    0,      0],
        [0,     0,     0.1,    0.8,    0.1,    0],
        [0,     0,     0,      0.1,    0.8,    0.1],
        [0,     0,     0,      0,      0.1,    0.9]
    ]

    CONG_LEVELS = [0, 1, 2, 3, 4, 5]
    CONG_FACTORS = {0: 1, 1: 1.05, 2: 1.15, 3: 1.25, 4: 1.35, 5: 1.45}

    ##################### DEPOT parameters ####################

    # we assume each depot has exactly only 5 vehicles
    NUM_TRUCK = 5 * len(DEPOT_LIST)
    NUM_DEPOT = len(DEPOT_LIST)

    TRIGGER_VOLUME = 20

    MAX_WAIT_TIME = m2s(30)

    #################### SIMULATION SETTINGS ###################

    SIM_TIME = 43200 # seconds

    #################### METRICS SETTINGS #######################







    ##################################################
    ##              MAIN LINE                       ##
    ##################################################

    env = sim.Environment()

    ################ INITIALIZATION #################

    # 1. Generators Initiation

    # Information Initialization

    truck_list = []
    depot_list = []
    order_list = []

    # dictionary of depot_id to depot

    DEPOTS = {}

    for ind in range(len(DEPOT_LIST)):

        depot = Depot(id=ind, node=DEPOT_LIST[ind], max_order=TRIGGER_VOLUME,
                      capacity=0, serve_time_dist=SERVE_TIME_DIS, serve_queue=sim.Queue(), max_wait_time=MAX_WAIT_TIME, order_list=[], truck_list=truck_list)

        depot_list.append(depot)

        DEPOTS[depot.node] = depot

    for ind in range(NUM_TRUCK):
        # Assign depot in a round-robin manner
        assigned_depot = depot_list[ind % NUM_DEPOT]
        truck_list.append(Truck(id=ind, order_list=[], act_time=None,
                          depot=assigned_depot, depot_list=depot_list))

    ###### generate event ########

    event_gen = LargeEventGen()

    ###### place order generators on each node #######

    OrderGen(event_gen=event_gen)

    Visual(vis=Plotter(truck_list=truck_list,
           depot_list=depot_list, venue_list=VENUES, map=map))

    env.run(till=SIM_TIME)

    #################### 3 STATISTICS ###################

    print()
    # for d in depot_list:
    #     d.service_center.serve_queue.print_statistics()
    print(truck_list[4].get_truck_pos())
