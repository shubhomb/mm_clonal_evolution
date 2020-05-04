''' Set up framework for graph model. Contains Subclone, Node and Graph class
    The graph model attempts to describe the similarity between subclone populations. 
    Nodes represent population colonies and contain information on the colony size and fitness.
    

    Graph:

    ----Node-----                        ----Node-----
    |           |                       |            |
    | Colony    |-----------------------|   Colony   |
    | birthtime |                       | birthtime  |
    | edges     |                       |   edges    |
    |-----------|                       |------------|


'''
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx

class Colony():
    """
        Colony object is inside node object
        Each colony contains:
            - Name 
            - Relation [relation with 1, relation with 2, ... ]
            - Alpha 
            - Relative Proportion
    """
    def __init__(self, name, relation, alpha, prop):
        self.name = name       #'drugA' for example 
        self.relation = relation    
        self.alpha = alpha
        self.prop = prop
    
    def get_colony_info(self):
        return (self.name, self.relation, self.alpha, self.prop)
    
    def update_alpha(self, newalpha):
        self.alpha = newalpha
    
    def update_prop(self, newprop):
        self.prop = newprop


class Node():
    """
        Nodes contain the following:
            - Colony Object describing subclone colony 
            - Birthtime 
            - Edges to other nodes
    """
    def __init__(self, colony, birth_time, edges):
        # TODO add assertions to verify edges input
        self.colony = colony # Colony Info
        self.birth_time = birth_time #birth_time
        self.edges = edges  # [(node, edge_weight), (node2, edge_weight), ...]
        self.fitness = 0

    def update_fitness(self):
        # TODO
        # W(v) = 1 - (cost of resis) - alpha*d_A(t) + (1-PA)X(T)
        self.fitness = max(0, 1 - 0.3 - self.colony.alpha*0.3 + (1-self.colony.prop)*0.1)
    
    def get_node_info(self):
        """ Return attributes """
        return (self.colony, self.birth_time, self.edges)
    
    def update_colony(self, newalpha, newprop):
        self.colony.alpha = newalpha
        self.colony.prop = newprop


    def treatment(self):
        # TODO
        pass
    
    def debug(self):
        return self.colony.name
    
    def log(self):
        print(f'Node: {self.debug()}')
        print(f'\t Birthtime: {self.birth_time}')
        print(f'\t Edges' + "*-"*10)
        for edge in self.edges:
            print(f'\t --> {edge[1].colony.name} {edge[1]} with weight {edge[0]}')
        print(f'\t \t Colony name: {self.colony.name}')
        print(f'\t \t Alpha: {self.colony.alpha}')
        print(f'\t \t Prop: {self.colony.prop}')
        print(f'\t \t Fitness: {self.fitness}')
        
    

        

class Graph():
    """
        The graph abstraction is the traditional graph with nodes and edges.
        In particular, this contains functions capable of accessing a node,
        its neighbors, removing the contained object, and storing a new object
        in its place.
        
        We have two representations

        - A networkx graph instance

        -   We represent the graph as an adjacency list.
            The graph is a mapping such that: map[node] = [list of neighbor nodes]
            where [list of neighbor nodes] contains element tuples (edgeweight, node)

        We choose this design for quick lookup for doctor treatment.
    """

    def log(self):
        """ Prints debug information  """
        for node in self.pointmap:
            print(f'Node: {node.debug()} obj: {node}: ')
            for neighbor, weight in self.pointmap[node]:
                print(f'\t {neighbor} with weight {weight}')

    def get_networkx_graph(self):
        G = nx.Graph()
        G.add_nodes_from(self.all_nodes)
        G.add_weighted_edges_from(self.all_edges)
        return G




    def plot(self, title, fitness=False):
        import matplotlib.pyplot as plt
        G = self.get_networkx_graph()
        pos = nx.spring_layout(G)
        # Plot graph with labels as specified by label_dict
        nx.draw(G, pos, labels=self.label_dict, with_labels=True)
        
        # Create edge label Dictionary to label edges:
        edge_labels = nx.get_edge_attributes(G,'weight')
        nx.draw_networkx_edge_labels(G, pos, labels = edge_labels)

        # -------- Draw fitness labels above -----

        pos_higher = {}
        y_offset = 0.07 # Might have to play around with
        for k, v in pos.items():
            pos_higher[k] = (v[0], v[1] + y_offset)        

        fit = {n: f'fitness: {n.fitness}' for n in self.all_nodes}
        nx.draw_networkx_labels(G, pos=pos_higher, font_size=10, font_color='black', labels=fit)
        plt.savefig(f'plots/Plot time {title}.png')
        plt.close()




    def __init__(self, env):
        """
            Given environment object consisting of:
                - names  (list): names of subclone colony
                - relations (matrix): adj matrix representing relations
                - alpha  (list) : of corresponding alpha constants 
                - prop  (list) : of corresponding initial proportions
            
            Has attributes:
                - Point map (dict): mapping from node to its neighbors
                - all_nodes (list): list of all nodes
                - all_edges  (list): list of all edgs
                - networkx_graph (networkx graph):
                - avg fitness
                - label_dict (map) : Maps node to its name (for plotting)

        Initializes a graph instance
        """
        self.pointmap = {} # map[node] = [(node, weight), (node2, eweight), ..]
        self.all_nodes = [] # [Node1, Node2, ... ]
        self.all_edges = [] # [(node1, node2, weight), ...] -- For printing
        self.nxgraph = nx.Graph()
        self.avgfitness = 0

        # Plotting purposes
        self.label_dict = {}  # Maps node to name (for plotting purposes)
        

        #  Initialize all nodes
        for (name, neigh, alpha, prop)  in zip(env.names, env.relations, env.alpha, env.prop):
            new_colony = Colony(name, neigh, alpha, prop)
            new_node = Node(new_colony, 0, [(None, None)])
            self.pointmap[new_node] = [(None, None)]
            self.all_nodes.append(new_node)  
            self.label_dict[new_node] = name

        # Add edges -- hacky way -- can make cleaner:
        ptr = 0 # current node exploring
        for (name, neigh)  in zip(env.names, env.relations):
            curr = 0 #pointer to each neighbor
            neighbor_list = [] #tuples (weight, node) list
            # Iterate through all neighbors and add nonzero ones to list
            for neighbor_weight in neigh:
                if neighbor_weight > 0 and curr != ptr:
                    neighbor_list.append((neighbor_weight, self.all_nodes[curr])) 
                    self.all_edges.append((self.all_nodes[ptr], self.all_nodes[curr], neighbor_weight))
                curr += 1
            self.pointmap[self.all_nodes[ptr]] = neighbor_list
            self.all_nodes[ptr].edges = neighbor_list
            

            ptr+=1
        
        self.nxgraph.add_nodes_from(self.all_nodes)
        self.nxgraph.add_weighted_edges_from(self.all_edges)


    def apply_medicine(self, target_node, depth):
        """
            TODO: 
            Applies treatment to each node within depth [depth]
        """
        nodes = nx.ego_graph(self.nxgraph, target_node, depth, center=False, undirected=True, distance='weight')
        print(f'Considering nodes: ')
        for curr in nodes:
            print(curr.colony.name)

             
            

    def nearest_neighbors(self, x1):
        """ Returns the Node and weight corresponding to the nearest neighbor """
        out_edges = x1.edges
        return min(data, key = lambda t: t[0])


if __name__ == "__main__":
    coord1 = np.array([0, 1, 0])
    progenitor = Node("origin", 0, coord1)
    graph = Graph(dims=3)
    graph.add_node(progenitor)

    for t in range(100):
        eps = np.random.normal(coord1.shape)
        pt = np.random.choice(np.array(list(graph.points.keys())))
        newnode = Node(str(t+1), t, graph.points[pt] + eps)
        graph.add_node(newnode)
    graph.display("random")
