import networkx as nx


def calc_turning_prob(transitions, tflow):
    turning_prob = {}
    for t in transitions:
        denominator = 0
        for t2 in transitions:
            if (t2[0] == t[0]):
                denominator += tflow[str(t2)]
        if (tflow[str(t)] == 0):
            turning_prob[str(t)] = 'no flow at this transition'
        else:
            turning_prob[str(t)] = tflow[str(t)] / denominator
    return turning_prob



def calc_arriving_prob(transitions, tflow):
    arriving_prob = {}
    for t in transitions:
        denominator = 0
        for t2 in transitions:
            if (t2[1] == t[1]):
                denominator += tflow[str(t2)]
        if (tflow[str(t)] == 0):
            arriving_prob[str(t)] = 'no flow at this transition'
        else:
            arriving_prob[str(t)] = tflow[str(t)] / denominator
    return arriving_prob



def calc_gain_loss_ratio(transitions, turning_prob, arriving_prob, lflow):
    gain_loss_ratio = {}
    for t in transitions:
        if not (type(turning_prob[str(t)]) == str or type(arriving_prob[str(t)]) == str):
            outflow = lflow[str(t[1])]
            inflow = lflow[str(t[0])]
            gain_loss_ratio[str(t)] = (outflow * arriving_prob[str(t)]) / (inflow * turning_prob[str(t)])
        else:
            gain_loss_ratio[str(t)] = 1.0
    return gain_loss_ratio




def check_repeat(G, s1, s2):
    repeat = False
    for e in G.edges():
        if (s1 == str(G[e[0]][e[1]]['name'])):
            info_1 = [e[0], e[1]]
        if (s2 == str(G[e[0]][e[1]]['name'])):
            info_2 = [e[0], e[1]]
    if (info_1[0] == info_2[1] and info_1[1] == info_2[0]):
        repeat = True
    return repeat


def get_all_paths(G, end, start):
    for e in G.edges():
        if (start == str(G[e[0]][e[1]]['name'])):
            init = e[1]
        if (end == str(G[e[0]][e[1]]['name'])):
            term = e[0]

    ls_paths = []
    if (init == term):
        ls_paths.append([start, end])
    else:
        for p in nx.all_simple_paths(G, init, term, cutoff=None):
            path = [start]
            for i in range(len(p) - 1):
                path.append(G[p[i]][p[i + 1]]['name'])
            path.append(end)
            ls_paths.append(path)

    ls_paths_final = []
    for p in ls_paths:
        repeat = False
        for j in range(len(p) - 1):
            if (check_repeat(G, p[j], p[j + 1])):
                repeat = True
        if (repeat == False):
            ls_paths_final.append(p)

    return ls_paths_final



def get_feasible_paths_1(all_paths, prob):  # stop: indefinite probability
    all_paths_feasible = []

    temp_list = []

    for p in all_paths:
        ls_tran = []
        for i in range(len(p) - 1):
            ls_tran.append([p[i], p[i + 1]])

        feasible_tran = []
        flag = True
        for t in ls_tran:
            if (flag == False):
                break
            if not (type(prob[str(t)]) == str):
                feasible_tran.append(t)
            else:
                flag = False

        if (len(feasible_tran) > 0):
            p_new = []
            for i in range(len(feasible_tran)):
                p_new.append(feasible_tran[i][0])
            p_new.append(feasible_tran[-1][1])
            temp_list.append(p_new)

        for p in temp_list:
            if not (p in all_paths_feasible):
                all_paths_feasible.append(p)

    return all_paths_feasible



def get_feasible_paths_2_f(all_paths, obs_states):  # stop: obs_state(forward)
    all_paths_feasible = []

    temp_list = []
    for p in all_paths:
        p_new = []
        flag = True
        for s in p:
            if (flag == False):
                break
            else:
                if not (s in obs_states):
                    p_new.append(s)
                else:
                    p_new.append(s)
                    flag = False
        if (len(p_new) > 1):
            temp_list.append(p_new)

    for p in temp_list:
        if not (p in all_paths_feasible):
            all_paths_feasible.append(p)

    return all_paths_feasible



def get_feasible_paths_2_b(all_paths, obs_states):  # stop: obs_state(backward)
    all_paths_feasible = []

    temp_list = []
    for p in all_paths:
        p_new = [p[0]]
        flag = True
        for s in p[1:]:
            if (flag == False):
                break
            if not (s in obs_states):
                p_new.append(s)
            else:
                p_new.append(s)
                flag = False
        if (len(p_new) > 1):
            temp_list.append(p_new)

    for p in temp_list:
        if not (p in all_paths_feasible):
            all_paths_feasible.append(p)

    return all_paths_feasible



def get_lp1_backward(path, gain_loss_ratio, turning_prob):
    ls_tran = []
    for i in range(len(path) - 1):
        ls_tran.append([path[i], path[i + 1]])

    lsk = {}
    m = len(ls_tran)
    lsk[str(m)] = abs(gain_loss_ratio[str(ls_tran[-1])] - 1)

    order = []
    for j in range(m - 1):
        order.append((m - 1) - j)

    for o in order:
        lsk[str(o)] = lsk[str(o + 1)] * turning_prob[str(ls_tran[o - 1])] + abs(
            gain_loss_ratio[str(ls_tran[o - 1])] - 1)

    return lsk[str(1)]


def get_lp1_forward(path, gain_loss_ratio, arriving_prob):
    ls_tran = []
    for i in range(len(path) - 1):
        ls_tran.append([path[i], path[i + 1]])

    lsk = {}
    m = len(ls_tran)
    lsk[str(m)] = abs(gain_loss_ratio[str(ls_tran[-1])] - 1)

    order = []
    for j in range(m - 1):
        order.append((m - 1) - j)

    for o in order:
        lsk[str(o)] = lsk[str(o + 1)] * arriving_prob[str(ls_tran[o - 1])] + abs(
            gain_loss_ratio[str(ls_tran[o - 1])] - 1)

    return lsk[str(1)]
