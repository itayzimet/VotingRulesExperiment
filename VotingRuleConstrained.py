#!/usr/bin/python
# -*- coding: utf-8 -*-

from VotingRule import VotingRule


class VotingRuleConstrained(VotingRule):
    """
    Abstract class for voting rules with constraints

    Attributes:

    Methods:
        find_winners(election, question_limit) -> list[int]:
            Returns a list of the winners of the election
    """
    @staticmethod
    def find_winners(election, question_limit) -> list[int]:
        """
        Returns a list of the winners of the election
        :param election: the election to find the winners of
        :param question_limit: the number of questions that can be asked
        :return: the list of winners of the election
        """
        pass
