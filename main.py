# %%

import numpy as np

from anealing import send_message
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
def main():
    """
    Main function to run the experiment
    :return: None
    """
    # %%
    test_parameters = dict(
        target_committee_size = 50, num_candidates = 100, num_voters = 100,
        voting_rule = Kborda,
        constrained_voting_rule =
        [
            KbordaSplitFCFS,
            KbordaNextEq, KbordaNextFCFS,
            KbordaLastEq, KbordaLastFCFS,
            KbordaNextLastEQ, KbordaNextLastFCFS,
            KbordaBucketSplit, KbordaBucketTrinary,
            VotingRuleRandom],
        number_of_questions = range(1, 150000, 1000), number_of_runs = 1,
        multithreaded = False)
    # %%
    """KBorda testing"""
    # %%
    # load averages from pickle file
    no_of_saved_runs, saved_averages = extract_saved_averages()
    # %%
    # Run the test for KBorda
    averages = run_test(test_parameters)
    # %%
    # Average the saved averages and the new averages
    averages, test_parameters = combine_saved_current(averages, no_of_saved_runs, saved_averages, test_parameters)
    # add averages to pickle file
    write_averages_to_file(averages, test_parameters)
    total_averages = {}
    # Calculate the average Accuracy for each voting rule
    for key in averages:
        total_averages[key] = float(np.mean(averages[key]))
    # %%
    # Print the average Accuracy for each voting rule
    send_message(total_averages.__str__())
    # Plot the graph for KBorda
    plot_graph(test_parameters, averages)


# %%
if __name__ == '__main__':
    main()
