# Description: Main file to run the experiment
from Experiment_framework.main_helper import *
from Voting_rules.KBorda.KBorda import KBorda
from Voting_rules.KBorda.KbordaConstrained import KbordaConstrained
from Voting_rules.SNTV.SNTV import SNTV
from Voting_rules.SNTV.SntvConstrained import SntvConstrained


def main():
    """
    Main function to run the experiment
    :return: None
    """
    SNTV_TEST_PARAMETERS = {'target_committee_size': 500, 'num_candidates': 1000, 'num_voters': 1000,
                            'voting_rule': SNTV, 'constrained_voting_rule': SntvConstrained,
                            'number_of_questions': list(range(1, 2001)),
                            'number_of_runs': 20, 'multithreded': True}
    KBORDA_TEST_PARAMETERS = {'target_committee_size': 500, 'num_candidates': 1000, 'num_voters': 1000,
                              'voting_rule': KBorda, 'constrained_voting_rule': KbordaConstrained,
                              'number_of_questions': list(range(1, 2000001, 10000)),
                              'number_of_runs': 20, 'multithreded': True}

    """SNTV testing"""
    # Run the test for SNTV
    average_differences = run_test(SNTV_TEST_PARAMETERS)

    # Plot the graph for SNTV
    plot_graph(SNTV_TEST_PARAMETERS, average_differences)

    """KBorda testing"""
    # Run the test for KBorda
    average_differences = run_test(KBORDA_TEST_PARAMETERS)

    # Plot the graph for KBorda
    plot_graph(KBORDA_TEST_PARAMETERS, average_differences)


if __name__ == '__main__':
    main()
