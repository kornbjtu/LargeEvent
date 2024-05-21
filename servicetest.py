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
    def process(self):
        while True:
            while len(waitingline) == 0:
                self.passivate()
            self.truck = waitingline.pop()
            service_time = sim.Uniform(20, 40).sample()  # 使用均匀分布生成服务时间
            self.hold(service_time)
            self.truck.activate()

env = sim.Environment(trace=True)

TruckGenerator()
servicecenter = ServiceCenter()
waitingline = sim.Queue("waitingline")

env.run(till=50)
print()
waitingline.print_statistics()
