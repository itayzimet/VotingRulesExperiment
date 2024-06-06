# %%

from Experiment_framework.main_helper import *
from Voting_rules.KBorda.Kborda import Kborda
from Voting_rules.KBorda.KbordaConstrainedEq import KbordaConstrainedEq
from Voting_rules.KBorda.KbordaConstrainedFCFS import KbordaConstrainedFCFS
from Voting_rules.KBorda.KbordaSplitEq import KbordaSplitEq
from Voting_rules.KBorda.KbordaSplitFCFS import KbordaSplitFCFS
from Voting_rules.SNTV.SNTV import SNTV
from Voting_rules.SNTV.SntvConstrained import SntvConstrained

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
    sntv_test_parameters = dict(target_committee_size=500, num_candidates=1000, num_voters=1000, voting_rule=SNTV,
                                constrained_voting_rule=[SntvConstrained],
                                number_of_questions=list(range(1, 1001, 100)), number_of_runs=20, multithreaded=True)
    kborda_test_parameters = dict(target_committee_size=50, num_candidates=100, num_voters=10, voting_rule=Kborda,
                                  constrained_voting_rule=[KbordaSplitFCFS, KbordaSplitEq, KbordaConstrainedEq,
                                                           KbordaConstrainedFCFS],
                                  number_of_questions=range(1, 1000, 10), number_of_runs=20, multithreaded=True)
    #%%
    """SNTV testing"""
    # Run the test for SNTV
    averages = run_test(sntv_test_parameters)
    # Plot the graph for SNTV
    plot_graph(sntv_test_parameters, averages)
    #%%
    """KBorda testing"""
    # Run the test for KBorda
    averages = run_test(kborda_test_parameters)
    # Plot the graph for KBorda
    plot_graph(kborda_test_parameters, averages)


if __name__ == '__main__':
    main()
