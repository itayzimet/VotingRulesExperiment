#!/usr/bin/python
# -*- coding: utf-8 -*-

from ExperimentHelper import ExperimentHelper


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
    def __init__(self, target_committee_size, election, voting_rule, constrained_voting_rule, number_of_questions):
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

    def experiment(self, ):
        """
        Runs the experiment and returns the distance between the two committees
        :return: the distance between the two committees
        """
        # Find the committees
        committee1 = self.votingRule.find_winners(self.election, self.targetCommitteeSize)
        committee2 = self.constrainedVotingRule.find_winners(self.election, self.targetCommitteeSize,
                                                             self.numberOfQuestions)
        # Print the committees
        print(f"Committee: {committee1}")
        print(f"Committee restrained: {committee2}")
        # Return the distance between the two committees
        return ExperimentHelper.committee_distance(committee1, committee2)
