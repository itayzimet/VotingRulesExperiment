#!/usr/bin/python
# -*- coding: utf-8 -*-
from Voter import Voter


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
        get_voter(voter_id) -> Voter:
            Returns the voter with the given id.
        get_voters() -> list[Voter]:
            Returns the list of voters.
        get_candidates() -> list[int]:
            Returns the list of candidates.
        get_number_of_voters() -> int:
            Returns the number of voters.
        get_number_of_candidates() -> int:
            Returns the number of candidates.
        reset() -> None:
            Resets the votes of all voters to 0.
    """

    def __init__(self, candidates, voters) -> None:
        """
        Constructor of the Election class.
        :param candidates: the list of candidates
        :param voters: the list of voters
        """
        self.voters = voters
        self.candidates = candidates
        self.numberOfVoters = len(voters)
        self.numberOfCandidates = len(candidates)

    def get_voter(self, voter_id) -> Voter:
        """
        Returns the voter with the given id.
        :param voter_id: the id of the voter
        :return: the voter with the given id
        """
        return self.voters[voter_id]

    def get_voters(self, ) -> list[Voter]:
        """
        Returns the list of voters.
        :return: the list of voters
        """
        return self.voters

    def get_candidates(self, ) -> list[int]:
        """
        Returns the list of candidates.
        :return: the list of candidates
        """
        return self.candidates

    def get_number_of_voters(self, ) -> int:
        """
        Returns the number of voters.
        :return: the number of voters
        """
        return self.numberOfVoters

    def get_number_of_candidates(self, ) -> int:
        """
        Returns the number of candidates.
        :return: the number of candidates
        """
        return self.numberOfCandidates

    def reset(self, ) -> None:
        """
        Resets the votes of all voters to 0.
        :return: None
        """
        for voter in self.voters:
            voter.reset()
        return None
