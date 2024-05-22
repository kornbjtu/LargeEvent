import numpy as np

all_trucks = []
all_depots = []
all_venues = []
all_ordergenerators = []
all_roads = []
all_nodes = {}
class Loc:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self):
        return f'Loc(x={self.x}, y={self.y})'

class Node:
    def __init__(self, location: Loc, id=None):  # 将默认值设为 None
        self.location = location
        self.id = id if id is not None else id(self)  # 处理默认情况，如果 id 是 None，则使用对象的 ID

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)
    
    @staticmethod
    def _find_or_create_node(node_id: int):
        # 如果节点已经存在于全局字典中，则直接返回
        if node_id in all_nodes:
            return all_nodes[node_id]
        # 否则，创建一个新的节点对象，并将其添加到全局字典中
        default_location = Loc(0, 0)
        new_node = Node(default_location, node_id)
        all_nodes[node_id] = new_node
        return new_node

class Truck:
    def __init__(self, location: Loc) -> None:
        
        self.location = location
        
        all_trucks.append(self)

loc1 = Loc(x=50, y=-20)     #test for trucks
loc2 = Loc(x=50, y=50)
# 创建两个 Truck 对象并分配 Loc 对象
truck1 = Truck(location=loc1)
truck2 = Truck(location=loc2) 
# 创建两个 Loc 对象

loc3 = Loc(x=0, y=5)        #test for depots
loc4 = Loc(x=10, y=-10)
loc5 = Loc(x=30, y=30)        #test for venue
loc6 = Loc(x=10, y=-30)
loc7 = Loc(x=40, y=0)        #test for order generator
loc8 = Loc(x=-20, y=-10)

node1 = Node(location=loc3, id=1)
all_nodes[node1.id] = node1

node2 = Node(location=loc4, id=2)
all_nodes[node2.id] = node2

node3 = Node(location=loc5, id=3)
all_nodes[node3.id] = node3

node4 = Node(location=loc6, id=4)
all_nodes[node4.id] = node4

node5 = Node(location=loc7, id=5)
all_nodes[node5.id] = node5

node6 = Node(location=loc8, id=6)
all_nodes[node6.id] = node6


class Depot:
    def __init__(self, node: Node) -> None:
        if isinstance(node, int):
            node = Node._find_or_create_node(node)
        
        self.node = node      
        
        all_depots.append(self)

depot1 = Depot(node = node1)
depot2 = Depot(2)

class Venue:
    def __init__(self, node: Node) -> None:
        if isinstance(node, int):
            node = Node._find_or_create_node(node)
        
        self.node = node 
        all_venues.append(self)

venue1 = Venue(node = node3)
venue2 =  Venue(4)

class Ordergenerator:
    def __init__(self, node: Node) -> None:
        if isinstance(node, int):
            node = Node._find_or_create_node(node)
        
        self.node = node 
        all_ordergenerators.append(self)

ordergenerator1 = Ordergenerator(node = node5)
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
 
    


Road1 = Road(Node1 = node1, Node2 = node2, cong=0, road_type = False)
Road2 = Road(Node1 = 1, Node2 = 3, cong=2, road_type = False)
Road3 = Road(2, 3, cong=0, road_type = True)


