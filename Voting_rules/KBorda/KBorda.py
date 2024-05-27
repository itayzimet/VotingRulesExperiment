#!/usr/bin/python
# -*- coding: utf-8 -*-
from Experiment_framework.Election import Election
from Voting_rules.VotingRule import VotingRule
from heapq import nlargest


class KBorda(VotingRule):
    """
    Class for K-Borda voting rule

    Methods:
        find_winners(election, num_winners) -> list[int]:
            Returns a list of the winners of the election according to the K-Borda rule
    """

    @staticmethod
    def find_winners(election: Election, num_winners: int) -> list[int]:
        """
        Returns a list of the winners of the election according to the K-Borda rule
        :param election: the election to find the winners for
        :param num_winners: the number of winners to find
        :return: the list of winners according to the K-Borda rule
        """
        # Get the voters, candidates and the number of candidates
        voters = election.voters
        candidates = election.candidates
        num_candidates = election.numberOfCandidates
        # Initialize the scores of the candidates
        scores = [0] * len(candidates)
        # Sum the scores of the candidates based on the preferences of the voters
        for voter in voters:
            for i, candidate in enumerate(voter.get_preferences()):
                scores[candidate] += num_candidates - i

        # Return the num_winners candidates with the highest scores
        return nlargest(num_winners, candidates, key=scores.__getitem__)

    @staticmethod
    def __str__():
        return "K-Borda"
