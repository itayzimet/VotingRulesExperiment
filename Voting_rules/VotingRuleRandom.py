#!/usr/bin/python
# -*- coding: utf-8 -*-
from random import randint

from Experiment_framework.Election import Election
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained


class VotingRuleRandom(VotingRuleConstrained):
    """
    Abstract class for voting rules with constraints

    Methods:
        find_winners(election, question_limit) -> list[int]:
            Returns a random list of winners of the election
    """
    
    @staticmethod
    def find_winners(election: Election, num_winners: int, question_limit: int) -> list[int]:
        """
        Returns a random list of winners of the election
        :param election: the election to find the winners for
        :param num_winners: the number of winners to find
        :param question_limit: the number of questions all voters can answer
        :return: a random list of winners of the election
        """
        winners = []
        for i in range(election.numberOfCandidates):
            winners.append(randint(0, election.numberOfCandidates - 1))
        return winners
    
    @staticmethod
    def __str__():
        return "Random voting rule"
