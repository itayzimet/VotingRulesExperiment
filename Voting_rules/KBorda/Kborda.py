#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np

from Experiment_framework.Election import Election
from Voting_rules.VotingRule import VotingRule
import bottleneck as bn


class Kborda(VotingRule):
    """
    Class for K-Borda voting rule

    Methods:
        find_winners(election, num_winners) -> list[int]:
            Returns a list of the winners of the election according to the K-Borda rule
        __str__() -> str:
            Returns the name of the voting rule
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
        num_candidates = election.numberOfCandidates
        # Initialize the scores of the candidates
        scores = np.zeros(num_candidates, dtype = int)
        # Pre-calculate the scores for each rank
        rank_scores = np.arange(num_candidates, 0, -1)
        # Count the votes for each candidate
        for voter in voters:
            voter_preferences = voter.OrdinalPreferences
            scores[voter_preferences] += rank_scores
        # Return the num_winners candidates with the highest scores using bottleneck argsort
        return bn.argpartition(scores, num_winners)[-num_winners:]
    
    @staticmethod
    def calculate_scores(election: Election) -> list[int]:
        # Get the voters, candidates and the number of candidates
        voters = election.voters
        num_candidates = election.numberOfCandidates
        # Initialize the scores of the candidates
        scores = np.zeros(num_candidates, dtype = int)
        # Pre-calculate the scores for each rank
        rank_scores = np.arange(num_candidates, 0, -1)
        # Count the votes for each candidate
        for voter in voters:
            voter_preferences = voter.OrdinalPreferences
            scores[voter_preferences] += rank_scores
        return list(scores)
    
    @staticmethod
    def __str__():
        """
        Returns the name of the voting rule
        :return: the name of the voting rule
        """
        return "K-Borda"
