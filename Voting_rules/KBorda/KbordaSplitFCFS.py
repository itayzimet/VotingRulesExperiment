#!/usr/bin/python
# -*- coding: utf-8 -*-
import bottleneck as bn
import numpy as np

from Experiment_framework.Election import Election
from Voting_rules.KBorda.KbordaHelper import KbordaHelper
from Voting_rules.KBorda.Node import Node
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained


class KbordaSplitFCFS(VotingRuleConstrained):
    """
    Class for K-Borda voting rule constrained by the number of questions in the form of a split between preferred and
    not preferred candidates by the voter distributed First Come First Serve among voters.

    Methods: find_winners(election, num_winners) -> list[int]: Returns a list of the winners of the election
    according to the K-Borda rule constrained by the number of questions in the form of a split between preferred and
    not preferred candidates by the voter distributed First Come First Serve among voters.
    """

    @staticmethod
    def find_winners(election: Election, num_winners: int, question_limit: int) -> list[int]:
        """
        Returns a list of the winners of the election according to the K-Borda rule constrained by the number of
        questions in the form of a split between preferred and not preferred candidates by the voter distributed First
        Come First Serve among voters.
        :param election: the election to find the winners for
        :param num_winners: the number of winners to find
        :param question_limit: the number of questions all voters can answer
        :return: the list of winners according to the K-Borda rule constrained by the number of questions
        in the form of a split between preferred and not preferred candidates by the voter distributed First Come
        First Serve among voters.
        """
        voters = election.voters
        candidates = election.candidates
        num_candidates = len(candidates)
        scores = np.zeros(num_candidates, dtype=int)
        helper = KbordaHelper([question_limit])
        for idx, voter in enumerate(voters):
            # Create a binary tree to split the preferences of the voter
            root_node = Node(candidates)
            helper.fill_tree(voter, root_node, 0, [0.5, 0.5])
            # Score the candidates based on the tree created, if there is a leaf with multiple candidates,
            # score them all based on the position in the leaf regardless of the order in the leaf
            rank = num_candidates
            KbordaHelper.score_candidates(root_node, scores, rank)

        # Return the num_winners candidates with the highest scores using bottleneck argpartition
        return bn.argpartition(scores, num_winners)[-num_winners:]
    
    @staticmethod
    def __str__():
        return "K-Borda split questions distributed First Come First Serve"
