import numpy as np
import pandas as pd
import os
script_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_path, "node_matrix.xlsx")
df = pd.read_excel(file_path, header=None)



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



#遍历DataFrame中的每一行
for index, row in df.iloc[1:].iterrows():
    # 创建Loc对象
    loc = Loc(row[0], row[1])
    # 创建Node对象并添加到字典
    node = Node(loc, index)
    all_nodes[node.id] = node


# 以下点集更新于5.30，已停用，仅可用于excel链接失败后的备用
# loc1 = Loc(x=0, y=40)        
# loc2 = Loc(x=-10, y=10)
# loc3 = Loc(x=-40, y=-10)       
# loc4 = Loc(x=-30, y=-30)
# loc5 = Loc(x=30, y=-30)        
# loc6 = Loc(x=-10, y=20)
# loc7 = Loc(x=-40, y=10)
# loc8 = Loc(x=0, y=0)
# loc9 = Loc(x=-40, y=-20)
# loc10 = Loc(x=-30, y=-20)
# loc11 = Loc(x=10, y=-10)
# loc12 = Loc(x=10, y=-20)
# loc13 = Loc(x=10, y=-30)
# loc14 = Loc(x=10, y=20)
# loc15 = Loc(x=-30, y=-40)
# loc16 = Loc(x=0, y=20)
# loc17 = Loc(x=-50, y=-20)
# loc18 = Loc(x=30, y=-10)
# loc19 = Loc(x=10, y=-50)
# loc20 = Loc(x=0, y=35)
# loc21 = Loc(x=-10, y=15)
# loc22 = Loc(x=-15, y=10)
# loc23 = Loc(x=-40, y=-5)
# loc24 = Loc(x=-35, y=-10)
# loc25 = Loc(x=-40, y=-15)
# loc26 = Loc(x=-45, y=-15)
# loc27 = Loc(x=-25, y=-30)
# loc28 = Loc(x=-30, y=-35)
# loc29 = Loc(x=30, y=-25)
# loc30 = Loc(x=25, y=-30)
# loc31 = Loc(x=0, y=50)
# loc32 = Loc(x=20, y=50)
# loc33 = Loc(x=5, y=40)

# locations = [loc1, loc2, loc3, loc4, loc5, loc6, loc7, loc8, loc9, loc10,
#              loc11, loc12, loc13, loc14, loc15, loc16, loc17, loc18, loc19, loc20,
#              loc21, loc22, loc23, loc24, loc25, loc26, loc27, loc28, loc29, loc30,
#              loc31, loc32, loc33]




# for i in range(33):
#     node = Node(location=locations[i], id=i+1)
#     all_nodes[node.id] = node


