#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
from Experiment_framework.Election import Election
from Experiment_framework.Voter import Voter
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained
import bottleneck as bn


class Node:
    def __init__(self, value):
        """
        Constructor for the Node class
        :param value: the value of the node
        """
        self.value = value
        self.left = None
        self.right = None


class KbordaSplitEq(VotingRuleConstrained):
    """
    Class for K-Borda voting rule constrained by the number of questions in the form of a split between preferred and
    not preferred candidates by the voter distributed equally among voters.

    Methods: find_winners(election, num_winners) -> list[int]: Returns a list of the winners of the election
    according to the K-Borda rule constrained by the number of questions in the form of a split between preferred and
    not preferred candidates by the voter distributed equally among voters.
    """
    questions_limit = []

    def find_winners(self, election: Election, num_winners: int, question_limit: int) -> list[int]:
        """
        Returns a list of the winners of the election according to the K-Borda rule constrained by the number of
        questions in the form of a split between preferred and not preferred candidates by the voter.
        :param election: the election to find the winners for
        :param num_winners: the number of winners to find
        :param question_limit: the number of questions all voters can answer
        :return: the list of winners according to the K-Borda rule constrained by the number of questions
        in the form of a split between preferred and not preferred candidates by the voter.
        """
        voters = election.voters
        candidates = election.candidates
        num_candidates = len(candidates)
        scores = np.zeros(num_candidates, dtype=int)
        self.questions_limit = [question_limit // len(voters)] * len(voters)
        for i, voter in enumerate(voters):
            # Carefully split the preferences of the voter into preferred and not preferred candidates multiple times
            # to get the voters preferences. Don't use get_preferences() or directly use the preferences of the voter
            # as it is disallowed in the constraints. Get the preferences using a binary tree
            if self.questions_limit[i] == 0:
                break
            # Create a binary tree to split the preferences of the voter
            root_node = Node(candidates)
            self.__split_preferences(i, voter, root_node)
            # Score the candidates based on the tree created
            # score them all based on the position in the leaf regardless of the order in the leaf
            rank = num_candidates
            self.__score_candidates(root_node, scores, rank)

        # Return the num_winners candidates with the highest scores using bottleneck argpartition
        return bn.argpartition(scores, num_winners)[-num_winners:]

    def __score_candidates(self, current_node: Node, scores: np.ndarray, rank: int):
        """
        Recursively score the candidates based on the tree created
        :param current_node: the current node of the binary tree
        :param scores: the scores of the candidates
        :param rank: the rank of the candidate
        :return: None
        """
        if current_node.left is None and current_node.right is None:
            scores[current_node.value] += rank - len(current_node.value)//2
            return
        self.__score_candidates(current_node.left, scores, rank)
        self.__score_candidates(current_node.right, scores, rank - len(current_node.left.value))

    def __split_preferences(self, voter_index: int, voter: Voter, current_node: Node):
        """
        Recursively create a binary tree to split the preferences of the voter
        :param voter_index: the index of the voter
        :param voter: the voter
        :param current_node: the current node of the binary tree
        :return: None
        """
        # Recursively create a binary tree to split the preferences of the voter
        if self.questions_limit[voter_index] == 0 or len(current_node.value) == 1:
            return
        temp = voter.split_candidates(current_node.value)
        current_node.left = Node(temp[0])
        current_node.right = Node(temp[1])
        self.questions_limit[voter_index] -= 1
        self.__split_preferences(voter_index, voter, current_node.left)
        self.__split_preferences(voter_index, voter, current_node.right)

    @staticmethod
    def __str__():
        """
        Returns the name of the voting rule
        :return: the name of the voting rule
        """
        return "K-Borda split questions distributed equally among voters"
