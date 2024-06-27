#%%
import os
import pickle

import numpy as np

from Experiment_framework.main_helper import *
from Voting_rules.KBorda.Kborda import Kborda
from Voting_rules.KBorda.KbordaBucketGeneral import KbordaBucketGeneral
from Voting_rules.KBorda.KbordaLastEq import KbordaLastEq
from Voting_rules.KBorda.KbordaLastFCFS import KbordaLastFCFS
from Voting_rules.KBorda.KbordaNextEq import KbordaNextEq
from Voting_rules.KBorda.KbordaNextFCFS import KbordaNextFCFS
from Voting_rules.KBorda.KbordaNextLastEQ import KbordaNextLastEQ
from Voting_rules.KBorda.KbordaNextLastFCFS import KbordaNextLastFCFS
from Voting_rules.KBorda.KbordaSplitEq import KbordaSplitEq
from Voting_rules.KBorda.KbordaSplitFCFS import KbordaSplitFCFS
from Voting_rules.SNTV.SNTV import SNTV
from Voting_rules.SNTV.SntvConstrained import SntvConstrained
from Voting_rules.VotingRuleRandom import VotingRuleRandom

"""
This file is the main file to run the experiment. It contains the main function that runs the experiment and plots the
graph for the experiment.
"""


#%%
def main ():
    """
    Main function to run the experiment
    :return: None
    """
    #%%
    sntv_test_parameters = dict(target_committee_size = 10, num_candidates = 100, num_voters = 10, voting_rule = SNTV,
                                constrained_voting_rule = [SntvConstrained, VotingRuleRandom],
                                number_of_questions = list(range(1, 1000, 1)), number_of_runs = 20,
                                multithreaded = False)
    kborda_test_parameters = dict(
        target_committee_size = 50, num_candidates = 100, num_voters = 100,
        voting_rule = Kborda,
        constrained_voting_rule =
        [
            KbordaSplitEq, KbordaSplitFCFS,
            KbordaNextEq, KbordaNextFCFS,
            KbordaLastEq, KbordaLastFCFS,
            KbordaNextLastEQ, KbordaNextLastFCFS,
            KbordaBucketGeneral, VotingRuleRandom],
        number_of_questions = range(1, 150000, 1000), number_of_runs = 5,
        multithreaded = True)
    #%%
    # """SNTV testing"""
    # # Run the test for SNTV
    # averages = run_test(sntv_test_parameters)
    # # Plot the graph for SNTV
    # plot_graph(sntv_test_parameters, averages)
    #%%
    """KBorda testing"""
    #%%
    # load averages from pickle file
    saved_averages = {}
    try:
        with open('averages.pickle', 'rb') as f:
            saved_averages = pickle.load(f)
            no_of_saved_runs = int(saved_averages[1])
            saved_averages = saved_averages[0]
    except:
        pass
    #%%
    # Run the test for KBorda
    averages = run_test(kborda_test_parameters)
    # Average the saved averages and the new averages
    if saved_averages != {}:
        for key in averages:
            if key in saved_averages:
                for i, average in enumerate(averages[key]):
                    averages[key][i] = (((
                        averages[key][i] * kborda_test_parameters['number_of_runs'] +
                        saved_averages[key][i] * no_of_saved_runs)) /
                        (kborda_test_parameters['number_of_runs'] + no_of_saved_runs))
        no_runs = int(no_of_saved_runs) + int(kborda_test_parameters['number_of_runs'])
        kborda_test_parameters['number_of_runs'] = no_runs
    # add averages to pickle file
    if os.path.exists('averages.pickle'):
        os.remove('averages.pickle')
    with open('averages.pickle', 'wb') as f:
        # add the averages to a new pickle file
        data = [averages, int(kborda_test_parameters['number_of_runs'])]
        pickle.dump(data, f)
    total_averages = {}
    # Calculate the average Accuracy for each voting rule
    for key in averages:
        total_averages[key] = float(np.mean(averages[key]))
    #%%
    # Print the average Accuracy for each voting rule
    print(total_averages)
    # Plot the graph for KBorda
    plot_graph(kborda_test_parameters, averages)


#%%
if __name__ == '__main__':
    main()
