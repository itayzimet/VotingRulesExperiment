from multiprocessing import Pool
from tqdm import tqdm
from Experiment_framework.Experiment import Experiment
from Experiment_framework.Experiment import ExperimentHelper
from Voting_rules.KBorda.KBorda import KBorda
from Voting_rules.KBorda.KbordaConstrained import KbordaConstrained
from Voting_rules.SNTV.SNTV import SNTV
from Voting_rules.SNTV.SntvConstrained import SntvConstrained
import matplotlib.pyplot as plt


def run_experiment(target_committee_size: int, num_candidates: int, num_voters: int, voting_rule,
                   constrained_voting_rule, number_of_questions: list[int]) -> int:
    """
    Run the experiment
    :param target_committee_size: the size of the committee to be found
    :param num_candidates: the number of candidates in the election
    :param num_voters: the number of voters in the election
    :param voting_rule: the voting rule to find the committee with
    :param constrained_voting_rule: the constrained voting rule to find the committee with
    :param number_of_questions: the number of questions all voters can answer for the constrained voting rule
    :return: list of distances between all the committees
    """
    # Fabricate an election with num_candidates candidates and num_voters voters
    election = ExperimentHelper.fabricate_election(num_candidates, num_voters)
    # Run the experiment
    experiment = Experiment(target_committee_size, election, voting_rule, constrained_voting_rule, number_of_questions)
    # Return the distance between the two committees
    return experiment.committeeDistance


def run_experiment_wrapper(args):
    return run_experiment(*args)


def main():
    """
    Main function to run the experiment
    :return: None
    """
    SNTV_TEST_PARAMETERS = {'target_committee_size': 500, 'num_candidates': 1000, 'num_voters': 1000,
                            'number_of_questions': range(1, 1001),
                            'number_of_runs': 2000}
    KBORDA_TEST_PARAMETERS = {'target_committee_size': 50, 'num_candidates': 100, 'num_voters': 100,
                              'number_of_questions': range(1, 10001),
                              'number_of_runs': 50}

    """SNTV testing"""

    target_committee_size = SNTV_TEST_PARAMETERS['target_committee_size']
    num_candidates = SNTV_TEST_PARAMETERS['num_candidates']
    num_voters = SNTV_TEST_PARAMETERS['num_voters']
    number_of_questions = SNTV_TEST_PARAMETERS['number_of_questions']
    number_of_runs = SNTV_TEST_PARAMETERS['number_of_runs']

    # Start testing loop multithreded with imap
    average_differences = [0] * len(number_of_questions)
    with Pool() as pool:
        differences = list(tqdm(
            pool.imap(run_experiment_wrapper,
                      [(target_committee_size, num_candidates, num_voters, SNTV, SntvConstrained, number_of_questions[i])
                       for i in range(number_of_runs)]),
            total=number_of_runs, desc='Running experiments'))
        # Average the results from the different runs
        for difference in differences:
            for i in range(len(difference)):
                average_differences[i] += difference[i]
    for i in range(len(average_differences)):
        average_differences[i] /= number_of_runs

    # Export the results from Experiments to an Excel file using pandas
    # ExperimentHelper.export_to_excel(number_of_questions, differences)

    # Plot the graph
    plt.plot(average_differences)
    plt.xlabel('Number of questions')
    plt.ylabel('Distance between the committees')
    plt.title('Distance between the committees for different number of questions SNTV')
    plt.show()

    """KBorda testing"""

    target_committee_size = KBORDA_TEST_PARAMETERS['target_committee_size']
    num_candidates = KBORDA_TEST_PARAMETERS['num_candidates']
    num_voters = KBORDA_TEST_PARAMETERS['num_voters']
    number_of_questions = KBORDA_TEST_PARAMETERS['number_of_questions']
    number_of_runs = KBORDA_TEST_PARAMETERS['number_of_runs']

    # Start testing loop multithreded with imap
    average_differences = [0] * len(number_of_questions)

    with Pool() as pool:
        differences = list(tqdm(
            pool.imap(run_experiment_wrapper,
                      [(target_committee_size, num_candidates, num_voters, KBorda, KbordaConstrained,
                        number_of_questions[i]) for i in range(number_of_runs)]),
            total=number_of_runs, desc='Running experiments'))
        # Average the results from the different runs
        for difference in differences:
            for i in range(len(difference)):
                average_differences[i] += difference[i]
    for i in range(len(average_differences)):
        average_differences[i] /= number_of_runs

    # Export the results from Experiments to an Excel file using pandas
    # ExperimentHelper.export_to_excel(number_of_questions, differences)

    # Plot the graph as a dotted plot
    plt.plot(average_differences)
    plt.xlabel('Number of questions')
    plt.ylabel('Distance between the committees')
    plt.title('Distance between the committees for different number of questions KBorda')
    # plot as a dotted plot
    plt.plot(average_differences, 'ro')
    plt.show()


if __name__ == '__main__':
    main()
