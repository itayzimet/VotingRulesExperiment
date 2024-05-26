#!/usr/bin/python
# -*- coding: utf-8 -*-
from Election import Election
from ExperimentHelper import ExperimentHelper
from VotingRule import VotingRule
from VotingRuleConstrained import VotingRuleConstrained


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
