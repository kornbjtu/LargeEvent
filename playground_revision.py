import numpy as np
from NodeData import *
import pandas as pd
import os
script_path = os.path.dirname(os.path.abspath(__file__))




all_trucks = []
all_depots = []
all_venues = []
all_ordergenerators = []
all_roads = []
all_midpoints = []


class Truck:
    def __init__(self, location: Loc) -> None:
        
        self.location = location
        
        all_trucks.append(self)

truck_loc1 = Loc(x=50, y=-20)     #test for trucks
truck_loc2 = Loc(x=50, y=50)
# 创建两个 Truck 对象并分配 Loc 对象
# truck1 = Truck(location=truck_loc1)
# truck2 = Truck(location=truck_loc2) 
# 创建两个 Loc 对象


class Depot:
    def __init__(self, node: Node) -> None:
        if isinstance(node, int):
            node = Node._find_or_create_node(node)
        
        self.node = node      
        
        all_depots.append(self)

depot1 = Depot(16)
depot2 = Depot(17)
depot3 = Depot(18)

class Venue:
    def __init__(self, node: Node) -> None:
        if isinstance(node, int):
            node = Node._find_or_create_node(node)
        
        self.node = node 
        all_venues.append(self)

venue1 = Venue(1)
venue2 =  Venue(2)
venue3 =  Venue(3)
venue4 =  Venue(4)
venue5 =  Venue(5)

class Ordergenerator:
    def __init__(self, node: Node) -> None:
        if isinstance(node, int):
            node = Node._find_or_create_node(node)
        
        self.node = node 
        all_ordergenerators.append(self)



ordergenerator1 = Ordergenerator(32)
ordergenerator2 = Ordergenerator(31)
ordergenerator3 = Ordergenerator(14)
ordergenerator4 = Ordergenerator(6)
ordergenerator5 = Ordergenerator(7)
ordergenerator6 = Ordergenerator(8)
ordergenerator7 = Ordergenerator(11)
ordergenerator8 = Ordergenerator(12)
ordergenerator9 = Ordergenerator(13)
ordergenerator10 = Ordergenerator(19)
ordergenerator11 = Ordergenerator(9)
ordergenerator12 = Ordergenerator(10)
ordergenerator13 = Ordergenerator(15)
ordergenerator14 = Ordergenerator(1)
ordergenerator15 = Ordergenerator(2)
ordergenerator16 = Ordergenerator(3)
ordergenerator17 = Ordergenerator(4)
ordergenerator18 = Ordergenerator(5)



class Road:
    
    def __init__(self, Node1: Node, Node2: Node, cong: int, road_type: bool):        #cong>=1 means with congestion, road_type=True means highway
        if isinstance(Node1, int):
            Node1 = Node._find_or_create_node(Node1)
        if isinstance(Node2, int):
            Node2 = Node._find_or_create_node(Node2)
        self.Node1 = Node1      #start node
        self.Node2 = Node2      #end node
        self.cong = cong           
        self.road_type = road_type
        all_roads.append(self)
 
    
file_path = os.path.join(script_path, "node_matrix.xlsx")
df = pd.read_excel(file_path, header=None)

for i in range(1, df.shape[0]):
    for j in range(3, df.shape[1]):
        # 检查是否有有效的地点序列
        if pd.notna(df.iloc[i, j]):
            # 根据值确定road_type
            if df.iloc[i, j] == 1:
                road_type = False
            elif df.iloc[i, j] == 2:
                road_type = True
            else:
                continue  # 如果值不是1或2，则跳过这次循环，不创建Road对象
            # 创建Road对象并添加到列表
            all_roads.append(Road(i, j-2, 0, road_type))


for road in all_roads:
    print("Node1: ", road.Node1.id)
    print("Node2: ", road.Node2.id)



