import numpy as np




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
        
# 创建两个 Loc 对象
loc1 = Loc(x=50, y=-20)     #test for trucks
loc2 = Loc(x=50, y=50)
loc3 = Loc(x=0, y=0)        #test for depots
loc4 = Loc(x=10, y=-10)
loc5 = Loc(x=30, y=30)        #test for venue
loc6 = Loc(x=10, y=-30)
loc7 = Loc(x=40, y=0)        #test for order generator
loc8 = Loc(x=-20, y=-10)

# 创建两个 Truck 对象并分配 Loc 对象
truck1 = Truck(location=loc1)
truck2 = Truck(location=loc2)

class Depot:
    def __init__(self, location: Loc) -> None:
        self.location = location
        all_depots.append(self)

depot1 = Depot(location=loc3)
depot2 = Depot(location=loc4)

class Venue:
    def __init__(self, location: Loc) -> None:
        self.location = location
        all_venues.append(self)

venue1 = Venue(location=loc5)
venue2 =  Venue(location=loc6)

class Ordergenerator:
    def __init__(self, location: Loc) -> None:
        self.location = location
        all_ordergenerators.append(self)

ordergenerator1 = Ordergenerator(location=loc7)
ordergenerator2 = Ordergenerator(location=loc8)

class Node:
    def __init__(self, location: Loc, id = int):
        self.location = location
        self.id = id
    

node1 = Node(location = loc3, id=3)
node2 = Node(location = loc4, id=4)
node3 = Node(location = loc5, id=5)
node4 = Node(location = loc6, id=6)

class Road:
    def __init__(self, Node1: Loc, Node2: Node, cong: int, road_type: bool):       #cong>=1 means with congestion, road_type=True means highway
        self.Node1 = Node1      #start node
        self.Node2 = Node2      #end node
        self.cong = cong           
        self.road_type = road_type
        all_roads.append(self)

Road1 = Road(Node1 = node1, Node2 = node2, cong=0, road_type = False)
Road2 = Road(Node1 = node1, Node2 = node3, cong=2, road_type = False)
Road3 = Road(Node1 = node2, Node2 = node3, cong=0, road_type = True)


