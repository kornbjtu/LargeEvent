import cv2
import numpy as np
from Graph import *
import time
from DONTUSELargeEvent import *


class Plotter:
    def __init__(self, truck_list, depot_list, venue_list, map, order_list):
        self.canvas = np.zeros((700, 700, 3), dtype=np.uint8)
        self.fps = 200
        self.truck_color = ((0, 215, 255))  # truck: gold
        self.depot_color = ((0, 255, 255))  # depot: yellow
        # self.venue_color = ((255, 0, 0))        #event venue: blue
        self.ordergenerator_color = ((144, 238, 144))  # order generator: green
        self.generate_order_color = ((255, 255, 150))       
        self.complete_order_color = ((185, 218, 255))       
        self.highway_color = ((255, 255, 224))
        self.depot_volume = ((185, 218, 255))

        self.road_color = [
            (255, 255, 255), (204, 204, 255), (153, 153,
                                               255), (102, 102, 255), (51, 51, 255), (0, 0, 255)
        ]
        self.venue_color = [
            (255, 213, 213), (255, 170, 170), (255, 128,
                                               128), (255, 85, 85), (255, 43, 43), (255, 0, 0)
        ]
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.truck_radius = 5
        self.depot_radius = 10
        self.venue_radius = 10
        self.ordergenerator_radius = 6
        self.road_nor_width = 2
        self.road_high_width = 3
        self.midpoint_width = 4
        self.rect_width, self.rect_height = 1, 2  # 长方形的尺寸
        self.gap = 0.5  # 长方形之间的间隔

        ###########################################################################################
        self.all_trucks: List[Truck] = truck_list
        self.all_depots: List[Depot] = depot_list
        self.all_venues: List[Venue] = venue_list
        self.all_orders: List[Order] = order_list
        self.map: Graph = map

        self.all_ordergenerators = []
        self.all_ordergenerators.extend(self.map.get_type_nodes('Affectted_node'))
        self.all_ordergenerators.extend(self.map.get_type_nodes('Order_dest'))
        self.ordergenerator_states = {}
        for ordergenerator in self.all_ordergenerators:
            if ordergenerator.id not in self.ordergenerator_states:
                self.ordergenerator_states[ordergenerator.id] = {
                    'color': self.ordergenerator_color,
                    'reset_time': None,
                    'display_text': False
                }
        ###########################################################################################
    def _clear_canvas(self):
        self.canvas = np.zeros((700, 700, 3), dtype="uint8")

    def update_canvas(self):
        cv2.imshow('Canvas', self.canvas)
        self.end()
        time.sleep(1 / self.fps)

    def end(self):
        k = cv2.waitKey(1)
        if k == ord('q'):
            # press q to terminate the loop
            cv2.destroyAllWindows()
            return True
        elif k == ord('p'):
            while True:
                k2 = cv2.waitKey(1)
                if k2 == ord('q'):
                    # press q to terminate the loop
                    cv2.destroyAllWindows()
                    return True
                elif k2 == ord('p'):
                    break

    def trans(self, x: int, y: int):  # coordinate transfer
        canvas_x = int(5*(x + 60))
        canvas_y = int(700-5*(y + 60))
        return canvas_x, canvas_y

    def animate_meantime(self, now):
        cv2.putText(self.canvas, str(int(now)), self.trans(-60, 60),
                    self.font, 0.7, (255, 255, 255), 1)

    def animate_depots(self):
        for depot in self.all_depots:
            cv2.putText(self.canvas, str(depot.id+1), self.trans(
                    depot.node.x+5, depot.node.y-5), self.font, 0.5, (0, 255, 255), 1)
            v = 0.0
            for order in depot.order_list:
                v+=order.volume
            volume = int(v)
            if depot.id == 0:
                 cv2.putText(self.canvas, str(volume), self.trans(
                    depot.node.x-5, depot.node.y+5), self.font, 0.5, self.depot_volume, 1)
            elif depot.id == 1:
                cv2.putText(self.canvas, str(volume), self.trans(
                    depot.node.x-5, depot.node.y), self.font, 0.5, self.depot_volume, 1)
            elif depot.id == 2:
                cv2.putText(self.canvas, str(volume), self.trans(
                    depot.node.x+5, depot.node.y), self.font, 0.5, self.depot_volume, 1)
            else:
                cv2.putText(self.canvas, str(volume), self.trans(
                    depot.node.x, depot.node.y-5), self.font, 0.5, self.depot_volume, 1)
            for i in range(depot.service_center.serve_queue.length()):
                # 计算每个长方形的位置
                position_x = depot.node.x-5 + (self.rect_width + self.gap) * i
                # 绘制长方形
                cv2.rectangle(self.canvas, self.trans(position_x, depot.node.y-5), self.trans(
                    position_x + self.rect_width, depot.node.y-5 + self.rect_height), (255, 255, 255), -1)
            for j in range(depot.service_center.serve_queue.length()):
                # 计算每个长方形的位置
                position_x = depot.node.x-5 + (self.rect_width + self.gap) * i
                # 绘制长方形
                cv2.rectangle(self.canvas, self.trans(position_x, depot.node.y-5), self.trans(
                    position_x + self.rect_width, depot.node.y-5 + self.rect_height), (255, 255, 255), -1)
            cv2.circle(self.canvas, self.trans(
                depot.node.x, depot.node.y), self.depot_radius, self.depot_color, -1)

    def animate_trucks(self):
        for truck in self.all_trucks:
            x_position, y_position = truck.get_truck_pos()
            cv2.circle(self.canvas, self.trans(x_position, y_position),
                       self.truck_radius, self.truck_color, -1)

    def animate_venues(self):
        for venue in self.all_venues:

            if venue.cong_level == 0:
                cv2.circle(self.canvas, self.trans(
                    venue.node.x, venue.node.y), self.venue_radius, self.venue_color[0], -1)
                cv2.putText(self.canvas, '0', self.trans(
                    venue.node.x-5, venue.node.y-5), self.font, 0.5, (255, 255, 255), 1)
            elif venue.cong_level == 1:
                cv2.circle(self.canvas, self.trans(
                    venue.node.x, venue.node.y), self.venue_radius, self.venue_color[1], -1)
                cv2.putText(self.canvas, '1', self.trans(
                    venue.node.x-5, venue.node.y-5), self.font, 0.5, (255, 255, 255), 1)
            elif venue.cong_level == 2:
                cv2.circle(self.canvas, self.trans(
                    venue.node.x, venue.node.y), self.venue_radius, self.venue_color[2], -1)
                cv2.putText(self.canvas, '2', self.trans(
                    venue.node.x-5, venue.node.y-5), self.font, 0.5, (255, 255, 255), 1)
            elif venue.cong_level == 3:
                cv2.circle(self.canvas, self.trans(
                    venue.node.x, venue.node.y), self.venue_radius, self.venue_color[3], -1)
                cv2.putText(self.canvas, '3', self.trans(
                    venue.node.x-5, venue.node.y-5), self.font, 0.5, (255, 255, 255), 1)
            elif venue.cong_level == 4:
                cv2.circle(self.canvas, self.trans(
                    venue.node.x, venue.node.y), self.venue_radius, self.venue_color[4], -1)
                cv2.putText(self.canvas, '4', self.trans(
                    venue.node.x-5, venue.node.y-5), self.font, 0.5, (255, 255, 255), 1)
            elif venue.cong_level == 5:
                cv2.circle(self.canvas, self.trans(
                    venue.node.x, venue.node.y), self.venue_radius, self.venue_color[5], -1)
                cv2.putText(self.canvas, '5', self.trans(
                    venue.node.x-5, venue.node.y-5), self.font, 0.5, (255, 255, 255), 1)
            else:
                raise "venue color error"

    def animate_ordergenerators(self, now):
        for ordergenerator in self.all_ordergenerators:

            state = self.ordergenerator_states[ordergenerator.id]
            # print(state['color'])
            # 检查是否需要重置颜色
            if state['reset_time'] is not None and now >= state['reset_time']:
                state['color'] = self.ordergenerator_color
                state['reset_time'] = None
                state['display_text'] = False
            # print(state['reset_time'])



            for order in self.all_orders:
                # print(order.destination)
                if order.destination.id == ordergenerator.id:
                    # print(1)
                    if order.is_complete==False and abs(order.generation_time - now) <= 12:
                        state['color'] = self.generate_order_color
                        state['reset_time'] = now + 20
                        state['display_text'] = 'green'
                        break
                    elif order.is_complete == True and abs(order.complete_time - now) <= 12:
                        state['color'] = self.complete_order_color
                        state['reset_time'] = now + 20
                        state['display_text'] = 'red'
                        break
            # print(f"OrderGenerator ID: {ordergenerator.id}, Display Text: {state['display_text']}")
            # 绘制 ordergenerator
            cv2.circle(self.canvas, self.trans(ordergenerator.x, ordergenerator.y),
                       self.ordergenerator_radius, state['color'], -1)

            # 显示文本
            if state['display_text']:
                if state['display_text'] == 'green':
                    cv2.putText(self.canvas, 'New', self.trans(ordergenerator.x + 2, ordergenerator.y + 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, state['color'], 1, cv2.LINE_AA)
                elif state['display_text'] == 'red':
                    cv2.putText(self.canvas, 'Arvl', self.trans(ordergenerator.x + 2, ordergenerator.y + 2),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, state['color'], 1, cv2.LINE_AA)

           
    def animate_roads(self):

        for road in self.map.roads:
            if road.node1.id<road.node2.id:
                if road.road_type == False:
                    if road.cong == 0:
                        # normal road and no congestion

                        cv2.line(self.canvas, self.trans(road.node1.x, road.node1.y), self.trans(
                            road.node2.x, road.node2.y), self.road_color[0], self.road_nor_width)
                    elif road.cong == 1:
                        # normal road with congestion rank1

                        cv2.line(self.canvas, self.trans(road.node1.x, road.node1.y), self.trans(
                            road.node2.x, road.node2.y), self.road_color[1], self.road_nor_width)
                    elif road.cong == 2:
                        # normal road with congestion rank2

                        cv2.line(self.canvas, self.trans(road.node1.x, road.node1.y), self.trans(
                            road.node2.x, road.node2.y), self.road_color[2], self.road_nor_width)
                    elif road.cong == 3:
                        # normal road with congestion rank3

                        cv2.line(self.canvas, self.trans(road.node1.x, road.node1.y), self.trans(
                            road.node2.x, road.node2.y), self.road_color[3], self.road_nor_width)
                    elif road.cong == 4:
                        # normal road with congestion rank4

                        cv2.line(self.canvas, self.trans(road.node1.x, road.node1.y), self.trans(
                            road.node2.x, road.node2.y), self.road_color[4], self.road_nor_width)
                    elif road.cong == 5:
                        # normal road with congestion rank5

                        cv2.line(self.canvas, self.trans(road.node1.x, road.node1.y), self.trans(
                            road.node2.x, road.node2.y), self.road_color[5], self.road_nor_width)
                    else:
                        print('Road_color error!!!')
                else:
                    # highways
                    cv2.line(self.canvas, self.trans(road.node1.x, road.node1.y), self.trans(
                        road.node2.x, road.node2.y), self.highway_color, self.road_high_width)
    # def animate_nodes(self):
    #     for node_id, node in all_nodes.items():
    #         # 获取节点的坐标
    #         x, y = node.location.x, node.location.y
    #         # 在画布上绘制一个圆形
    #         cv2.circle(self.canvas, self.trans(node.location.x, node.location.y), self.ordergenerator_radius, self.ordergenerator_color, -1)

    def draw_canvas(self, now):
        self._clear_canvas()
        self.animate_roads()
        self.animate_ordergenerators(now)
        self.animate_meantime(now)
        self.animate_depots()
        self.animate_venues()


        self.animate_trucks()
        
        self.update_canvas()
