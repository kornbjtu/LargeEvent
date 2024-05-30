import heapq
from dataclasses import dataclass
from typing import Callable, Dict, List, Union
import numpy as np

@dataclass
class Node:
    x: float
    y: float
    id: int


    def __str__(self):
        return "id: %d, location: x=%.2f, y=%.2f"%(self.id, self.x, self.y)

class Road:

    def __init__(self, node1=None, node2=None, velocity_limit=None):
        self.node1: Node = node1
        self.node2: Node = node2
        self.velocity_limit: float = velocity_limit
        self.length: float = np.sqrt((self.node1.location.x - self.node2.location.x).pow(2) + (self.node1.location.y - self.node2.location.y).pow(2))
    
    def get_weight(self):
        return self.length / self.velocity_limit


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
            self.adj_list[road.node2].append((road.node1, road.get_weight()))  # Assuming undirected graph
        

    def shortest_path(self, start, end): # return a set of road with its distance
        """
        Implements Dijkstra's algorithm to find the shortest path from start to end.

        Args:
            start (int): the starting node.
            end (int): the ending node.

        Returns:
            path (List[int]): the shortest path from start to end.
            distance (float): the total distance of the shortest path.
        """  
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
