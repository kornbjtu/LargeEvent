import numpy as np
import pandas as pd
from Graph import *

def init_graph(file_path: str):

    df = pd.read_excel(file_path, header=None)
    all_nodes = {}
    all_roads = []

    
    ####################### Get Nodes ############################
    for index, row in df.iloc[1:].iterrows():

        node = Node(x=row[0], y=row[1], id=index)
        all_nodes[index] = node


    ####################### Get Roads ###############################

    road_type_to_sl = {True: 70, False: 30} # True: the express way, False: Normal In-city way

    for i in range(1, df.shape[0]):
        for j in range(3, df.shape[1]):

            if pd.notna(df.iloc[i, j]):
                if df.iloc[i, j] == 1:
                    road_type = False
                elif df.iloc[i, j] == 2:
                    road_type = True
                else:
                    continue  

                all_roads.append(Road(all_nodes[i], all_nodes[j-2], road_type_to_sl[road_type]))
    
    
    ####################### Create Graph ###############################

    return Graph(all_roads, all_nodes.values())



graph = init_graph("node_matrix.xlsx")
print(graph.shortest_path(14, 15))