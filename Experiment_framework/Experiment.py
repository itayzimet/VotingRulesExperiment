#!/usr/bin/python
# -*- coding: utf-8 -*-
from Voting_rules.VotingRule import VotingRule
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained
from Experiment_framework.Experiment_helper import *


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
        __init__(target_committee_size: int, election: Election, voting_rule: VotingRule,
                    constrained_voting_rule: VotingRuleConstrained, number_of_questions: list[int])
                Constructor of the Experiment class. it sets the attributes and finds the committees
        export_to_excel()
            Exports the data to an Excel file
        __str__()
            Returns a string representation of the Experiment
    """
    
    def __init__(self, target_committee_size: int, election: Election, voting_rule: VotingRule,
                 constrained_voting_rule: VotingRuleConstrained, number_of_questions: list[int]):
        """
        Constructor of the Experiment class
        :type constrained_voting_rule: VotingRuleConstrained
        :param target_committee_size: the size of the committee to be found
        :param election: the election to find the committee for
        :param voting_rule: the voting rule to find the committee with
        :param constrained_voting_rule: the constrained voting rule to find the committee with
        :param number_of_questions: the number of questions all voters can answer for the constrained voting rule
        """
        # Set the attributes
        self.targetCommitteeSize = target_committee_size
        self.election = election
        self.votingRule = voting_rule
        self.constrainedVotingRule = constrained_voting_rule
        self.numberOfQuestions = number_of_questions
        
        # Find the committees
        self.true_committee = self.votingRule.find_winners(self.election, self.targetCommitteeSize)
        self.committees = []
        self.committeeDistance = []
        # Find the committees with the constrained voting rule
        for i in self.numberOfQuestions:
            rule = constrained_voting_rule()
            self.committees.append(rule.find_winners(self.election, self.targetCommitteeSize, i))
        # find the distance between the true committee and the committees
        for committee in self.committees:
            self.committeeDistance.append(committee_distance(self.true_committee, committee))
    
    def export_to_excel(self) -> 'Experiment':
        """
        Exports the data to an Excel file
        :return: the Experiment object
        """
        # Create a Pandas DataFrame with the data
        data = {'Number of questions': self.numberOfQuestions,
                'Committee distance': self.committeeDistance,
                'Committees': self.committees,
                'True committee': [self.true_committee] * len(self.numberOfQuestions)}
        df = pd.DataFrame(data)
        # Write the DataFrame to an Excel file
        df.to_excel(f"{self.votingRule.__str__()}_{self.constrainedVotingRule.__str__()}.xlsx")
        return self
    
    def __str__(self):
        new_line = '\n'
        return f"""Experiment with candidates: {self.election.candidates}
    voters:
    {new_line.join([x.__str__() for x in self.election.voters])}
    target committee size: {self.targetCommitteeSize}
    voting rule: {self.votingRule.__str__()}
    constrained voting rule: {self.constrainedVotingRule.__str__()}
    number of questions: {self.numberOfQuestions}
    committee by voting rule: {self.true_committee}
    committees by constrained voting rule: {self.committees}
    committee distance: {self.committeeDistance}"""
