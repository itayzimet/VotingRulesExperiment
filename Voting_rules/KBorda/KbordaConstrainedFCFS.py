#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
from Experiment_framework.Election import Election
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained
import bottleneck as bn


class KbordaConstrainedFCFS(VotingRuleConstrained):
    """
    Class for K-Borda voting rule constrained by the number of questions all voters can answer

    Methods: find_winners(election, num_winners) -> list[int]: Returns a list of the winners of the election
    according to the K-Borda rule constrained by the number of questions all voters can answer
    """

    @staticmethod
    def find_winners(election: Election, num_winners: int, question_limit: int) -> list[int]:
        """
        Returns a list of the winners of the election according to the K-Borda rule constrained by the number of questions all voters can answer
        :param election: the election to find the winners for
        :param num_winners: the number of winners to find
        :param question_limit: the number of questions all voters can answer
        :return: the list of winners according to the K-Borda rule constrained by the number of questions all voters can answer
        """
        voters = election.voters
        candidates = election.candidates
        num_candidates = len(candidates)
        scores = np.zeros(num_candidates, dtype=int)
        rank_scores = np.arange(0, -num_candidates, -1)  # Pre-calculate the scores for each rank
        # rank_scores = [0, -1, -2, -3, ..., -num_candidates]
        max_questions_per_voter = min(question_limit // len(voters), num_candidates)
        for voter in voters:
            questions_per_voter = min(max_questions_per_voter, question_limit)
            voter_preferences = voter.get_preferences()[:questions_per_voter]
            scores[voter_preferences] += rank_scores[:questions_per_voter]
        # Return the num_winners candidates with the highest scores using bottleneck argpartition
        return bn.argpartition(scores, num_winners)[-num_winners:]

    @staticmethod
    def __str__():
        return "K-Borda Next Questions distributed first come first serve"
