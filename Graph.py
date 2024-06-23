import heapq
from dataclasses import dataclass
from typing import Callable, Dict, List, Union
import numpy as np
import pandas as pd


@dataclass
class Node:
    x: float
    y: float
    id: int
    property: str

    def __str__(self):
        return "id: %d, location: x=%.2f, y=%.2f, property: %s" % (self.id, self.x, self.y, self.property)
        # return "id: %d, location: x=%.2f, y=%.2f"%(self.id, self.x, self.y)

    def __hash__(self):
        return self.id

    def __lt__(self, other):
        return self.id < other.id  # This is a simple comparison method for the Node class

    def get_loc(self):
        return self.x, self.y


class Road:

    def __init__(self, node1=None, node2=None, velocity_limit=None, road_type=None):
        self.node1: Node = node1
        self.node2: Node = node2
        self.velocity_limit: float = velocity_limit
        self.cong = 0  # we assume there's no congestion in the road initially
        self.length: float = np.sqrt(np.power(
            (self.node1.x - self.node2.x), 2) + np.power((self.node1.y - self.node2.y), 2)) * 0.1  # km
        self.road_type: bool = road_type

    def get_nodes(self):
        return set([self.node1, self.node2])

    def get_weight(self):
        time_hour = self.length / self.velocity_limit * \
            np.maximum(self.cong, 1)
        return time_hour * 60 * 60

    def get_another_node(self, node):
        if self.node1 == node:
            return self.node2
        elif self.node2 == node:
            return self.node1
        else:
            return None

    def get_pos(self, time: float, from_node: Node):

        time = time / 60 / 60 # convert to hour

        assert from_node == self.node1 or from_node == self.node2
        to_node = self.get_another_node(from_node)

        distance_elapse = time * self.velocity_limit # fix bug here

        from_x, from_y = from_node.get_loc()
        to_x, to_y = to_node.get_loc()

        return (distance_elapse / self.length * to_x + (self.length - distance_elapse) / self.length * from_x,
                distance_elapse / self.length * to_y + (self.length - distance_elapse) / self.length * from_y)


class Graph:

    def __init__(self, roads, nodes):
        """
        Args:
            edges (List<Edge>): the key of every edge is the address of the tuple.
            vertex (List<Integer>): the key of every vertice.
        """
        self.roads: List[Road] = roads
        self.nodes: List[Node] = nodes
        self.adj_list = {node: [] for node in nodes}
        for road in roads:
            self.adj_list[road.node1].append((road.node2, road.get_weight()))
            self.adj_list[road.node2].append(
                (road.node1, road.get_weight()))  # Assuming undirected graph

    def node(self, id: int):
        ### This method is used to unify the id input and node input ###
        if isinstance(id, Node):
            return id
        for n in self.nodes:
            if id == n.id:
                return n
        raise "Node not found!"  # node id Not found

    def get_road(self, node1: Node, node2: Node):
        node1 = self.node(node1)
        node2 = self.node(node2)

        for road in self.roads:
            if road.get_nodes() == set([node1, node2]):
                return road

        raise "None Connection Found"

    def distance(self, node1: Node, node2: Node):
        node1 = self.node(node1)
        node2 = self.node(node2)
        # euciledian distance is used
        return np.sqrt(np.power((node1.x - node2.x), 2) + np.power((node1.y - node2.y), 2))

    def shortest_path(self, start, end):  # return a set of road with its distance
        """
        Implements Dijkstra's algorithm to find the shortest path from start to end.

        Args:
            start (int): the starting node.
            end (int): the ending node.

        Returns:
            path (List[int]): the shortest path from start to end.
            distance (float): the total distance of the shortest path.
        """

        ###### convert id to node if id is used ####
        start = self.node(start)
        end = self.node(end)

        ###### MAIN BODY ########
        # Priority queue to store (distance, node)
        pq = [(0, start)]
        distances = {node: float('inf') for node in self.nodes}
        distances[start] = 0
        previous_nodes = {node: None for node in self.nodes}

        while pq:
            current_distance, current_node = heapq.heappop(pq)

            if current_node == end:
                break

            if current_distance > distances[current_node]:
                continue

            for neighbor, weight in self.adj_list[current_node]:
                distance = current_distance + weight

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    previous_nodes[neighbor] = current_node
                    heapq.heappush(pq, (distance, neighbor))

        path = []
        current_node = end
        while previous_nodes[current_node] is not None:
            path.insert(0, current_node)
            current_node = previous_nodes[current_node]
        path.insert(0, start)

        return path, distances[end]

    def get_type_nodes(self, property: str):

        return [node for node in self.nodes if node.property == property]


def init_graph(file_path: str, road_type_to_sl):

    df = pd.read_excel(file_path, header=None)
    all_nodes = {}
    all_roads = []

    ####################### Get Nodes ############################
    for index, row in df.iloc[1:].iterrows():
        # node = Node(x=row[0], y=row[1], id=index)
        node = Node(x=row[0], y=row[1], id=index, property=row[36])
        all_nodes[index] = node

    ####################### Get Roads ###############################

    for i in range(1, df.shape[0]):
        for j in range(3, df.shape[1] - 1):

            if pd.notna(df.iloc[i, j]):
                if df.iloc[i, j] == 1:
                    road_type = False
                elif df.iloc[i, j] == 2:
                    road_type = True
                else:
                    continue

                all_roads.append(
                    Road(all_nodes[i], all_nodes[j-2], road_type_to_sl[road_type], road_type=road_type))

    ####################### Create Graph ###############################

    return Graph(all_roads, all_nodes.values())

    ######## USE CASE OF DIJKSTRA ALGORITHM ######
    # graph = init_graph("node_matrix.xlsx")
    # print(graph.shortest_path(14, 15))
