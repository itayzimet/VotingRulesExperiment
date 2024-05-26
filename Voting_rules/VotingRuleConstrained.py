#!/usr/bin/python
# -*- coding: utf-8 -*-
from Experiment_framework.Election import Election
from Voting_rules.VotingRule import VotingRule


class VotingRuleConstrained(VotingRule):
    """
    Abstract class for voting rules with constraints

    Attributes:

    Methods:
        find_winners(election, question_limit) -> list[int]:
            Returns a list of the winners of the election
    """
    @staticmethod
    def find_winners(election: Election, num_winners:int, question_limit: int) -> list[int]:
        """
        Returns a list of the winners of the election
        :param num_winners: the number of winners to find
        :param election: the election to find the winners of
        :param question_limit: the number of questions that can be asked
        :return: the list of winners of the election
        """
        pass

    @staticmethod
    def __str__():
        return "Constrained Voting Rule"
