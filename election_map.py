from multiprocessing import Pool
import random

from mapel import elections as mapel
import matplotlib as mpl
import numpy as np

from Experiment_framework.Election import Election
from Experiment_framework.Experiment import Experiment
from Experiment_framework.Voter import Voter
from Voting_rules import VotingRuleConstrained
from Voting_rules.KBorda.Kborda import Kborda
from Voting_rules.KBorda.KbordaBucketSplit import KbordaBucketSplit
from Voting_rules.KBorda.KbordaNextFCFS import KbordaNextFCFS


def generate_election_map(exp_id: str = '100x100', distance_id: str = 'emd-positionwise',
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
        experiment.prepare_elections()
    
    # %% compute distances
    if compute_distances:
        experiment.compute_distances(num_processes = 10)
    # %% compute feature
    if compute_feature:
        experiment.add_feature('next_fcfs_integral', maple_feature_next_fcfs)
        experiment.compute_feature('next_fcfs_integral')
        experiment.add_feature('split_integral', maple_feature_split)
        experiment.compute_feature('split_integral')
    # %% embed 2d and print map
    if embed:
        experiment.embed_2d(embedding_id = 'fr')
    if print_map:
        cmap = mpl.colormaps['inferno']
        experiment.print_map_2d(saveas = 'map', figsize = (10, 8),
                                textual = ['ID', 'UN', 'AN', 'ST'],
                                legend_pos = (1.05, 1),
                                shading = True,
                                tex = True)
        omit = []
        for i in range(0, 19):
            omit.append(f'anid_100_100_{i}')
            omit.append(f'stid_100_100_{i}')
            omit.append(f'anun_100_100_{i}')
            omit.append(f'stun_100_100_{i}')
            omit.append(f'stan_100_100_{i}')
            omit.append(f'unid_100_100_{i}')
        experiment.print_map_2d_colored_by_feature(feature_id = 'next_fcfs_integral', cmap = cmap, tex = True,
                                                   saveas = 'map_next', figsize = (10, 8),
                                                   textual = ['ID', 'UN', 'AN', 'ST'],
                                                   omit = omit)
        experiment.print_map_2d_colored_by_feature(feature_id = 'split_integral', cmap = cmap, tex = True,
                                                   saveas = 'map_split', figsize = (10, 8),
                                                   textual = ['ID', 'UN', 'AN', 'ST'],
                                                   omit = omit)


def maple_experiment(voters, num_candidates, num_questions, rule = KbordaNextFCFS()):
    random.shuffle(voters)
    temp_election = Election(list(range(num_candidates)), voters)
    # noinspection PyTypeChecker
    experiment = Experiment(50, temp_election, Kborda, rule, num_questions)
    return experiment.committeeDistance


def maple_feature_next_fcfs(election: mapel.OrdinalElection):
    return maple_feature(election, KbordaNextFCFS)


def maple_feature_split(election: mapel.OrdinalElection):
    return maple_feature(election, KbordaBucketSplit)


def maple_feature(election: mapel.OrdinalElection, rule: VotingRuleConstrained) -> dict:
    """
    This function computes the feature for the election using the Next FCFS rule.
    :param election: Election object
    :param rule: Voting rule
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
    
    distances = maple_experiment(new_voters, num_candidates, num_questions, rule())
    x = num_questions
    y = distances
    x = np.array(x)
    y = np.array(y)
    max_value = np.max(y)
    if max_value == 0:  # debugging purposes
        import matplotlib.pyplot as plt
        plt.plot(x, y, 'o')
        plt.xlabel('Number of questions')
        plt.ylabel('Distance between the committees')
        plt.title(f"{election.election_id}\n {0}")
        plt.grid()
        plt.show()
        return {'value': 0, 'plot': (x, y)}
    y = y / max_value
    integral = np.sum(y)
    # return the strongest coefficient of the polynomial as the feature
    return {'value': integral, 'plot': (x, y)}
