# -*- coding: utf-8 -*-
"""
Created on Fri Jun  1 14:22:18 2018

@author: miaoyufei
"""

import pickle
import networkx as nx
import matplotlib.pyplot as plt
#matplotlib inline

INTERSECTION = 0
BRIDGE = 1
# Load road network
G = nx.read_gpickle("quick_traffic_model/input/graphMTC_CentroidsLength3int.gpickle")
print ('finished loading road network')


def intersections(G): 
# Make intersections node type 0 to separate from bridges
#@G is the original road network 
    for n in G.nodes():
        G.node[n]['nodetype'] = INTERSECTION # intersection, not bridge
    print 'finished loading road network'
    G = G.to_undirected()
    # Open bridge database
    bridges_dict = None
    with open('quick_traffic_model/input/20140114_master_bridge_dict.pkl','rb') as f:
        bridges_dict = pickle.load(f)
    # Add list of bridges on each road segment
    for b_num in bridges_dict.keys():
        bridge_edges = bridges_dict[b_num]['a_b_pairs_direct']
        new_id = str(bridges_dict[b_num]['new_id'])
        for [u,v] in bridge_edges:
            G.edge[str(u)][str(v)]['bridges'].append('b' + new_id)
    intersections_G = G.copy()
    return (intersections_G)


def intersections_and_bridges(G):
# For each bridge, make a new node connecting to the proper intersections
# in series, needs to be changed to in parallel for modularity to work properly
#@G is the intersections_G processed in previous function
    for (u,v) in G.edges():
        if len(G.edge[u][v]['bridges']) > 0:
            bridge_list = G.edge[u][v]['bridges']
            for bridge in bridge_list:
                data = G.get_edge_data(u, v)
                data['bridges'] = None
                data['distance'] = data['distance']/2
                data['distance_0'] = data['distance_0']/2
                data['t_0'] = data['t_0']/2
                G.add_node(bridge, nodetype=BRIDGE)
                G.add_edge(u, bridge, attr_dict = data)
                G.add_edge(bridge, v, attr_dict = data)
            G.remove_edge(u,v)
    print ('finished adding bridges')
    bridges_and_intersections_G = G.copy()
    return (bridges_and_intersections_G)
    
    
def bridges(G):
# Remove the intersections
#@G is the bridges_and_intersections_G processed in previous function
    for n in G.nodes():
        if G.node[n]['nodetype'] == INTERSECTION:
            adj_nodes = G.neighbors(n)
            for v1 in range(len(adj_nodes)):
                for v2 in range(v1+1, len(adj_nodes)):
                    v1n = adj_nodes[v1]
                    v2n = adj_nodes[v2]
                    if G.node[v1n]['nodetype'] == BRIDGE and G.node[v2n]['nodetype'] == BRIDGE:
                        G.add_edge(v1n, v2n)
            G.remove_node(n)
    print 'finished removing road intersections'
    bridges_G = G.copy()
    return (bridges_G)
