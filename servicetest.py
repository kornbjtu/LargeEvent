import salabim as sim

class TruckGenerator(sim.Component):
    def process(self):
        while True:
            Truck()
            self.hold(sim.Uniform(5, 15).sample())

class Truck(sim.Component):
    def process(self):
        self.enter(servicecenter.serve_queue)
        if servicecenter.ispassive():
            servicecenter.activate()
        self.passivate()

class AbstractServiceCenter:
    def __init__(self, capacity, serve_time_dist, serve_queue) -> None:
        self.capacity = capacity  # 服务中心的容量
        self.serve_time_dist = serve_time_dist  # 服务时间分布
        self.serve_queue = serve_queue  # 服务队列

class ServiceCenter(sim.Component, AbstractServiceCenter):
    def setup(self, capacity, serve_time_dist, serve_queue):
        AbstractServiceCenter.__init__(self, capacity, serve_time_dist, serve_queue)
        self.active_trucks = []  # 当前正在服务的卡车列表

    def process(self):
        while True:
            while len(self.serve_queue) == 0 or len(self.active_trucks) >= self.capacity:
                self.passivate()
            self.truck = self.serve_queue.pop()
            self.active_trucks.append(self.truck)
            service_time = self.serve_time_dist.sample()  # 使用分布生成服务时间
            self.hold(service_time)
            self.truck.activate()
            self.active_trucks.remove(self.truck)
            if len(self.serve_queue) > 0 and len(self.active_trucks) < self.capacity:
                self.activate()

env = sim.Environment(trace=True)

waitingline = sim.Queue("waitingline")
service_time_distribution = sim.Uniform(20, 40)
servicecenter = ServiceCenter(capacity=4, serve_time_dist=service_time_distribution, serve_queue=waitingline)

TruckGenerator()

env.run(till=500)
print()
waitingline.print_statistics()
