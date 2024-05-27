#!/usr/bin/python
# -*- coding: utf-8 -*-
from heapq import nlargest

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
        candidates = election.candidates  # Copy the list of candidates
        voters = election.voters  # Copy the list of voters
        scores = [0] * len(candidates)  # Initialize the scores of the candidates
        # Count the votes for each candidate
        for voter in voters:
            scores[voter.get_preference(0)] += 1
        ## Return the num_winners candidates with the highest scores
        return nlargest(num_winners, candidates, key=scores.__getitem__)

    @staticmethod
    def __str__():
        return "SNTV"
