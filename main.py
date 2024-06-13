import Window
from LargeEvent import *
from Graph import *
import json



##########################################################
#                                                        #
#                   UTENSILS FUNCTION                    #
#                                                        #
##########################################################
def draw_without_replacement(items):
    result = []
    while items:
        choice = random.choice(items)
        items.remove(choice)
        result.append(choice)
    return result


if __name__ == "__main__":




    ############## GET USER-DEFINED PARAMS ###########

    params = Window.get_simulation_params()
    print(params)



    ############## GRAPH SETTING ###################

    # 1. Graph generation
    data_file = params["Behavioral Settings"]["Map"]

    # road setting

    # Road type, True: expressway, False: Cityway
    ROAD_SL = {True: params["Behavioral Settings"]["Speed on Motorway"], 
               False: params["Behavioral Settings"]["Speed on City Street"]}

    map: Graph = init_graph(data_file, ROAD_SL)

    # read each nodes

    DEPOT_LIST = map.get_type_nodes("Depot")  # all the nodes which are depots

    ORDER_DES_LIST = map.get_type_nodes("Order_dest")

    ##################### DISTRIBUTION ###################
    SERVE_TIME_DIS = sim.Exponential(mean=m2s(params["Distributions Parameters"]["Service time mean"]))

    GAP_DIST = sim.Exponential(m2s(params["Distributions Parameters"]["Order generation IAT mean"]))  # 订单生成时间的分布

    DURATION_DIST = sim.Normal(h2s(params["Distributions Parameters"]["Event Duration Shift mean"]), params["Distributions Parameters"]["Event Duration Shift sigma"])  # event持续时间的

    VOLUME_DIST = sim.Uniform(params["Distributions Parameters"]["Voloume mean"], params["Distributions Parameters"]["Volume sigma"])  # 订单生成的load的分布

    DEPOT_DIST = {}  # table density for order generation's depot
    DEST_DIST = {}  # table density for order generation's dedstination

    for node in ORDER_DES_LIST:
        DEST_DIST[node.id] = 1.0 / len(ORDER_DES_LIST)  # 每个节点的概率均等

    for depot_node in DEPOT_LIST:
        DEPOT_DIST[depot_node] = 1.0 / len(DEPOT_LIST)

    ############# VENUE SETTING #################

    # read venue settings

    with open(params["Behavioral Settings"]["Venue-related parameters"]) as file: general_params = json.load(file)

    VENUES = []

    for venue in general_params["venues"]:
        VENUES.append(Venue(node=map.node(venue["Node"]), 
                            start_time=h2s(venue["StartTime"]), 
                            duration=DURATION_DIST.sample() + venue["Duration"], 
                            event_scale=venue["Scale"], 
                            influence_road=[map.get_road(1, x) for x in venue["AffectedNodes"]], 
                            affected_node=[map.node(x) for x in venue["AffectedNodes"]]))
    # 一天按12小时算总共43200s
   

    TRANS_MAT = general_params["TransMat"]

    CONG_LEVELS = general_params["CongLevel"]
    CONG_FACTORS = {int(key): item for key, item in general_params["CongFactor"]}

    ##################### DEPOT parameters ####################

    # we assume each depot has exactly only 5 vehicles
    NUM_TRUCK_TYPES = {
                0: params["Behavioral Settings"]["Number of Ritsch Truck"],
                1: params["Behavioral Settings"]["Number of Dongfeng Truck"],
                2: params["Behavioral Settings"]["Number of Isuzu Truck"],
                3: params["Behavioral Settings"]["Number of Volvo Truck"],
    }

    

    NUM_DEPOT = len(DEPOT_LIST)

    TRIGGER_VOLUME = 20

    MAX_WAIT_TIME = m2s(30)

    #################### SIMULATION SETTINGS ####################

    SIM_TIME = 43200 # seconds
    CONSUMPTION = [1.11, 0.063] #[time_consumption, distance_consumption]
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
    complete_times = [] # this list is to store the time spent that completes the tour. After one tour, the data in the truck will be cleaned.

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
           depot_list=depot_list, venue_list=VENUES, map=map, order_list=order_list), dynamic_plot=DynamicPlot(truck_list=truck_list, order_list=order_list, complete_times=complete_times, sim_time=SIM_TIME, consumption=CONSUMPTION))

    env.run(till=SIM_TIME)

    #################### 3 STATISTICS ###################

    # print()
    # for d in depot_list:
    #     d.service_center.serve_queue.print_statistics()
    # print(truck_list[4].get_truck_pos())

