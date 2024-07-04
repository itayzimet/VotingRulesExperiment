import inspect

import numpy as np

from Experiment_framework.Voter import Voter
from Voting_rules import questionPrice
from Voting_rules.KBorda.Node import Node


class KbordaHelper:
    """
    Helper class for the K-Borda rule
    
    Attributes:
    questions: list of the question budget for each voter
    questions_limit: the budget for the questions
    
    Methods:
    score_candidates(node: Node, scores: np.ndarray, rank: int) -> None
    
    """
    questions = []
    
    def __init__(self, questions: list[int]):
        self.questions = questions.copy()
    
    @staticmethod
    def score_candidates(node: Node, scores: np.ndarray, rank: int):
        """
        Recursively score the candidates based on the tree created using the K-Borda rule
        :param node: the current node of the binary tree
        :param scores: the scores of the candidates
        :param rank: the rank of the candidate
        :return: None
        """
        if len(node.sons) <= 1:  # node is a leaf
            # score them all based on the position of the leaf regardless of the order in the leaf
            scores[node.value] += rank - len(node.value) // 2
            return
        for i, son in enumerate(node.sons):
            if i == 0:
                KbordaHelper.score_candidates(son, scores, rank)
            else:
                rank -= len(node.sons[i - 1].value)
                KbordaHelper.score_candidates(son, scores, rank)
    
    def fill_tree(self, voter: Voter, current_node: Node, voter_idx: int, question_type: list[float]) -> None:
        """
        Recursively create a binary tree to split the preferences of the voter
        :param voter: the voter to split the preferences for
        :param current_node: the current node of the binary tree
        :param voter_idx: the index of the voter
        :param question_type: the question type to split according to
        :return: None
        """
        if self.questions[voter_idx] <= 0 or len(current_node.value) <= 1:
            return
        if len(inspect.stack(0)) >= 30:
            return
        self.questions[voter_idx] -= questionPrice.get_price(current_node.value, question_type)
        buckets = voter.general_bucket_question(current_node.value, question_type.copy())
        for bucket in buckets:
            current_node.sons.append(Node(bucket))
            self.fill_tree(voter, current_node.sons[-1], voter_idx, question_type)
