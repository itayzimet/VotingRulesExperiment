#!/usr/bin/python
# -*- coding: utf-8 -*-
from Experiment_framework.Election import Election
from Voting_rules.VotingRule import VotingRule


class KBorda(VotingRule):
    """
    Class for K-Borda voting rule

    Attributes:

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
        voters = election.get_voters()
        candidates = election.get_candidates().copy()
        num_candidates = len(candidates)
        scores = [0] * len(candidates)
        for voter in voters:
            for i, candidate in enumerate(voter.get_preferences()):
                scores[candidate] += num_candidates - i
        candidates.sort(reverse=True, key=lambda x: scores[x])
        return candidates[:num_winners]

    @staticmethod
    def __str__():
        return "K-Borda"
