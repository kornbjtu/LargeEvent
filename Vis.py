import cv2
import numpy as np
from playground import *

class Visualizor:
    def __init__(self):
        self.canvas = np.zeros((700, 700, 3), dtype=np.uint8)
        self.fps = 24
        self.truck_color = ((255, 0, 255))      #truck: purple
        self.depot_color = ((0, 255, 255))      #depot: yellow
        self.venue_color = ((255, 0, 0))        #event venue: blue
        self.ordergenerator = ((0,255,0 ))      #order generator: green
        self.road_nor = ((255, 255, 255))       #normal road: white
        self.road_cong = ((0, 0, 255))          #congested road: red
        self.truck_radius = 2, 


    def update_canvas(self):
        cv2.imshow('Canvas', self.canvas)
        key = cv2.waitKey(int(1000/self.fps))
        return key  # 返回按下的键的ASCII码
    
    def trans(self, x: int, y: int):    #coordinate transfer
        canvas_x = int(5*(x + 60))
        canvas_y = int(700-5*(y + 60))
        cv2.circle(self.canvas, (canvas_x, canvas_y), self.truck_radius, self.truck_color, -1)

    def animate_trucks(self):
        for truck in all_trucks:
            self.trans(truck.location.x, truck.location.y)
        key = self.update_canvas()
        if key != -1:  # 如果用户按下了键，跳出循环
            cv2.destroyAllWindows()
        self.canvas.fill(0)  # 清空画布以便于下一帧
        cv2.waitKey(0)  # 动画结束后，窗口将保持打开状态，直到用户按下任意键
        cv2.destroyAllWindows()



    def draw(self):
        self.animate_trucks()
    
   


vis = Visualizor()
vis.draw()