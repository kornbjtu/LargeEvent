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

class Loc:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self):
        return f'Loc(x={self.x}, y={self.y})'

class Truck:
    def __init__(self, location: Loc) -> None:
        
        self.location = location
        
        all_trucks.append(self)

truck_loc1 = Loc(x=50, y=-20)     #test for trucks
truck_loc2 = Loc(x=50, y=50)
# 创建两个 Truck 对象并分配 Loc 对象
truck1 = Truck(location=truck_loc1)
truck2 = Truck(location=truck_loc2) 
# 创建两个 Loc 对象


class Depot:
    def __init__(self, node: Node) -> None:
        if isinstance(node, int):
            node = Node._find_or_create_node(node)
        
        self.node = node      
        
        all_depots.append(self)

depot1 = Depot(1)
depot2 = Depot(2)

class Venue:
    def __init__(self, node: Node) -> None:
        if isinstance(node, int):
            node = Node._find_or_create_node(node)
        
        self.node = node 
        all_venues.append(self)

venue1 = Venue(3)
venue2 =  Venue(4)

class Ordergenerator:
    def __init__(self, node: Node) -> None:
        if isinstance(node, int):
            node = Node._find_or_create_node(node)
        
        self.node = node 
        all_ordergenerators.append(self)

ordergenerator1 = Ordergenerator(5)
ordergenerator2 = Ordergenerator(6)
  

    


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
 
    
file_path = os.path.join(script_path, "node-matrix.xlsx")
df = pd.read_excel(file_path, header=None)

# for index, row in df.iterrows():
#     # 从第三列开始，因为前两列是坐标
#     for i in range(2, len(row), 2):
#         # 检查是否有有效的地点序列
#         if pd.notna(row[i]) and pd.notna(row[i+1]):
#             # 根据值确定road_type
#             road_type = False if row[i+1] == 1 else True
#             # 创建Road对象并添加到列表
#             all_roads.append(Road(row[i], row[i+1], 0, road_type))


Road1 = Road(Node1 = 1, Node2 = 2, cong=0, road_type = False)
Road2 = Road(Node1 = 1, Node2 = 3, cong=1, road_type = False)
Road3 = Road(2, 3, cong=0, road_type = True)
Road4 = Road(6, 10, 2, False)
Road5 = Road(11, 18, 3, False)
Road6 = Road(12, 33, 4, False)
Road7 = Road(30, 5, 5, False)

import os

# 打印当前工作目录
print(os.getcwd())

# 打印当前工作目录下的所有文件和文件夹
print(os.listdir(os.getcwd()))