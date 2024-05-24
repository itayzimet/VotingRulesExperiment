#!/usr/bin/python
#-*- coding: utf-8 -*-

from ExperimentHelper import ExperimentHelper


class Experiment:
    def __init__(self):
        self.targetCommitteeSize = None
        self.election = None
        self.votingRule = None
        self.constrainedVotingRule = None
    def __init__(self, targetCommitteeSize, election, votingRule, constrainedVotingRule, numberOfQuestions):
        self.targetCommitteeSize = targetCommitteeSize
        self.election = election
        self.votingRule = votingRule
        self.constrainedVotingRule = constrainedVotingRule
        self.numberOfQuestions = numberOfQuestions

    def experiment(self, ):
        committee1 = self.votingRule.findWinners(self.election, self.targetCommitteeSize)
        committee2 = self.constrainedVotingRule.findWinners(self.election, self.targetCommitteeSize, self.numberOfQuestions)
        print(f"Committee: {committee1}")
        print(f"Committee restrained: {committee2}")
        return ExperimentHelper.committeeDistance(committee1, committee2)
