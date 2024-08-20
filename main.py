# %%

import argparse

import numpy as np
import torch

from election_map import generate_election_map
from Experiment_framework.ai_training import deep_learning, genetic, annealing
from Experiment_framework.main_helper import *
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

"""
This file is the main file to run the experiment. It contains the main function that runs the experiment and plots the
graph for the experiment.
"""


# %%
def run_ic_experiments(training_mode = False, load_saved = True, compute = False):
    """
    Main function to run the experiment
    :return: None
    """
    if training_mode:
        best_annealing_function = annealing()
        best_genetic_function = genetic()
        final_learning_model = deep_learning()
    else:
        try:
            with open('models/best_annealing_function.pkl', 'rb') as f:
                best_annealing_function = pickle.load(f)
            with open('models/best_genetic_function.pkl', 'rb') as f:
                best_genetic_function = pickle.load(f)
            final_learning_model = torch.load('final_model.pth')
        except FileNotFoundError:
            send_message("Please run the training mode first.")
            return
    # %%
    
    test_parameters = dict(
        target_committee_size = 50, num_candidates = 100, num_voters = 100,
        voting_rule = Kborda,
        constrained_voting_rule =
        [
            KbordaSplitFCFS(),
            KbordaNextEq(), KbordaNextFCFS(),
            KbordaLastEq(), KbordaLastFCFS(),
            KbordaNextLastEQ(), KbordaNextLastFCFS(),
            KbordaBucketSplit(), KbordaBucketTrinary(),
            KbordaBucket(best_annealing_function, 'Annealing'),
            KbordaBucket(best_genetic_function, 'Genetic'),
            KbordaBucket(final_learning_model, 'Deep Learning'),
            VotingRuleRandom()],
        number_of_questions = range(1, 400000, 1000), number_of_runs = 5000,
        multithreaded = True)
    
    # %%
    """KBorda testing"""
    # %%
    if load_saved:
        no_of_saved_runs, saved_averages = extract_saved_averages()
        if compute:
            averages = run_test(test_parameters)
            averages, test_parameters = combine_saved_current(averages, no_of_saved_runs, saved_averages,
                                                              test_parameters)
            write_averages_to_file(averages, test_parameters)
        else:
            averages = saved_averages
            test_parameters['number_of_runs'] = no_of_saved_runs
    elif compute:
        averages = run_test(test_parameters)
        write_averages_to_file(averages, test_parameters)
    else:
        raise Exception("Please choose either load_saved or compute or both to be True.")
    # %%
    total_averages = {}
    # Calculate the average Accuracy for each voting rule
    for key in averages:
        total_averages[key] = float(np.mean(averages[key]))
    # %%
    # send plot, averages, parameters and file to telegram
    send_plot(test_parameters, averages)
    send_message(total_averages.__str__())
    send_message(test_parameters.__str__())
    send_file('averages.pickle')


def run_maple_experiments(exp_id: str = '100x100', distance_id: str = 'emd-positionwise',
                          embedding_id: str = 'fr', num_voters: int = 100, num_candidates: int = 100,
                          generate: bool = False, compute_distances: bool = False, compute_feature: bool = False,
                          embed: bool = False, print_map: bool = False):
    """
    Run the Maple experiments
    Args:
        exp_id: the experiment id
        distance_id: the distance id
        embedding_id: the embedding id
        num_voters: the number of voters
        num_candidates: the number of candidates
        generate: whether to generate the elections from scratch
        compute_distances: whether to compute the distances between the elections
        compute_feature: whether to compute the feature
        embed: whether to embed the 2d map
        print_map: whether to print the map
    """
    generate_election_map(exp_id, distance_id, embedding_id, num_voters, num_candidates, generate, compute_distances,
                          compute_feature, embed, print_map)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-ic", "--ic", help = "Run the IC experiment", action = "store_true")
    parser.add_argument("-t", "--training", help = "Run the training mode", action = "store_true")
    parser.add_argument("-l", "--load", help = "Load the saved averages", action = "store_true")
    parser.add_argument("-c", "--compute", help = "Compute more averages", action = "store_true")
    parser.add_argument("-m", "--maple", help = "Run the Maple experiment", action = "store_true")
    parser.add_argument("-e", "--embed", help = "Embed the 2d map", action = "store_true")
    parser.add_argument("-p", "--print", help = "Print the map", action = "store_true")
    parser.add_argument("-g", "--generate", help = "Generate the elections", action = "store_true")
    parser.add_argument("-d", "--compute_distances", help = "Compute the distances", action = "store_true")
    parser.add_argument("-f", "--compute_feature", help = "Compute the feature", action = "store_true")
    parser.add_argument("-n", "--num_voters", help = "Number of voters", type = int)
    parser.add_argument("-cand", "--num_candidates", help = "Number of candidates", type = int)
    parser.add_argument("-exp", "--exp_id", help = "Experiment id", type = str)
    parser.add_argument("-dist", "--distance_id", help = "Distance id", type = str)
    parser.add_argument("-emb", "--embedding_id", help = "Embedding id", type = str)
    args = parser.parse_args()
    if args.ic:
        run_ic_experiments(args.training, args.load, args.compute)
    elif args.maple:
        run_maple_experiments(args.exp_id, args.distance_id, args.embedding_id, args.num_voters, args.num_candidates,
                              args.generate, args.compute_distances, args.compute_feature, args.embed, args.print)
    else:
        raise Exception("Please choose either IC or Maple experiment.")


# %%
if __name__ == '__main__':
    main()
