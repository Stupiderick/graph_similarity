import itertools
import networkx as nx
from networkx.algorithms import bipartite
import numpy as np
import pandas as pd
import random
import matplotlib.pyplot as plt
from scipy import spatial

def get_random_capacity_undirected_graph(n, m, max_cap=20):
    '''
    Returns a `G_{n,m}` random directed graph with capacity.

    In the `G_{n,m}` model, a graph is chosen uniformly at random from the set
    of all graphs with `n` nodes and `m` edges.

    Partial credit to NetworkX.

    Parameters
    ----------
    n : int
        The number of nodes.
    m : int
        The number of edges.
    max_cap : int, optional
        Maximum capacity allowed for every edge (default=20).

    '''
    G = nx.Graph()

    G.add_nodes_from(range(n))
    G.name = "gnm_random_graph(%s,%s)"%(n, m)

    if n == 1:
        return
    max_edges = n * (n - 1)
    if m >= max_edges:
        return complete_graph(n, create_using=G)

    nlist = list(G.nodes())
    edge_count = 0

    while edge_count < m:
        # generate random edge,u,v
        u = random.choice(nlist)
        v = random.choice(nlist)

        if u == v or G.has_edge(u, v):
            continue
        else:
            capa = random.randint(1, max_cap)
            G.add_edge(u, v, weight=capa)
            edge_count += 1

    return G

def get_neighbor_edges(G, n):
    '''
    Input a graph and number of nodes
    ---------------------------------------
    Return the list of the neighbors of nodes.
    '''
    edge_list = G.edges.data('weight', default=1)
    neighbor = []
    [neighbor.append([]) for i in range(n)]
    # build a node list with adjacent weight edges.
    [(neighbor[edge[0]].append(edge[2]), neighbor[edge[1]].append(edge[2])) for edge in edge_list]

    for i in range(len(neighbor)):
        neighbor[i] = sorted(neighbor[i], reverse=True)

    return neighbor

def closest_node(nl1, nl2):
    '''
    Input two neighbor lists of two graphs
    nl1: the graph as subject
    nl2: the graph as comparable
    -----------------------------------
    Return: list of the closest node list
    '''
    closest_node_list = []
    count = 0
    for i in nl1:
        dist_list = []
        for j in nl2:
            if len(i) == len(j):
                dist_list.append(spatial.distance.euclidean(i, j))
            elif len(i) < len(j):
                [i.append(0) for k in range(len(j)-len(i))]
                dist_list.append(spatial.distance.euclidean(i, j))
            else:
                [j.append(0) for k in range(len(i)-len(j))]
                dist_list.append(spatial.distance.euclidean(i, j))
        closest_node_list.append([count, dist_list.index(min(dist_list))])
        count += 1
    return closest_node_list


def graphs2bipartite_weight(nei1, nei2):
    nodes1 = list(range(len(nei1)))
    nodes2 = list(range(len(nei2)))

    G_bp = nx.Graph()
    [G_bp.add_node(i+1) for i in nodes1]
    [G_bp.add_node(-j-1) for j in nodes2]

    for i in range(len(nei1)):
        for j in range(len(nei2)):
            node_i = nei1[i]
            node_j = nei2[j]
            if len(node_i) == len(node_j):
                G_bp.add_edge(i+1, -j-1, weight=1/(spatial.distance.euclidean(node_i, node_j)+0.001))
            if len(node_i) < len(node_j):
                [node_i.append(0) for k in range(len(node_j)-len(node_i))]
                G_bp.add_edge(i+1, -j-1, weight=1/(spatial.distance.euclidean(node_i, node_j)+0.001))
            else:
                [node_j.append(0) for k in range(len(node_i)-len(node_j))]
                G_bp.add_edge(i+1, -j-1, weight=1/(spatial.distance.euclidean(node_i, node_j)+0.001))
    return G_bp


def shortest_path_dist(G1, G2, best_fit):
    '''
    Get shortest paths from source to sink, then delete the shortest path, then
      do again.
    '''
    source_pair = random.choice(best_fit)
    sink_pair = random.choice(best_fit)
    # if source == sink, re-sample
    while source_pair == sink_pair:
        sink_pair = random.choice(best_fit)

    G1_source = 0
    G1_sink = 0
    G2_source = 0
    G2_sink = 0
    if source_pair[0] > 0:
        G1_source = source_pair[0] - 1
        G2_source = -source_pair[1] - 1
    else:
        G1_source = source_pair[1] - 1
        G2_source = -source_pair[0] - 1
    if sink_pair[0] > 0:
        G1_sink = sink_pair[0] - 1
        G2_sink = -sink_pair[1] - 1
    else:
        G1_sink = sink_pair[1] - 1
        G2_sink = -sink_pair[0] - 1

    G1_weight_list = []
    G2_weight_list = []

    # iterately find shortest path
    iter = len(best_fit) ** 2
    for i in range(iter):
        has_path1 = nx.has_path(G1, G1_source, G1_sink)
        has_path2 = nx.has_path(G2, G2_source, G2_sink)

        if has_path1 and has_path2:
            s1 = nx.shortest_path(G1, source=G1_source, target=G1_sink)
            w1 = []
            for j in range(len(s1)-1):
                # get edge weight and remove edge
                w1.append(G1[s1[j]][s1[j+1]]['weight'])
                G1.remove_edge(s1[j], s1[j+1])
            G1_weight_list.append(sum(w1))

            s2 = nx.shortest_path(G2, source=G2_source, target=G2_sink)
            w2 = []
            for j in range(len(s2)-1):
                # get edge weight and remove edge
                w2.append(G2[s2[j]][s2[j+1]]['weight'])
                G2.remove_edge(s2[j], s2[j+1])
            G2_weight_list.append(sum(w2))

        elif has_path1 == False and has_path2 == True:
            print('SPECIAL CASE: Graph 1 does not have enough shortest paths.')
            break

        elif has_path1 == True and has_path2 == False:
            print('SPECIAL CASE: Graph 2 does not have enough shortest paths.')
            break

        else:
            break

    return spatial.distance.euclidean(G1_weight_list, G2_weight_list)


n = 20
m = 40
mcap = 5

G1 = get_random_capacity_undirected_graph(n, m, max_cap=mcap)
G2 = get_random_capacity_undirected_graph(n, m, max_cap=mcap)

neighbor1 = get_neighbor_edges(G1, n)
neighbor2 = get_neighbor_edges(G2, n)

G_bp = graphs2bipartite_weight(neighbor1, neighbor2)
best_fit = list(nx.max_weight_matching(G_bp))

cnl1 = closest_node(neighbor1, neighbor2)
cnl2 = closest_node(neighbor2, neighbor1)

best_neighbor_list = []
for i in range(len(cnl1)):
    if cnl1[i][0] == cnl2[cnl1[i][1]][1]:
        best_neighbor_list.append([cnl1[i][0], cnl1[i][1]])

shortdist = shortest_path_dist(G1, G2, best_fit)


print('neighbor1', neighbor1)
print('neighbor2', neighbor2)
print('G1->G2, neighbor', cnl1)
print('G2->G1, neighbor', cnl2)
print('G1->G2, mutual neighbor', best_neighbor_list)
print('Closest combo', best_fit)
print('Shortest paths distance', shortdist)

myFile = open('closest_neighbor.csv', 'w+')
myFile.write('Nodes in G1,Closest neighbor in G2\n')
[myFile.write(str(cnl1[i][0]) + ',' + str(cnl1[i][1]) + '\n') for i in range(len(cnl1))]
myFile.write('Nodes in G1,Closest neighbor in G2\n')
[myFile.write(str(cnl2[i][0]) + ',' + str(cnl2[i][1]) + '\n') for i in range(len(cnl2))]
myFile.write('Nodes in G1,Best neighbor in G2\n')
[myFile.write(str(i[0]) + ',' + str(i[1]) + '\n') for i in best_neighbor_list]

myFile.close()

pos1 = nx.circular_layout(G1)
edges = G1.edges()
weights = [G1[u][v]['weight'] for u,v in edges]
weights[:] = [x / (mcap / 10.0) for x in weights]
nx.draw(G1, pos=pos1, edges=edges, width=weights, with_labels=True)
plt.savefig('G1.png')
plt.clf()

pos2 = nx.circular_layout(G2)
edges = G2.edges()
weights = [G2[u][v]['weight'] for u,v in edges]
weights[:] = [x / (mcap / 10.0) for x in weights]
nx.draw(G2, pos=pos2, edges=edges, width=weights, with_labels=True)
plt.savefig('G2.png')
