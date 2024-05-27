
from Experiment_framework.Experiment import Experiment
from Experiment_framework.Experiment import ExperimentHelper
from Voting_rules.SNTV.SNTV import SNTV
from Voting_rules.SNTV.SntvConstrained import SntvConstrained
from Voting_rules.KBorda.KBorda import KBorda
from Voting_rules.KBorda.KbordaConstrained import KbordaConstrained
import matplotlib.pyplot as plt


def main():
    """
    Main function to run the experiment
    :return: None
    """

    """SNTV testing"""

    # Fabricate an election with 100 candidates and 1000 voters and run the experiment with SNTV and SNTV constrained
    # with 5 winners and differing number of questions, create a graph where the x-axis is the number of questions
    # and the y-axis is the distance between the two committees
    election = ExperimentHelper.fabricate_election(100, 1000)
    differences = Experiment(50, election, SNTV, SntvConstrained, range(1, 10000)).committeeDistance
    # Plot the graph
    plt.plot(differences)
    plt.xlabel('Number of questions')
    plt.ylabel('Distance between the committees')
    plt.title('Distance between the committees for different number of questions SNTV')
    # show 1000 ticks on the x-axis
    plt.xticks(range(0, 10000, 1000))
    plt.show()

    """KBorda testing"""

    differences = Experiment(50, election, KBorda, KbordaConstrained, range(1, 100000)).committeeDistance

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
