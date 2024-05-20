import numpy as np

class Loc:
    x: float
    y: float

class Truck:
    def __init__(self) -> None:
        self.location: Loc
        
# 创建两个 Loc 对象
loc1 = Loc(x=10, y=20)
loc2 = Loc(x=-15, y=-50)

# 创建两个 Truck 对象并分配 Loc 对象
truck1 = Truck(location=loc1)
truck2 = Truck(location=loc2)

# 打印 Truck 对象的位置信息以验证
print(truck1.location)  # 输出: Loc(x=10, y=20)
print(truck2.location)  # 输出: Loc(x=-15, y=-50)
