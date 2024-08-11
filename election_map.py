from multiprocessing import Pool
import random

from mapel import elections as mapel
import matplotlib as mpl
import numpy as np

from Experiment_framework.Election import Election
from Experiment_framework.Experiment import Experiment
from Experiment_framework.Voter import Voter
from Voting_rules.KBorda.Kborda import Kborda
from Voting_rules.KBorda.KbordaNextFCFS import KbordaNextFCFS


def generate_election_map(exp_id: str = '100x100_third_try', distance_id: str = 'emd-positionwise',
                          embedding_id: str = 'fr', num_voters: int = 100, num_candidates: int = 100,
                          generate: bool = False, compute_distances: bool = False, compute_feature: bool = False,
                          embed: bool = False, print_map: bool = False):
    # %% prepare experiment
    experiment = mapel.prepare_offline_ordinal_experiment(
        experiment_id = exp_id,
        distance_id = distance_id,
        embedding_id = embedding_id,
    )
    experiment.is_exported = True
    if generate:
        experiment.reset_cultures()
        experiment.set_default_num_voters(num_voters)
        experiment.set_default_num_candidates(num_candidates)
        ids = (['ic'] + ['urn'] * 6 + ['mallows'] * 10 + ['conitzer', 'walsh', 'spoc', 'single-crossing'] +
               ['euclidean'] * 9 + ['anid', 'stid', 'anun', 'stun', 'stan', 'unid'] + ['identity', 'uniformity',
                                                                                       'antagonism', 'stratification'])
        labels = ['IC', 'URN 0.01', 'URN 0.02', 'URN 0.05', 'URN 0.1', 'URN 0.2', 'URN 0.5', 'Mallows 0.001',
                  'Mallows 0.01', 'Mallows 0.05', 'Mallows 0.1', 'Mallows 0.25', 'Mallows 0.5', 'Mallows 0.75',
                  'Mallows 0.95', 'Mallows 0.99', 'Mallows 0.999', 'Conitzer', 'Walsh', 'SPOC', 'Single Crossing',
                  '1D Hypercube',
                  '2D Hypercube', '3D Hypercube', '5D Hypercube', '10D Hypercube', '20D Hypercube', '2D Hypersphere',
                  '3D Hypersphere', '5D Hypersphere', 'AN-ID', 'ST-ID', 'AN-UN', 'ST-UN', 'ST-AN', 'UN-ID', 'ID', 'UN',
                  'AN', 'ST']
        colors = ["#FF0000", "#0000FF", "#000080", "#87CEEB", "#00FFFF", "#40E0D0", "#008080", "#00FF00", "#008000",
                  "#90EE90", "#00FA9A", "#98FB98", "#32CD32", "#3CB371", "#2E8B57", "#228B22", "#006400", "#006400",
                  "#FFA500", "#800080", "#FFC0CB", "#FF0000", "#DC143C", "#B22222", "#8B0000", "#CD5C5C", "#FA8072",
                  "#808080", "#A9A9A9", "#D3D3D3", "#000000", "#000000", "#000000", "#000000", "#A52A2A", "#8B4513",
                  "#D2691E", "#DEB887", "#FF8C00", "#FF7F50"]
        params = [None, {'alpha': 0.01}, {'alpha': 0.02}, {'alpha': 0.05}, {'alpha': 0.1}, {'alpha': 0.2},
                  {'alpha': 0.5}, {'phi': 0.001}, {'phi': 0.01}, {'phi': 0.05}, {'phi': 0.1}, {'phi': 0.25},
                  {'phi': 0.5}, {'phi': 0.75}, {'phi': 0.95}, {'phi': 0.99}, {'phi': 0.999}, None, None, None, None,
                  {'dim': 1, 'space': 'uniform'}, {'dim': 2, 'space': 'uniform'}, {'dim': 3, 'space': 'uniform'},
                  {'dim': 5, 'space': 'uniform'}, {'dim': 10, 'space': 'uniform'}, {'dim': 20, 'space': 'uniform'},
                  {'dim': 2, 'space': 'sphere'}, {'dim': 3, 'space': 'sphere'}, {'dim': 5, 'space': 'sphere'},
                  None, None, None, None, None, None, None, None, None, None]
        sizes = [10] + [30] * 6 + [20] * 10 + [30] * 13 + [20] * 6 + [1] * 4
        markers = [None] * 30 + ['>'] * 6 + ['x'] * 4
        zipped = zip(ids, labels, colors, params, sizes, markers)
        for id_, label, color, param, size, marker in zipped:
            experiment.add_family(id_, size = size, label = label, color = color, params = param, marker = marker)
    
    # %% compute distances
    if compute_distances:
        experiment.prepare_elections()
    experiment.compute_distances(num_processes = 8)
    # %% compute feature
    if compute_feature:
        experiment.add_feature('next_fcfs_integral', maple_feature_next_fcfs)
    experiment.compute_feature('next_fcfs_integral')
    # %% embed 2d and print map
    if embed:
        experiment.embed_2d(embedding_id = 'fr')
    if print_map:
        cmap = mpl.colormaps['inferno']
    experiment.print_map_2d(saveas = 'map', figsize = (10, 8), textual = ['ID', 'UN', 'AN', 'ST'], tex = True)
    omit = []
    for i in range(0, 19):
        omit.append(f'anid_100_100_{i}')
        omit.append(f'stid_100_100_{i}')
        omit.append(f'anun_100_100_{i}')
        omit.append(f'stun_100_100_{i}')
    experiment.print_map_2d_colored_by_feature(feature_id = 'next_fcfs_integral', cmap = cmap, tex = True,
                                               saveas = 'map_colored', figsize = (10, 8),
                                               textual = ['ID', 'UN', 'AN', 'ST'],
                                               omit = omit)


def maple_experiment(voters, num_candidates, num_questions):
    random.shuffle(voters)
    temp_election = Election(list(range(num_candidates)), voters)
    # noinspection PyTypeChecker
    experiment = Experiment(50, temp_election, Kborda, KbordaNextFCFS(), num_questions)
    return experiment.committeeDistance


def maple_feature_next_fcfs(election: mapel.OrdinalElection) -> dict:
    """
    This function computes the feature for the election using the Next FCFS rule.
    :param election: Election object
    :return: Dictionary containing the feature for the election
    """
    
    if election.fake:
        return {'value': None, 'plot': None}
    voters = election.votes
    new_voters = []
    for voter in voters:
        new_voter = Voter(voter)
        new_voters.append(new_voter)
    num_candidates = election.num_candidates
    num_questions = list(range(1, 80000, 1000))
    
    with Pool() as pool:
        distances = list(
            pool.starmap(maple_experiment,
                         [(new_voters.copy(), num_candidates, num_questions.copy()) for _ in range(5)]))
    distances = np.mean(distances, axis = 0)
    x = num_questions
    y = distances
    x = np.array(x)
    y = np.array(y)
    max_value = np.max(y)
    y = y / max_value
    integral = np.sum(y)
    import matplotlib.pyplot as plt
    # save plot as var to return it
    fig, ax = plt.subplots()
    ax.plot(x, y, 'o')
    ax.set(xlabel = 'Number of questions', ylabel = 'Distance between the committees',
           title = f"{election.election_id}\n {integral}")
    ax.grid()
    plt.close(fig)
    # return the strongest coefficient of the polynomial as the feature
    return {'value': integral, 'plot': (fig, ax)}
