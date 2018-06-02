#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 27 20:28:33 2018

@author: miaoyufei
"""

import networkx as nx
import numpy as np
import random
import matplotlib.pyplot as plt
import json
from construct_network import intersections
from construct_network import intersections_and_bridges
from construct_network import bridges

INTERSECTION = 0
BRIDGE = 1


def sample_network():
    #Sample network for modularity calculation
    #@nodes: bridges
    #@edges: exist when two bridges have ending point on same road/super district
    #@edge weight: unweighted
    G = nx.Graph() #create a new graph
    G.add_nodes_from([1,2,3],nodetype = 1) #create nodes based on a list
    G.add_nodes_from([4,5],nodetype = 1)

    # Use the "weight" keyword -- important in some algorithms
    G.add_edge(1, 2)
    G[1][2]['distance'] = 1
    G[1][2]['bridge'] = 10
    G.add_edge(1, 4)
    G[1][4]['distance'] = 2
    G.add_edge(2, 3)
    G[2][3]['distance'] = 3
    G.add_edge(2, 4)
    G[2][4]['distance'] = 5
    G[2][4]['bridge'] = 20
    G.add_edge(2, 5)
    G[2][5]['distance'] = 2
    G.add_edge(3, 5)
    G[3][5]['distance'] = 1
    G[3][5]['bridge'] = 30
    G.add_edge(4, 5)
    G[4][5]['distance'] = 2
    return G
    
def plot(G,attribute):
    #Plot network
    #attribute can be: 'distance','betweenness'
    spr = nx.spring_layout(G)
    edges = G.edges()
    weights = [G[u][v][attribute] for u,v in edges]
    nx.draw(G,spr,edge = edges, width = weights)
    nx.draw_networkx_labels(G,spr)
    plt.show()
    return

def modularity(G,interation, retrofit, sample, high = True):
    
    """
    >>> modularity(sample_network1(),interation=20, retrofit=2, sample=4, high = True)
    [[5, 3], [3, 5], [5, 2], [2, 5]]
    #Compute modularity and return list of bridges to retrofit
    #@Input graph G (modularity_network)
    #@Compute modularity for interation times
    #@Each time, define retrofit bridges as set one type, others as another
    #@@If high = True, return the set of bridges to retrofit that gives highest modularity
    #@@Else, return the set of bridges to retrofit that gives lowest modularity
    """
    
    #Convert graph to adjacency matrix in numpy
    A = nx.to_numpy_matrix(G)
    bridge_list = G.nodes()
    n = len(bridge_list)
    #Compute degree matrix, should be symmetric
    rowsum = A.sum(axis = 1)
    colsum = A.sum(axis = 0)
    m = sum(rowsum)[0,0]
    Ki = rowsum
    Kj = colsum
    for count in range(n - 1):
        Ki = np.c_[Ki,rowsum]
        Kj = np.r_[Kj,colsum]
    #Select bridge set, compute modularity, determine set to retrofit
    retrofit_dict ={} #a dict with size = interation(10000), key is a list of sample birdges to retrofit(100), value is its modularity 
    retrofit_set = [] #a list of sample lists (100), each is retrofit bridges to retrofit (100)  
    for i in range (interation):
        #Get 5 bridges subset for retrofit (type1)
        slice_retrofit = random.sample(bridge_list, retrofit)#retrofit 5 bridges per time
        #Get all other bridges subset (type2)
        slice_other = [x for x in bridge_list if x not in slice_retrofit]
        #Compute community matrix, element of same type = 1
        C = np.zeros([n,n])
        for a in range(n):
            for b in range(n):
                if a in slice_retrofit and b in slice_retrofit:
                    C[a,b] = 1 
                elif a in slice_other and b in slice_other:
                    C[a,b] = 1
        M = np.multiply(Ki,Kj)/(2*m)
        M = np.subtract(A,M)
        M = np.multiply(M,C)
        modularity = np.sum(M)/(2*m)
        print(modularity, slice_retrofit)
        retrofit_dict[json.dumps(slice_retrofit)] = modularity #store list as string 
                                                               #this is because dict doesn't take list as key
        if high:
            retrofit_set = sorted(retrofit_dict.keys(),key = lambda x:retrofit_dict[x],reverse = True)[:sample]
            retrofit_set = [json.loads(x) for x in retrofit_set] #convert string back to list
        else:
            retrofit_set = sorted(retrofit_dict.keys(),key = lambda x:retrofit_dict[x],reverse = False)[:sample]
            retrofit_set = [json.loads(x) for x in retrofit_set] #convert string back to list
    return (retrofit_set)
    

def bridge_node_betweenness(G, retrofit):
    #Compute node betweenness centrality and return list of bridges to retrofit
    #@Input graph G (betweenness network)
    #@@Return retrofit number of bridges with highest betweenness centrality among all bridges
    #compute betweenness centrality for all nodes, distance considered in finding shortest path
    bb = nx.betweenness_centrality(G, weight = 'distance', normalized=False)
    #append betweenness centrality to attribute of nodes
    nx.set_node_attributes(G, name = 'betweenness', attributes = bb)
    #create subgraph of G that includes only bridge nodes
    bridge_nodes = [x for x in G.nodes() if G.nodes(data=True)[x]['nodetype'] == BRIDGE] #==BRIDGE
    G = G.subgraph(bridge_nodes)
    #list of bridge nodes sorted based on betweenness centrality from high to low
    sorted_nodes = sorted(G.nodes(), key = lambda x:G.node[x]['betweenness'],reverse=True)
    retrofit_set = sorted_nodes[:retrofit]
    return (retrofit_set)

def bridge_edge_betweenness(G, retrofit): 
    #Compute edge betweenness centrality and return list of bridges to retrofit
    #@Input graph G (betweenness network)
    #@@Return retrofit number of bridges with highest betweenness centrality among all bridges
    #compute betweenness centrality for all nodes, distance considered in finding shortest path
    bb = nx.edge_betweenness_centrality(G, normalized=False, weight='distance')
    nx.set_edge_attributes(G, name = 'betweenness', attributes = bb)
    #create a list of edges that have bridge(s) 
    bridge_edges = [(u,v) for (u,v) in G.edges() if 'bridge' in G.edge[u][v].keys()]  
    #list of edges sorted based on betweenness centrality from high to low, edge with bridges will be prioritized
    sorted_edges = sorted(G.edges(), key = lambda (u,v):G.edge[u][v]['betweenness'] if (u,v) in bridge_edges else -1,reverse=True)
    retrofit_set = sorted_edges[:retrofit]
    retrofit_set = [G.edge[u][v]['bridge'] for (u,v) in retrofit_set]
    return (retrofit_set)
    
def local_clustering(G, retrofit):
    #Compute clustering coefficient for nodes
    #Assign the lower one to the edge that connects the two end points
    #@Input graph G (betweenness network)
    #@@Return retrofit number of bridges with lowest local clustering coefficient
    #compute local clustering coefficient for all nodes, weight should be traffic flow   
    cc = nx.clustering(G,weight = 'distance')
    #append clustering coefficient to attribute of nodes
    nx.set_node_attributes(G, name = 'cluster_coefficient', attributes = cc)
    #create a list of edges that have bridge(s) 
    bridge_edges = [(u,v) for (u,v) in G.edges() if 'bridge' in G.edge[u][v].keys()]  
    #append clustering coefficient to attribute of bridge edges (choose min of end points)    
    for (u,v) in bridge_edges:
        G[u][v]['cluster_coefficient'] = min(G.node[u]['cluster_coefficient'],G.node[v]['cluster_coefficient'])
    #list of edges sorted based on clustering coefficient from low to high, edge with bridges will be prioritized
    sorted_edges = sorted(G.edges(), key = lambda (u,v):G.edge[u][v]['cluster_coefficient'] if (u,v) in bridge_edges else 2,reverse=False)
    retrofit_set = sorted_edges[:retrofit]
    retrofit_set = [G.edge[u][v]['bridge'] for (u,v) in retrofit_set]
    return (retrofit_set)
    
if __name__ == '__main__':
    G = nx.read_gpickle("quick_traffic_model/input/graphMTC_CentroidsLength3int.gpickle")
    print ('finished loading road network')
    betweenness_network = intersections(G) #also the local-clustering network
    #should have edge attribute 'bridge' that gives bridge id 
    middle = intersections_and_bridges(betweenness_network)
    modularity_network = bridges(middle)
    #should have node id that give bridge id 
    ##modularity is killing my computer
    #road_adjacent = modularity(modularity_network,interation=10000, retrofit=100, sample=100, high = True)
    #road_non_adjacent = modularity(modularity_network,interation=10000, retrofit=100, sample=100, high = False)
    high_betweenness = bridge_edge_betweenness(betweenness_network, retrofit=100)
    low_clustering = local_clustering(betweenness_network, retrofit=100)