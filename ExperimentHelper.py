#!/usr/bin/python
# -*- coding: utf-8 -*-
import random

from Election import Election
from Voter import Voter


class ExperimentHelper:
    """
    Helper class for the experiment
    Attributes:

    Methods:
        fabricate_election(number_of_candidates, number_of_voters) -> Election:
            Fabricates an election with the given number of candidates and voters
        committee_distance(committee1, committee2) -> int:
            Returns the distance between two committees
    """
    @staticmethod
    def fabricate_election(number_of_candidates, number_of_voters) -> Election:
        """
        Fabricates an election with the given number of candidates and voters randomly
        :param number_of_candidates: the number of candidates
        :param number_of_voters: the number of voters
        :return: the fabricated election
        """
        # Create the candidates
        candidates = []
        for i in range(number_of_candidates):
            candidates.append(i)
        # Create the voters
        voters = list()
        for i in range(number_of_voters):
            voter_ordinal_preferences = random.sample(candidates, number_of_candidates)  # Randomly shuffle the candidates
            voter = Voter(voter_ordinal_preferences)  # Create the voter
            voters.append(voter)  # Add the voter to the list of voters
        return Election(candidates, voters)  # Return the fabricated election

    @staticmethod
    def committee_distance(committee1, committee2) -> int:
        """
        Returns the distance between two committees
        :param committee1: the first committee
        :param committee2: the second committee
        :return: the distance between the two committees
        """
        # Return the size of the symmetric difference between the two committees
        return len(set(committee1).symmetric_difference(set(committee2)))
