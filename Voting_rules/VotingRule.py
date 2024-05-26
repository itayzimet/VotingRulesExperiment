#!/usr/bin/python
# -*- coding: utf-8 -*-
from Experiment_framework.Election import Election


class VotingRule:
    """
    Abstract class for voting rules

    Attributes:

    Methods:
        find_winners(election, num_winners) -> list[int]:
            Returns a list of the winners of the election
    """
    @staticmethod
    def find_winners(election: Election, num_winners: int) -> list[int]:
        """
        Returns a list of the winners of the election
        :param election: the election to find the winners of
        :param num_winners: the number of winners to find
        :return: a list of the winners of the election
        """
        pass

    @staticmethod
    def __str__():
        return "Voting Rule"