import numpy as np




all_trucks = []

class Loc:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __str__(self):
        return f'Loc(x={self.x}, y={self.y})'


class Truck:
    def __init__(self, location: Loc, id: int) -> None:
        self.location = location
        self.id = id
        all_trucks.append(self)
        
# 创建两个 Loc 对象
loc1 = Loc(x=50, y=-20)
loc2 = Loc(x=50, y=50)

# 创建两个 Truck 对象并分配 Loc 对象
truck1 = Truck(location=loc1, id=0)
truck2 = Truck(location=loc2, id=1)

# 打印 Truck 对象的位置信息以验证
# print(truck1.location)  # 输出: Loc(x=10, y=20)
# print(truck2.location)  # 输出: Loc(x=-15, y=-50)
