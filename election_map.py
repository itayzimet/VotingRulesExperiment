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
        experiment.add_family('ic', size = 10, color = 'blue', label = 'IC')
        alphas = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5]
        for alpha in alphas:
            experiment.add_family('urn', size = 30, color = 'red', params = {'alpha': alpha}, label = f'URN {alpha}')
        phis = [0.001, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.95, 0.99, 0.999]
        for phi in phis:
            experiment.add_family('mallows', size = 20, color = 'green', params = {'phi': phi}, label = f'Mallows {phi}')
        experiment.add_family('conitzer', size = 30, color = 'brown', label = 'Conitzer')
        experiment.add_family('walsh', size = 30, color = 'purple', label = 'Walsh')
        experiment.add_family('spoc', size = 30, color = 'orange', label = 'SPOC')
        experiment.add_family('single-crossing', size = 30, color = 'yellow', label = 'SC')
        dims = [1, 2, 3, 5, 10, 20]
        for dim in dims:
            experiment.add_family('euclidean', size = 30, color = 'cyan', params = {'dim': dim, 'space': 'uniform'}, label = f'{dim}D Hypercube', alpha = dim/20)
        dims = [2, 3, 5]
        for dim in dims:
            experiment.add_family('euclidean', size = 30, color = 'magenta', params = {'dim': dim, 'space': 'sphere'}, label = f'{dim}D Hypersphere', alpha = dim/5)
        
        experiment.add_election('identity', color = 'black', label = 'ID', marker = 'x')
        experiment.add_election('uniformity', color = 'black', label = 'UN', marker = 'x')
        experiment.add_election('antagonism', color = 'black', label = 'AN', marker = 'x')
        experiment.add_election('stratification', color = 'black', label = 'ST', marker = 'x')
        experiment.add_family('anid', color = 'silver', size = 20, marker = 3, path = {'variable': 'alpha'}, label = 'AN-ID')
        experiment.add_family('stid', color = 'silver', size = 20, marker = 3, path = {'variable': 'alpha'}, label = 'ST-ID')
        experiment.add_family('anun', color = 'silver', size = 20, marker = 3, path = {'variable': 'alpha'}, label = 'AN-UN')
        experiment.add_family('stun', color = 'silver', size = 20, marker = 3, path = {'variable': 'alpha'}, label = 'ST-UN')
    #%% compute distances
    if compute_distances:
        experiment.prepare_elections()
        experiment.compute_distances(num_processes = 5)
    #%% compute feature
    if compute_feature:
        experiment.add_feature('next_fcfs_integral', maple_feature_next_fcfs)
        experiment.compute_feature('next_fcfs_integral')
    #%% embed 2d and print map
    if embed:
        experiment.embed_2d(embedding_id = 'fr')
    if print_map:
        cmap = mpl.colormaps['inferno']
        experiment.print_map_2d(saveas = 'map', figsize = (10, 8), textual =['ID', 'UN', 'AN', 'ST'], tex = True)
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
