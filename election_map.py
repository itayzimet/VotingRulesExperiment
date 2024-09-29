import pickle
import random
from functools import partial

import mapof.elections as mapof
import matplotlib as mpl
import numpy as np
import torch

from Experiment_framework.Election import Election
from Experiment_framework.Experiment import Experiment
from Experiment_framework.Voter import Voter
from Voting_rules import VotingRuleConstrained
from Voting_rules.KBorda.Kborda import Kborda
from Voting_rules.KBorda.KbordaBucket import KbordaBucket
from Voting_rules.KBorda.KbordaBucketSplit import KbordaBucketSplit
from Voting_rules.KBorda.KbordaBucketTrinary import KbordaBucketTrinary
from Voting_rules.KBorda.KbordaLastEq import KbordaLastEq
from Voting_rules.KBorda.KbordaLastFCFS import KbordaLastFCFS
from Voting_rules.KBorda.KbordaNextEq import KbordaNextEq
from Voting_rules.KBorda.KbordaNextFCFS import KbordaNextFCFS
from Voting_rules.KBorda.KbordaNextLastEQ import KbordaNextLastEQ
from Voting_rules.KBorda.KbordaNextLastFCFS import KbordaNextLastFCFS
from Voting_rules.KBorda.KbordaSplitFCFS import KbordaSplitFCFS
from Voting_rules.VotingRuleRandom import VotingRuleRandom

voting_rules: list[VotingRuleConstrained] = []


def generate_election_map(
        exp_id: str = '100x100', distance_id: str = 'emd-positionwise', embedding_id: str = 'fr',
        generate: bool = False, compute_distances: bool = False, compute_feature: bool = False, embed: bool = False,
        print_map: bool = False):
    try:
        with open('models/best_annealing_function.pkl', 'rb') as f:
            best_annealing_function = pickle.load(f)
        with open('models/best_genetic_function.pkl', 'rb') as f:
            best_genetic_function = pickle.load(f)
        final_learning_model = torch.load('models/final_model.pth', weights_only = False)
    except FileNotFoundError:
        print("Please run the training mode first.")
        return

    global voting_rules
    voting_rules = [KbordaSplitFCFS(), KbordaNextEq(), KbordaNextFCFS(), KbordaLastEq(), KbordaLastFCFS(),
                    KbordaNextLastEQ(), KbordaNextLastFCFS(), KbordaBucketSplit(), KbordaBucketTrinary(),
                    KbordaBucket(best_annealing_function, 'Annealing'), KbordaBucket(best_genetic_function,'Genetic'),
                    KbordaBucket(final_learning_model, 'Deep Learning'),
            VotingRuleRandom()]
    # %% prepare experiment
    experiment = mapof.prepare_offline_ordinal_experiment(experiment_id = exp_id, distance_id = distance_id,
                                                          embedding_id = embedding_id)
    if generate:
        experiment.prepare_elections()
    # %% compute distances
    if compute_distances:
        experiment.compute_distances(num_processes = 10)
    # %% compute feature
    if compute_feature:
        compute_features(experiment)
    # %% embed 2d and print map
    if embed:
        experiment.embed_2d(embedding_id = 'fr')
    if print_map:
        print_maps(experiment)


def print_maps(experiment):
    cmap = mpl.colormaps['inferno']

    # experiment.print_map_2d(saveas = 'map', figsize = (10, 8), textual = ['ID', 'UN', 'AN', 'ST'],
    #                         legend_pos = (1.15, 1), tex = True)
    omit = []
    for i in range(0, 19):
        omit.append(f'anid_100_100_{i}')
        omit.append(f'stid_100_100_{i}')
        omit.append(f'anun_100_100_{i}')
        omit.append(f'stun_100_100_{i}')
        omit.append(f'stan_100_100_{i}')
        omit.append(f'unid_100_100_{i}')
    print_map = partial(experiment.print_map_2d_colored_by_feature, cmap = cmap, tex = True, figsize = (10, 8),
                        textual = ['ID', 'UN', 'AN', 'ST'], omit = omit)
    for rule in voting_rules:
        print_map(feature_id = rule.__str__(), saveas = f'map_{rule.__str__()}')

def compute_feature(rule: VotingRuleConstrained, experiment):
    feature = partial(mapof_feature, rule = rule)
    experiment.add_feature(f'{rule.__str__()}', feature)
    experiment.compute_feature(f'{rule.__str__()}')

def compute_features(experiment):
    import multiprocessing
    _compute_feature = partial(compute_feature, experiment = experiment)
    with multiprocessing.Pool(processes=8) as pool:
        pool.map(_compute_feature, voting_rules)




def mapof_experiment(voters, num_candidates, num_questions, rule, _ = 0):
    random.shuffle(voters)
    temp_election = Election(list(range(num_candidates)), voters)
    # noinspection PyTypeChecker
    experiment = Experiment(50, temp_election, Kborda, rule, num_questions)
    return experiment.committeeDistance


def mapof_feature(election: mapof.OrdinalElection, rule: VotingRuleConstrained) -> dict:
    """
    This function computes the feature for the election using the Next FCFS rule.
    :param election: Election object
    :param rule: Voting rule
    :return: Dictionary containing the feature for the election
    """

    if election.fake:
        return {'value': None, 'plotx': None, 'ploty': None}
    voters = election.votes
    new_voters = []
    for voter in voters:
        new_voter = Voter(voter)
        new_voters.append(new_voter)
    num_candidates = election.num_candidates
    num_questions = list(range(1, 80000, 1000))

    run_experiment = partial(mapof_experiment, new_voters, num_candidates, num_questions, rule)
    distances = [run_experiment(i) for i in range(0, 10)]

    average_distances = [np.mean(distances, axis = 0)]

    x = num_questions
    y = average_distances
    x = np.array(x)
    y = np.array(y)
    max_value = np.max(y)
    y = y / max_value
    integral = np.sum(y)
    # return the strongest coefficient of the polynomial as the feature
    return {'value': integral, 'plotx': x, 'ploty': y}
