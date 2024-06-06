import numpy as np
import pandas as pd

from Experiment_framework.Election import Election
from Experiment_framework.Voter import Voter

"""
This module is a helper module for the experiment

It contains the following functions: - fabricate_election(number_of_candidates: int, number_of_voters: int) -> 
Election - committee_distance(committee1: list[int], committee2: list[int]) -> int - export_to_excel(
number_of_questions: list[int], distances: list[list[int]]) -> None - run_experiment(target_committee_size: int, 
num_candidates: int, num_voters: int, voting_rule, constrained_voting_rule, number_of_questions: list[int]) -> list[
int] - run_experiment_wrapper(args) -> list[int]"""


def fabricate_election(number_of_candidates: int, number_of_voters: int) -> Election:
    """
    Fabricates an election with the given number of candidates and voters randomly
    :param number_of_candidates: the number of candidates
    :param number_of_voters: the number of voters
    :return: the fabricated election
    """
    # Create the candidates
    candidates = []
    for i in range(number_of_candidates):
        candidates.append(i)
    # Create the voters
    voters = list()
    for i in range(number_of_voters):
        # Shuffle the candidates using numpy.random.permutation
        voter_ordinal_preferences = np.random.permutation(candidates).tolist()
        voter = Voter(voter_ordinal_preferences)  # Create the voter
        voters.append(voter)  # Add the voter to the list of voters
    return Election(candidates, voters)  # Return the fabricated election


def committee_distance(committee1: list[int], committee2: list[int]) -> int:
    """
    Returns the distance between two committees
    :param committee1: the first committee
    :param committee2: the second committee
    :return: the distance between the two committees
    """
    # Return the size of the symmetric difference between the two committees
    return int(len(set(committee1).symmetric_difference(set(committee2))) / 2)


def export_to_excel(number_of_questions: list[int], distances: list[list[int]]) -> None:
    """
    Exports the data from the experiments to an Excel file
    :param number_of_questions: the number of questions all voters can answer
    :param distances: the distances between the true committee and the committees found
    :return: None
    """
    # Create a Pandas DataFrame with the data from the experiments on the left the number of questions(only once) and
    # on the right the committee distances found in each experiment for that number of questions
    data = {'Number of questions': number_of_questions}
    for i in range(len(distances)):
        data[f'Committee distance {i}'] = distances[i]
    df = pd.DataFrame(data)
    # Write the DataFrame to an Excel file
    df.to_excel(f"Experiments.xlsx")
