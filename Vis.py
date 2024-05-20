import cv2
import numpy as np

class Visualizor:
    def __init_git config user.name_(self):
        self.canvas = np.zeros((120, 120, 3), dtype=np.uint8)
        self.fps = 24
        self.truck_color = (0, 0, 255)
        self.truck_radius = 2

    def draw_truck(self, x: int, y: int):
        canvas_x = int(x + 60)
        canvas_y = int(y + 60)
        cv2.circle(self.canvas, (canvas_x, canvas_y), self.truck_radius, self.truck_color, -1)

    def update_canvas(self):
        cv2.imshow('Canvas', self.canvas)
        key = cv2.waitKey(int(1000/self.fps))
        return key  # 返回按下的键的ASCII码
    
    def draw(self, x: int, y: int):
        self.draw_truck(x, y)
        
        while True:  # 无限循环
            key = self.update_canvas()
            if key != -1:  # 如果用户按下了键，跳出循环
                break
                cv2.destroyAllWindows()

visualizor = Visualizor()
visualizor.draw(10, 20)
visualizor.update_canvas()


