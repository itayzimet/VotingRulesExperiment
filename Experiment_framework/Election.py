#!/usr/bin/python
# -*- coding: utf-8 -*-
from Experiment_framework.Voter import Voter


class Election:
    """
    Election class is a class that represents an election. It contains the list of voters and candidates.

    Attributes:
        voters : list[Voter]
            List of voters in the election.
        candidates : list[int]
            List of candidates in the election.
        numberOfVoters : int
            Number of voters in the election.
        numberOfCandidates : int
            Number of candidates in the election.

    Methods:
        __init__(candidates: list[int], voters: list[Voter]) -> None:
            Constructor of the Election class.
    """
    
    def __init__(self, candidates: list[int], voters: list[Voter]) -> None:
        """
        Constructor of the Election class.
        :param candidates: the list of candidates
        :param voters: the list of voters
        """
        self.voters = voters
        self.candidates = candidates
        self.numberOfVoters = len(voters)
        self.numberOfCandidates = len(candidates)
