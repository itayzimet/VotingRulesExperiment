"""
This module is a helper module for the main part of the experiment

It contains the following functions:
    - run_experiment(target_committee_size: int, num_candidates: int, num_voters: int, voting_rule, constrained_voting_rule, number_of_questions: list[int]) -> list[int]
    - run_experiment_wrapper(args) -> list[int]
"""
from multiprocessing import Pool
from typing import Any
from tqdm import tqdm
from Experiment_framework.Experiment import Experiment
from Experiment_framework.Experiment_helper import fabricate_election
import plotly.express as px


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
    """
    Wrapper function for the run_experiment function to allow for the use of the Pool class
    :param args: the arguments for the run_experiment function
    :return: the result of the run_experiment function
    """
    return run_experiment(*args)


def run_test(params: dict[str, any]) -> dict[Any, list[int]]:
    """
    Run the experiment multiple times and return the average differences between the committees

    :param params: the parameters of the test
    :return: the average differences between the committees
    """
    target_committee_size = params['target_committee_size']
    num_candidates = params['num_candidates']
    num_voters = params['num_voters']
    voting_rule = params['voting_rule']
    constrained_voting_rules = params['constrained_voting_rule']
    number_of_questions = params['number_of_questions']
    number_of_runs = params['number_of_runs']
    multithreaded = params['multithreaded']
    averages = {}
    for rule in constrained_voting_rules:
        if multithreaded:
            with Pool() as pool:
                differences = list(tqdm(pool.imap(run_experiment_wrapper,
                                                  [(
                                                      target_committee_size, num_candidates, num_voters, voting_rule,
                                                      rule,
                                                      number_of_questions)
                                                      for _ in range(number_of_runs)]),
                                        total=number_of_runs, desc='Running experiments'))
        else:
            differences = []
            for _ in tqdm(range(number_of_runs), desc='Running experiments', total=number_of_runs):
                differences.append(
                    run_experiment(target_committee_size, num_candidates, num_voters, voting_rule, rule,
                                   number_of_questions))
        average_differences = [0] * len(number_of_questions)
        # Average the results from the different runs
        for difference in differences:
            for i in range(len(difference)):
                average_differences[i] += difference[i]
        for i in range(len(average_differences)):
            average_differences[i] /= number_of_runs
        averages[rule.__str__()] = average_differences
    return averages


def plot_graph(test_params: dict[str, any], averages: dict[Any, list[int]]) -> None:
    """
    Plots the graph for the experiment
    :param test_params: the parameters of the test
    :param averages: the average differences between the committees for the different constrained voting rules
    :return: None
    """
    # make it a scatter plot
    fig = px.scatter()
    for rule, average in averages.items():
        fig.add_scatter(x=list(test_params['number_of_questions']), y=average, mode='markers', name=rule.__str__())
    fig.update_layout(title=f"{test_params['voting_rule'].__str__()}: {test_params['target_committee_size']} committee members, {test_params['num_candidates']} candidates, {test_params['num_voters']} voters, {test_params['number_of_runs']} runs",
                      xaxis_title='Number of questions',
                      yaxis_title='Distance between the committees')

    fig.show()
