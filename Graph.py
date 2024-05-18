
class Road():

    def __init__(self, node1=None, node2=None, weight=None):
        self.node1: int = node1
        self.node2: int = node2
        self.ind: int
        self.velocity_limit: float
        self.length: float

    def __str__(self):
        return "vertex_set: {0}, weight: {1}".format(self.vertex_set, self.weight)


class Graph:

    def __init__(self, edges, vertex):
        """
        Args:
            edges (List<Edge>): the key of every edge is the address of the tuple.
            vertex (List<Integer>): the key of every vertice.
        """
        self.edges = edges
        self.vertex = vertex

    
