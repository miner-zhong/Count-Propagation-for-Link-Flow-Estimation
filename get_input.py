import networkx as nx
import pandas as pd


def get_graph(args):
    data = pd.read_csv(args.f_graph_info)
    graph_info = []
    for i in range(len(data)):
        graph_info.append([str(list(data['edge_index'])[i]),
                           int(list(data['node_from'])[i]),
                           int(list(data['node_to'])[i]),
                           int(list(data['length'])[i])])
    G = nx.DiGraph()
    for info in graph_info:
        G.add_edge(info[1], info[2], name=info[0], length=info[3])
    return G



def get_transitions(args):
    data = pd.read_csv(args.f_transition)
    transitions = []
    for i in range(len(data)):
        transitions.append(['s' + str(list(data['state_from'])[i]), 's' + str(list(data['state_to'])[i])])
    return transitions



def get_observed_data(args):
    data = pd.read_csv(args.f_path_flow)
    pflow = []
    for i in range(len(data)):
        path = []
        for j in range(len(list(data['path'])[i].split(',')) - 1):
            path.append(int(list(data['path'])[i].split(',')[j][1:]))
        path.append(int(list(data['path'])[i].split(',')[-1][1:-1]))
        trans = []
        for k in range(len(path) - 1):
            trans.append(['s' + str(path[k]), 's' + str(path[k + 1])])
        flow_sampled = int(list(data['flow_sampled'])[i])
        pflow.append({'path': path, 'trans': trans, 'flow_sampled': flow_sampled})
    data = pd.read_csv(args.f_obs_counts)
    obs_counts = []
    for i in range(len(data)):
        state = 's' + str(list(data['obs_state'])[i])
        flow = int(list(data['observed_nb'])[i])
        obs_counts.append({'state': state, 'flow': flow})
    return (pflow, obs_counts)




def get_true_flow(args):
    data = pd.read_csv(args.f_link_flow_true)
    lflow_true = {}
    for i in range(len(data)):
        state = str(list(data['state'])[i])
        flow = int(list(data['flow'])[i])
        lflow_true[str(state)] = flow
    return lflow_true