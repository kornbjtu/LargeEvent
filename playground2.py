from Graph import *


data_file = "node_matrix.xlsx"
ROAD_SL = {True: 60, False: 30} ## Road type, True: expressway, False: Cityway
map: Graph = init_graph(data_file, ROAD_SL)

# print(map.node(3))

# print(map.shortest_path(25, 18))

print(set([1, 2]) == set([2, 1]))