import salabim as sim
import random
from DynamicPlot import DynamicPlot

# 设置模拟时长
SIM_TIME = 100

# 创建模拟环境
env = sim.Environment()

# 模拟过程中变量的类
class LargeEvent(sim.Component):
    def process(self):
        while True:
            yield self.hold(sim.Uniform(1, 5).sample())

# 初始化变量
variables = [0, 0, 0, 0]

# 定义获取当前时间的函数
def get_time():
    return env.now()

# 定义获取变量的函数
def get_variables():
    global variables
    # 模拟随时间变化的变量
    variables = [random.random() for _ in range(4)]
    return variables

# 主程序
def main():
    # 创建并激活事件
    event = LargeEvent()
    event.activate()

    # 运行环境至时间1
    env.run(till=1)

    # 创建动态绘图对象
    dynamic_plot = DynamicPlot(get_time, get_variables, SIM_TIME)

    # 开始绘图
    dynamic_plot.draw_table_and_graph()

    # 等待用户按下键盘任意键退出
    input("Press any key to exit...")

if __name__ == "__main__":
    main()
