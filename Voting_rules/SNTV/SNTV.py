#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np

from Experiment_framework.Election import Election
from Voting_rules.VotingRule import VotingRule


class SNTV(VotingRule):
    """
    Class for Single Non-Transferable Vote voting rule

    Methods:
        find_winners(election, num_winners) -> list[int]:
            Returns a list of the winners of the election according to the Single Non-Transferable Vote rule
    """

    @staticmethod
    def find_winners(election: Election, num_winners: int) -> list[int]:
        """
        Returns a list of the winners of the election according to the Single Non-Transferable Vote rule
        :param election: the election to find the winners for
        :param num_winners: the number of winners to find
        :return: the list of winners according to the Single Non-Transferable Vote rule
        """
        no_of_voters = election.numberOfVoters
        candidates = election.candidates  # Copy the list of candidates
        scores = [0] * len(candidates)  # Initialize the scores of the candidates
        # Count the votes for each candidate
        for voter in range(no_of_voters):
            scores[election.voters[voter].get_preference(0)] += 1
        # partially sort the candidates by their scores in descending order using argpartition() to get the
        # num_winners first candidates
        candidates = np.array(candidates)
        scores = np.array(scores)
        candidates = candidates[np.argpartition(-scores, num_winners)[:num_winners]]
        return candidates.tolist()

    @staticmethod
    def __str__():
        return "SNTV"
