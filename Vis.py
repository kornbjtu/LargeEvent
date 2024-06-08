import cv2
import numpy as np
import matplotlib.pyplot as plt
import threading
from playground import *
from LargeEvent import *
from Graph import *


class Plotter:
    def __init__(self, sim_time, truck_list, depot_list, venue_list, map):
        self.canvas = np.zeros((700, 700, 3), dtype=np.uint8)
        self.fps = 24
        self.truck_color = ((255, 0, 255))  # truck: purple
        self.depot_color = ((0, 255, 255))  # depot: yellow
        self.venue_color = ((255, 0, 0))  # event venue: blue
        self.ordergenerator_color = ((0, 255, 0))  # order generator: green

        self.midpoint_color = ((255, 165, 0))

        self.road_color = [
            (255, 255, 255), (204, 204, 255), (153, 153,
                                               255), (102, 102, 255), (51, 51, 255), (0, 0, 255)
        ]

        # self.road_cong_color = ((0, 0, 255))          #congested road: red
        self.truck_radius = 3
        self.depot_radius = 10
        self.venue_radius = 10
        self.ordergenerator_radius = 6
        self.road_nor_width = 1
        self.road_high_width = 2
        self.midpoint_width = 4

        self.table_data = [["1", "2"], ["3", "4"]]  # 这是一个示例数据，你可以根据需要修改

        ###########################################################################################
        self.truck_list: List[Truck] = truck_list
        self.depot_list: List[Depot] = depot_list
        self.venue_list: List[Venue] = venue_list
        self.map: Graph = map

        ###########################################################################################

    def update_canvas(self):
        cv2.imshow('Canvas', self.canvas)
        key = cv2.waitKey(int(1000/self.fps))
        return key  # 返回按下的键的ASCII码

    def end(self):
        key = self.update_canvas()
        if key != -1:  # 如果用户按下了键，跳出循环
            cv2.destroyAllWindows()
        self.canvas.fill(0)  # 清空画布以便于下一帧
        cv2.waitKey(0)  # 动画结束后，窗口将保持打开状态，直到用户按下任意键
        cv2.destroyAllWindows()

    def trans(self, x: int, y: int):  # coordinate transfer
        canvas_x = int(5*(x + 60))
        canvas_y = int(700-5*(y + 60))
        return canvas_x, canvas_y

    def animate_depots(self):
        for depot in all_depots:
            cv2.circle(self.canvas, self.trans(depot.node.location.x,
                       depot.node.location.y), self.depot_radius, self.depot_color, -1)

    def animate_venues(self):
        for venue in all_venues:
            cv2.circle(self.canvas, self.trans(venue.node.location.x,
                       venue.node.location.y), self.venue_radius, self.venue_color, -1)

    def animate_ordergenerators(self):
        for ordergenerator in all_ordergenerators:
            cv2.circle(self.canvas, self.trans(ordergenerator.node.location.x,
                       ordergenerator.node.location.y), self.ordergenerator_radius, self.ordergenerator_color, -1)

    def animate_midpoints(self):
        for midpoint in all_midpoints:
            cv2.circle(self.canvas, self.trans(midpoint.node.location.x,
                       midpoint.node.location.y), self.midpoint_width, self.midpoint_color, -1)

    def animate_roads(self):

        for road in all_roads:

            if road.road_type == False:
                if road.cong == 0:
                    # normal road and no congestion

                    cv2.line(self.canvas, self.trans(road.Node1.location.x, road.Node1.location.y), self.trans(
                        road.Node2.location.x, road.Node2.location.y), self.road_color[0], self.road_nor_width)
                elif road.cong == 1:
                    # normal road with congestion rank1

                    cv2.line(self.canvas, self.trans(road.Node1.location.x, road.Node1.location.y), self.trans(
                        road.Node2.location.x, road.Node2.location.y), self.road_color[1], self.road_nor_width)
                elif road.cong == 2:
                    # normal road with congestion rank2

                    cv2.line(self.canvas, self.trans(road.Node1.location.x, road.Node1.location.y), self.trans(
                        road.Node2.location.x, road.Node2.location.y), self.road_color[2], self.road_nor_width)
                elif road.cong == 3:
                    # normal road with congestion rank3

                    cv2.line(self.canvas, self.trans(road.Node1.location.x, road.Node1.location.y), self.trans(
                        road.Node2.location.x, road.Node2.location.y), self.road_color[3], self.road_nor_width)
                elif road.cong == 4:
                    # normal road with congestion rank4

                    cv2.line(self.canvas, self.trans(road.Node1.location.x, road.Node1.location.y), self.trans(
                        road.Node2.location.x, road.Node2.location.y), self.road_color[4], self.road_nor_width)
                elif road.cong == 5:
                    # normal road with congestion rank5

                    cv2.line(self.canvas, self.trans(road.Node1.location.x, road.Node1.location.y), self.trans(
                        road.Node2.location.x, road.Node2.location.y), self.road_color[5], self.road_nor_width)

            else:
                # highways

                cv2.line(self.canvas, self.trans(road.Node1.location.x, road.Node1.location.y), self.trans(
                    road.Node2.location.x, road.Node2.location.y), self.road_color[0], self.road_high_width)

    def animate_nodes(self):
        for node_id, node in all_nodes.items():
            # 获取节点的坐标
            x, y = node.location.x, node.location.y
            # 在画布上绘制一个圆形
            cv2.circle(self.canvas, self.trans(node.location.x, node.location.y),
                       self.ordergenerator_radius, self.ordergenerator_color, -1)

    def draw_table_and_graph(self):
        # 创建一个新的figure
        fig, axs = plt.subplots(2)

        # 在第一个子图中绘制表格
        axs[0].axis('off')
        table = axs[0].table(cellText=self.table_data,
                             loc='center', cellLoc='center')
        table.scale(1, 4)

        # 在第二个子图中绘制图像
        x = np.linspace(0, 2 * np.pi, 100)
        y = np.sin(x)
        axs[1].plot(x, y)
        axs[1].set_title('y = sin(x)')

        # 显示图表
        plt.show()

    def draw_canvas(self):

        self.animate_depots()
        self.animate_venues()
        self.animate_ordergenerators()
        self.animate_roads()
        self.animate_midpoints()

        # self.animate_nodes()

        self.end()

    def draw(self):
        thread = threading.Thread(target=self.draw_canvas)

        # 启动线程
        thread.start()

        # 在主线程中绘制表格和图像
        self.draw_table_and_graph()
