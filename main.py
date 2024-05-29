from multiprocessing import Pool
from tqdm import tqdm
from Experiment_framework.Experiment import run_experiment_wrapper
from Voting_rules.KBorda.KBorda import KBorda
from Voting_rules.KBorda.KbordaConstrained import KbordaConstrained
from Voting_rules.SNTV.SNTV import SNTV
from Voting_rules.SNTV.SntvConstrained import SntvConstrained
import matplotlib.pyplot as plt


def main():
    """
    Main function to run the experiment
    :return: None
    """
    SNTV_TEST_PARAMETERS = {'target_committee_size': 500, 'num_candidates': 1000, 'num_voters': 1000,
                            'number_of_questions': range(1, 1001),
                            'number_of_runs': 20}
    KBORDA_TEST_PARAMETERS = {'target_committee_size': 50, 'num_candidates': 100, 'num_voters': 10,
                              'number_of_questions': range(1, 1001),
                              'number_of_runs': 20}

    """SNTV testing"""

    target_committee_size = SNTV_TEST_PARAMETERS['target_committee_size']
    num_candidates = SNTV_TEST_PARAMETERS['num_candidates']
    num_voters = SNTV_TEST_PARAMETERS['num_voters']
    number_of_questions = SNTV_TEST_PARAMETERS['number_of_questions']
    number_of_runs = SNTV_TEST_PARAMETERS['number_of_runs']
    average_differences = [0] * len(number_of_questions)

    # Start testing loop multithreded with imap

    with Pool() as pool:
        differences = list(tqdm(pool.imap(run_experiment_wrapper,
                                          [(target_committee_size, num_candidates, num_voters, SNTV, SntvConstrained,
                                            number_of_questions)
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
    # plt.plot(average_differences)
    # plt.xlabel('Number of questions')
    # plt.ylabel('Distance between the committees')
    # plt.title('Distance between the committees for different number of questions SNTV')
    # plt.show()

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
                                       number_of_questions) for i in range(number_of_runs)]),
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
    # plt.plot(average_differences)
    # plt.xlabel('Number of questions')
    # plt.ylabel('Distance between the committees')
    # plt.title('Distance between the committees for different number of questions KBorda')
    # # plot as a dotted plot
    # plt.plot(average_differences, 'ro')
    # plt.show()


if __name__ == '__main__':
    main()
