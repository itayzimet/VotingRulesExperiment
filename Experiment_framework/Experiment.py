#!/usr/bin/python
# -*- coding: utf-8 -*-
from random import random

from Election import Election
from Experiment import ExperimentHelper
from Voter import Voter
from Voting_rules.VotingRule import VotingRule
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained


class Experiment:
    """
    Class for the experiment

    Attributes:
        targetCommitteeSize : int
            The size of the committee to be found
        election : Election
            The election to find the committee for
        votingRule : VotingRule
            The voting rule to find the committee with
        constrainedVotingRule : VotingRuleConstrained
            The constrained voting rule to find the committee with
        numberOfQuestions : int
            The number of questions all voters can answer
    Methods:
        experiment() -> int:
            Runs the experiment and returns the distance between the two committees
    """

    def __init__(self, target_committee_size: int, election: Election, voting_rule: VotingRule,
                 constrained_voting_rule: VotingRuleConstrained, number_of_questions: int):
        """
        Constructor of the Experiment class
        :param target_committee_size: the size of the committee to be found
        :param election: the election to find the committee for
        :param voting_rule: the voting rule to find the committee with
        :param constrained_voting_rule: the constrained voting rule to find the committee with
        :param number_of_questions: the number of questions all voters can answer for the constrained voting rule
        """
        self.targetCommitteeSize = target_committee_size
        self.election = election
        self.votingRule = voting_rule
        self.constrainedVotingRule = constrained_voting_rule
        self.numberOfQuestions = number_of_questions

        # Find the committees
        self.committee1 = self.votingRule.find_winners(self.election, self.targetCommitteeSize)
        self.committee2 = self.constrainedVotingRule.find_winners(self.election, self.targetCommitteeSize,
                                                                  self.numberOfQuestions)
        # sort the committees
        self.committee1.sort()
        self.committee2.sort()

        # Calculate the distance between the committees
        self.committeeDistance = ExperimentHelper.committee_distance(self.committee1, self.committee2)

    def __str__(self):
        new_line = '\n'
        return f"""Experiment with candidates: {self.election.candidates}
voters:
{new_line.join([x.__str__() for x in self.election.voters])}
target committee size: {self.targetCommitteeSize}
voting rule: {self.votingRule.__str__()}
constrained voting rule: {self.constrainedVotingRule.__str__()}
number of questions: {self.numberOfQuestions}
committee by voting rule: {self.committee1}
committee by constrained voting rule: {self.committee2}
committee distance: {self.committeeDistance}"""

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
    def fabricate_election(number_of_candidates: int, number_of_voters: int) -> Election:
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
        return int(len(set(committee1).symmetric_difference(set(committee2)))/2)

