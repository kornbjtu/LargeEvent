import salabim as sim

class TruckGenerator(sim.Component):
    def process(self):
        while True:
            Truck()
            self.hold(sim.Uniform(5, 15).sample())

class Truck(sim.Component):
    def process(self):
        self.enter(waitingline)
        if servicecenter.ispassive():
            servicecenter.activate()
        self.passivate()

class ServiceCenter(sim.Component):
    def setup(self, capacity):
        self.capacity = capacity  # 服务中心的容量
        self.active_trucks = []  # 当前正在服务的卡车列表

    def process(self):
        while True:
            while len(waitingline) == 0 or len(self.active_trucks) >= self.capacity:
                self.passivate()
            self.truck = waitingline.pop()
            self.active_trucks.append(self.truck)
            service_time = sim.Uniform(20, 40).sample()  # 使用均匀分布生成服务时间
            self.hold(service_time)
            self.truck.activate()
            self.active_trucks.remove(self.truck)
            if len(waitingline) > 0 and len(self.active_trucks) < self.capacity:
                self.activate()

env = sim.Environment(trace=True)

TruckGenerator()
servicecenter = ServiceCenter(capacity=4)  # 设置ServiceCenter的容量为4
waitingline = sim.Queue("waitingline")

env.run(till=50)
print()
waitingline.print_statistics()
