#!/usr/bin/python
# -*- coding: utf-8 -*-
import numpy as np
from Experiment_framework.Election import Election
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained
import bottleneck as bn


class KbordaSplit(VotingRuleConstrained):
    """
    Class for K-Borda voting rule constrained by the number of questions in the form of a split between preferred and
    not preferred candidates by the voter.

    Methods: find_winners(election, num_winners) -> list[int]: Returns a list of the winners of the election
    according to the K-Borda rule constrained by the number of questions all voters can answer
    """

    @staticmethod
    def find_winners(election: Election, num_winners: int, question_limit: int) -> list[int]:
        """
        Returns a list of the winners of the election according to the K-Borda rule constrained by the number of questions in the form of a split between preferred and not preferred candidates by the voter.
        :param election: the election to find the winners for
        :param num_winners: the number of winners to find
        :param question_limit: the number of questions all voters can answer
        :return: the list of winners according to the K-Borda rule constrained by the number of questions all voters can answer
        """
        voters = election.voters
        candidates = election.candidates
        num_candidates = len(candidates)
        scores = np.zeros(num_candidates, dtype=int)
        rank_scores = np.arange(num_candidates, 0, -1)
        questions_per_voter = question_limit // len(voters)
        for voter in voters:
            candidate_pool = candidates
            voter_preferences = list()
            split_amount = 0
            while split_amount < questions_per_voter:
                preferred_candidates, not_preferred_candidates = voter.split_candidates(candidate_pool)
                candidate_pool = preferred_candidates
                voter_preferences.extend(preferred_candidates)
                voter_preferences.extend(not_preferred_candidates)
                split_amount += 1
            for candidate in voter_preferences:
                scores[candidate] += rank_scores[voter_preferences.index(candidate)]
        return bn.argpartition(scores, num_winners)[-num_winners:]



    @staticmethod
    def __str__():
        return "K-Borda split"
