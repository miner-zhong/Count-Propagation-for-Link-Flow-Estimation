import networkx as nx
import pandas as pd
from util import *



def propag(G, obs_states, unobs_states, lflow, arriving_prob, turning_prob, gain_loss_ratio):
    propag_result = {}
    quality_result = {}

    for z in unobs_states[:]:
        propag_result[str(z)] = {}
        quality_result[str(z)] = {}

        # find all possible 's'
        ls_s = []
        start = 'n/a'
        end = 'n/a'
        for e in G.edges():
            if (z == str(G[e[0]][e[1]]['name'])):
                start = e[1]
        for s in obs_states:
            for e2 in G.edges():
                if (s == str(G[e2[0]][e2[1]]['name'])):
                    end = e2[0]
            if (nx.has_path(G, start, end)):
                ls_s.append(s)

        # propagation value
        value_forward = 0
        value_backward = 0

        # quality value
        completeness_forward = 0
        completeness_backward = 0

        propagation_info_forward = {}
        propagation_info_backward = {}

        s_no_propag_info_forward = []
        s_no_propag_info_backward = []

        for s in ls_s:
            qs = lflow[str(s)]

            # forward--------------------------------------
            all_paths_z_s = get_all_paths(G, end=s, start=z)
            all_paths_z_s_f1 = get_feasible_paths_1(all_paths_z_s, arriving_prob)
            all_paths_z_s_f2 = get_feasible_paths_2_f(all_paths_z_s_f1, obs_states)
            all_paths_z_s_f3 = []
            for p in all_paths_z_s_f2:
                if (p[-1] == s):
                    all_paths_z_s_f3.append(p)

            # propagation
            value_f_sum = 0
            for p in all_paths_z_s_f3:
                value_f_multiply = 1
                ls_tran = []
                for i in range(len(p) - 1):
                    ls_tran.append([p[i], p[i + 1]])
                for t in ls_tran:
                    value_f_multiply *= (arriving_prob[str(t)] / gain_loss_ratio[str(t)])
                value_f_sum += value_f_multiply
            value_for_s = value_f_sum * qs
            value_forward += value_for_s

            # quality--completeness
            if (len(all_paths_z_s_f3) == 0):
                s_no_propag_info_forward.append(s)
            else:
                sum_f = 0
                for p in all_paths_z_s_f3:
                    multiply = 1
                    ls_tran = []
                    for i in range(len(p) - 1):
                        ls_tran.append([p[i], p[i + 1]])
                    for t in ls_tran:
                        multiply *= turning_prob[str(t)]
                    sum_f += multiply
                completeness_forward += sum_f

            # quality--propagation
            if (len(all_paths_z_s_f3) == 0):
                propagation_info_forward[str(s)] = 'no info'
            else:
                info_p_f = []
                for p in all_paths_z_s_f3:
                    ptp = 1
                    ls_tran = []
                    for i in range(len(p) - 1):
                        ls_tran.append([p[i], p[i + 1]])
                    for t in ls_tran:
                        ptp *= turning_prob[str(t)]
                    lp1 = get_lp1_forward(p, gain_loss_ratio, arriving_prob)
                    info_p_f.append({'denominator': ptp, 'numerator': ptp / (1 + lp1)})
                propagation_info_forward[str(s)] = info_p_f


            # backward--------------------------------------
            all_paths_s_z = get_all_paths(G, end=z, start=s)
            all_paths_s_z_f1 = get_feasible_paths_1(all_paths_s_z, turning_prob)
            all_paths_s_z_f2 = get_feasible_paths_2_b(all_paths_s_z_f1, obs_states)
            all_paths_s_z_f3 = []
            for p in all_paths_s_z_f2:
                if (p[-1] == z):
                    all_paths_s_z_f3.append(p)

            # propagation
            value_b_sum = 0
            for p in all_paths_s_z_f3:
                value_b_multiply = 1
                ls_tran = []
                for i in range(len(p) - 1):
                    ls_tran.append([p[i], p[i + 1]])
                for t in ls_tran:
                    value_b_multiply *= (turning_prob[str(t)] * gain_loss_ratio[str(t)])
                value_b_sum += value_b_multiply
            value_for_s = value_b_sum * qs
            value_backward += value_for_s

            # quality--completeness
            if (len(all_paths_s_z_f3) == 0):
                s_no_propag_info_backward.append(s)
            else:
                sum_b = 0
                for p in all_paths_s_z_f3:
                    multiply = 1
                    ls_tran = []
                    for i in range(len(p) - 1):
                        ls_tran.append([p[i], p[i + 1]])
                    for t in ls_tran:
                        multiply *= arriving_prob[str(t)]
                    sum_b += multiply
                completeness_backward += sum_b

            # quality--propagation
            if (len(all_paths_s_z_f3) == 0):
                propagation_info_backward[str(s)] = 'no info'
            else:
                info_p_b = []
                for p in all_paths_s_z_f3:
                    pap = 1
                    ls_tran = []
                    for i in range(len(p) - 1):
                        ls_tran.append([p[i], p[i + 1]])
                    for t in ls_tran:
                        pap *= arriving_prob[str(t)]
                    lp1 = get_lp1_backward(p, gain_loss_ratio, turning_prob)
                    info_p_b.append({'denominator': pap, 'numerator': pap / (1 + lp1)})
                propagation_info_backward[str(s)] = info_p_b

        # propagation results
        propag_result[str(z)]['foreward'] = value_forward
        propag_result[str(z)]['backward'] = value_backward


        if (completeness_forward == 0):
            quality_result[str(z)]['completeness_forward'] = 'no propag info'
        else:
            quality_result[str(z)]['completeness_forward'] = completeness_forward

        if (completeness_backward == 0):
            quality_result[str(z)]['completeness_backward'] = 'no propag info'
        else:
            quality_result[str(z)]['completeness_backward'] = completeness_backward

        numerator_f = 0
        denominator_f = 0
        for s in ls_s:
            if not (propagation_info_forward[str(s)] == 'no info'):
                for f in propagation_info_forward[str(s)]:
                    numerator_f += f['numerator']
                    denominator_f += f['denominator']
        if (denominator_f == 0):
            quality_result[str(z)]['propagation_forward'] = 'no propag info'
        else:
            quality_result[str(z)]['propagation_forward'] = numerator_f / denominator_f

        numerator_b = 0
        denominator_b = 0
        for s in ls_s:
            if not (propagation_info_backward[str(s)] == 'no info'):
                for b in propagation_info_backward[str(s)]:
                    numerator_b += b['numerator']
                    denominator_b += b['denominator']
        if (denominator_b == 0):
            quality_result[str(z)]['propagation_backward'] = 'no propag info'
        else:
            quality_result[str(z)]['propagation_backward'] = numerator_b / denominator_b

        # quality results
        quality_result[str(z)]['ratio_s_without_propag_info_forward'] = len(s_no_propag_info_forward) / len(ls_s)
        quality_result[str(z)]['ratio_s_without_propag_info_backward'] = len(s_no_propag_info_backward) / len(ls_s)

    return propag_result, quality_result




def get_quality_result(quality_result, unobs_states):
    final_quality = {}
    for z in unobs_states:
        final_quality[str(z)] = {}
        if (quality_result[str(z)]['completeness_forward'] == 'no propag info' or
                quality_result[str(z)]['propagation_forward'] == 'no propag info'):
            final_quality[str(z)]['forward'] = 'no propag info'
            final_quality[str(z)]['forward_missing_ratio'] = quality_result[str(z)][
                'ratio_s_without_propag_info_forward']
        else:
            final_quality[str(z)]['forward'] = quality_result[str(z)]['completeness_forward'] * quality_result[str(z)][
                'propagation_forward']
            final_quality[str(z)]['forward_missing_ratio'] = quality_result[str(z)][
                'ratio_s_without_propag_info_forward']

        if (quality_result[str(z)]['completeness_backward'] == 'no propag info' or
                quality_result[str(z)]['propagation_backward'] == 'no propag info'):
            final_quality[str(z)]['backward'] = 'no propag info'
            final_quality[str(z)]['backward_missing_ratio'] = quality_result[str(z)][
                'ratio_s_without_propag_info_backward']
        else:
            final_quality[str(z)]['backward'] = quality_result[str(z)]['completeness_backward'] * \
                                                quality_result[str(z)]['propagation_backward']
            final_quality[str(z)]['backward_missing_ratio'] = quality_result[str(z)][
                'ratio_s_without_propag_info_backward']
    return final_quality





def get_final_result(propag_result, final_quality, unobs_states):
    final_result = {}
    for z in unobs_states:
        final_result[str(z)] = {}
        if not (final_quality[str(z)]['forward'] == 'no propag info' or final_quality[str(z)]['backward'] == 'no propag info'):
            if (final_quality[str(z)]['forward'] == 'no propag info' > final_quality[str(z)]['backward'] == 'no propag info'):
                final_result[str(z)]['flow'] = propag_result[str(z)]['foreward']
                final_result[str(z)]['missing ratio'] = final_quality[str(z)]['forward_missing_ratio']
            else:
                final_result[str(z)]['flow'] = propag_result[str(z)]['backward']
                final_result[str(z)]['missing ratio'] = final_quality[str(z)]['backward_missing_ratio']
        else:
            if (final_quality[str(z)]['forward'] == 'no propag info'):
                if not (final_quality[str(z)]['backward'] == 'no propag info'):
                    final_result[str(z)]['flow'] = propag_result[str(z)]['backward']
                    final_result[str(z)]['missing ratio'] = final_quality[str(z)]['backward_missing_ratio']
                else:
                    final_result[str(z)]['flow'] = 'no propag info'
                    final_result[str(z)]['missing ratio'] = 1
            else:
                final_result[str(z)]['flow'] = propag_result[str(z)]['foreward']
                final_result[str(z)]['missing ratio'] = final_quality[str(z)]['forward_missing_ratio']
    return final_result


