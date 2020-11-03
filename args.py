

path_1 = './data'
path_2 = './data/obs_s1'


def get_args(parser):
    # network information & true flow
    parser.add_argument("--f_graph_info", type=str, default=path_1 + '/graph_info.csv')
    parser.add_argument("--f_transition", type=str, default=path_1 + '/transition_info.csv')
    parser.add_argument("--f_link_flow_true", type=str, default=path_1 + '/link_flow_true.csv')

    # observed data
    parser.add_argument("--f_path_flow", type=str, default=path_2 + '/trajectory_obs.csv')
    parser.add_argument("--f_obs_counts", type=str, default=path_2 + '/link_flow_obs.csv')

    # output
    parser.add_argument("--f_output", type=str, default=path_2 + '/_output.csv')



