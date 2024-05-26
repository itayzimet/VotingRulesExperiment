from multiprocessing import Pool
from tqdm import tqdm
from Experiment_framework.Election import Election
from Experiment_framework.Experiment import Experiment
from Experiment_framework.Experiment import ExperimentHelper
from Voting_rules.SNTV.SNTV import SNTV
from Voting_rules.SNTV.SNTV_constrained import SNTV_constrained
from Voting_rules.KBorda.KBorda import KBorda
from Voting_rules.KBorda.KbordaConstrained import KbordaConstrained
import matplotlib.pyplot as plt
import pandas as pd

from Voting_rules.VotingRule import VotingRule
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained


def run_experiment(election : Election, rule1: VotingRule, rule2: VotingRuleConstrained, i: int):
    """
    Run the experiment and return the committee distance.

    :param election: The election instance.
    :param rule1: The first voting rule.
    :param rule2: The second voting rule.
    :param i: The number of questions.
    :return: The committee distance.
    """
    result = Experiment(50, election, rule1, rule2, i).committeeDistance
    election.reset()
    return result


def run_experiment_wrapper(args):
    return run_experiment(*args)


def run_multithreaded_experiment(election: Election, rule1: VotingRule, rule2: VotingRuleConstrained, start: int, end: int):
    """
    Run the experiment in multiple threads and return the differences.

    :param election: The election instance.
    :param rule1: The first voting rule.
    :param rule2: The second voting rule.
    :param start: The start of the range of questions.
    :param end: The end of the range of questions.
    :return: The differences.
    """
    with Pool() as pool:
        tasks = list(tqdm(pool.imap(run_experiment_wrapper, [(election, rule1, rule2, i) for i in range(start, end + 1)]),
                          total=end - start + 1))
    return tasks


def main():
    """
    Main function to run the experiment
    :return: None
    """

    """SNTV testing"""

    # Fabricate an election with 100 candidates and 1000 voters and run the experiment with SNTV and SNTV constrained with 5 winners and differing number of questions, create a graph where the x-axis is the number of questions and the y-axis is the distance between the two committees
    election = ExperimentHelper.fabricate_election(100, 1000)
    differences = run_multithreaded_experiment(election, SNTV, SNTV_constrained, 1, 10000)

    # Plot the graph
    plt.plot(differences)
    plt.xlabel('Number of questions')
    plt.ylabel('Distance between the committees')
    plt.title('Distance between the committees for different number of questions SNTV')
    # show 1000 ticks on the x-axis
    plt.xticks(range(0, 10000, 1000))
    plt.show()

    """KBorda testing"""

    differences = run_multithreaded_experiment(election, KBorda, KbordaConstrained, 1, 100000)

    # Plot the graph
    plt.plot(differences)
    plt.xlabel('Number of questions')
    plt.ylabel('Distance between the committees')
    plt.title('Distance between the committees for different number of questions KBorda')
    # show 1000 ticks on the x-axis
    plt.xticks(range(0, 100000, 10000))
    plt.show()


if __name__ == '__main__':
    main()
