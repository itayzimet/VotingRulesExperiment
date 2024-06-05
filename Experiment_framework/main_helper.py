"""
This module is a helper module for the main part of the experiment

It contains the following functions:
    - run_experiment(target_committee_size: int, num_candidates: int, num_voters: int, voting_rule, constrained_voting_rule, number_of_questions: list[int]) -> list[int]
    - run_experiment_wrapper(args) -> list[int]
"""
from multiprocessing import Pool

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from tqdm import tqdm

from Experiment_framework.Experiment import Experiment
from Experiment_framework.Experiment_helper import fabricate_election


def run_experiment(target_committee_size: int, num_candidates: int, num_voters: int, voting_rule,
                   constrained_voting_rule, number_of_questions: list[int]) -> list[int]:
    """
    Run the experiment a single time with one fabricated election and return the distances between the committees for that election and the given numbers of questions
    :param target_committee_size: the size of the committee to be found
    :param num_candidates: the number of candidates in the election
    :param num_voters: the number of voters in the election
    :param voting_rule: the voting rule to find the committee with
    :param constrained_voting_rule: the constrained voting rule to find the committee with
    :param number_of_questions: the number of questions all voters can answer for the constrained voting rule
    :return: list of distances between all the committees
    """
    # Fabricate an election with num_candidates candidates and num_voters voters
    election = fabricate_election(num_candidates, num_voters)
    # Run the experiment
    experiment = Experiment(target_committee_size, election, voting_rule, constrained_voting_rule,
                            number_of_questions)
    # Return the distance between the two committees
    return experiment.committeeDistance


def run_experiment_wrapper(args):
    return run_experiment(*args)


def run_test(params: dict()) -> list[int]:
    """
    Run the experiment multiple times and return the average differences between the committees

    :param params: the parameters of the test
    :return: the average differences between the committees
    """
    target_committee_size = params['target_committee_size']
    num_candidates = params['num_candidates']
    num_voters = params['num_voters']
    voting_rule = params['voting_rule']
    constrained_voting_rule = params['constrained_voting_rule']
    number_of_questions = params['number_of_questions']
    number_of_runs = params['number_of_runs']
    multithreded = params['multithreded']
    if multithreded:
        with Pool() as pool:
            differences = list(tqdm(pool.imap(run_experiment_wrapper,
                                              [(
                                                  target_committee_size, num_candidates, num_voters, voting_rule,
                                                  constrained_voting_rule,
                                                  number_of_questions)
                                                  for i in range(number_of_runs)]),
                                    total=number_of_runs, desc='Running experiments'))
    else:
        differences = []
        for i in tqdm(range(number_of_runs), desc='Running experiments', total=number_of_runs):
            differences.append(
                run_experiment(target_committee_size, num_candidates, num_voters, voting_rule, constrained_voting_rule,
                               number_of_questions))
    average_differences = [0] * len(number_of_questions)
    # Average the results from the different runs
    for difference in differences:
        for i in range(len(difference)):
            average_differences[i] += difference[i]
    for i in range(len(average_differences)):
        average_differences[i] /= number_of_runs
    return average_differences


def plot_graph(test_params: dict[str, any], average_differences: list[int]) -> None:
    """
    Plots the graph for the experiment
    :param test_params: the parameters of the test
    :param average_differences: the average differences between the committees
    :return: None
    """
    matplotlib.use('TkAgg')
    # Plot the graph for the experiment
    plt.plot(test_params['number_of_questions'], average_differences)
    plt.xlabel('Number of questions')
    plt.ylabel('Distance between the committees')
    plt.suptitle(
        f"Distance between the committees for {test_params['voting_rule'].__str__()} and {test_params['constrained_voting_rule'].__str__()}")
    plt.title(
        f"with {test_params['num_voters']} voters and {test_params['num_candidates']} candidates while finding a committee of size {test_params['target_committee_size']}")
    plt.gca().xaxis.set_major_formatter(mticker.ScalarFormatter(useMathText=True))
    plt.gca().ticklabel_format(style='plain', axis='x')
    plt.show()
