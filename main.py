
'''

Algorithm for "Brunauer, Richard, Stefan Henneberger, and Karl Rehrl. "Network-wide link flow estimation through probe
vehicle data supported count propagation." 2017 IEEE 20th International Conference on Intelligent Transportation
Systems (ITSC). IEEE, 2017."

Written by Miner Zhong.


first sepcify input data in args.py
there are 4 observation scenarios:
    all of these scenarios share the same set of observed link flow (30% of the entire link set)
    for observed trajectories:
    -- obs_s1: All path sampling rate = 100%, also, add paths to make the observed trajectories cover all possible
                transitions in the network
    -- obs_s2: All path sampling rate = 100%
    -- obs_s3: Among the entire path set, sampling rate range from 20%-40%
    -- obs_s4: Among the entire path set, sampling rate range from 5%-20%

then run this program

when finished, the output file contains link flow estimation results

'''



import pandas as pd
from get_input import *
from propagation import *

import argparse
from args import get_args
parser = argparse.ArgumentParser()
get_args(parser)
args = parser.parse_args()


def main():

    # get input data
    G = get_graph(args)
    transitions = get_transitions(args)
    lflow_true = get_true_flow(args)
    (pflow, obs_counts) = get_observed_data(args)

    # link flow from observed trajectory
    lflow = {}
    for l in range(len(G.edges())):
        lflow['s' + str(str(l))] = 0
        for p in pflow:
            if (l in p['path']):
                lflow['s' + str(str(l))] += p['flow_sampled']

    # transition flow from observed trajectory
    tflow = {}
    for t in transitions:
        tflow[str(t)] = 0
        for p in pflow:
            if (t in p['trans']):
                tflow[str(t)] += p['flow_sampled']


    # observed and unobserved links
    obs_states = []
    for info in obs_counts:
        obs_states.append(info['state'])
    unobs_states = []
    for i in range(len(G.edges())):
        if not ('s' + str(i) in obs_states):
            unobs_states.append('s' + str(i))


    # calculate
    turning_prob = calc_turning_prob(transitions, tflow)

    arriving_prob = calc_arriving_prob(transitions, tflow)

    gain_loss_ratio = calc_gain_loss_ratio(transitions, turning_prob, arriving_prob, lflow)

    # propagation
    propag_result, quality_result = propag(G, obs_states, unobs_states, lflow,
                                           arriving_prob, turning_prob, gain_loss_ratio)

    # get results
    final_quality = get_quality_result(quality_result, unobs_states)

    final_result = get_final_result(propag_result, final_quality, unobs_states)

    # output
    output = {'state': [], 'flow_true': [], 'flow_predict': [], 'missing_ratio': []}
    for k in final_result.keys():
        output['state'].append(k)
        output['flow_true'].append(lflow_true[k])
        output['flow_predict'].append(final_result[k]['flow'])
        output['missing_ratio'].append(final_result[k]['missing ratio'])
    pd.DataFrame(output).to_csv(args.f_output, index=False)
    print('done')





if __name__ == "__main__":
    main()