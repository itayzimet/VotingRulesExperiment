#!/usr/bin/python
# -*- coding: utf-8 -*-
import bottleneck as bn
import numpy as np

from Experiment_framework.Election import Election
from Voting_rules import questionPrice
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained


class KbordaNextEq(VotingRuleConstrained):
    """
    Class for K-Borda voting rule with the next question with budget distributed equally among voters

    Methods: find_winners(election, num_winners) -> list[int]: returns the winners of the election according to the
    K-Borda rule with the next question with budget distributed equally among voters
    """
    
    @staticmethod
    def find_winners(election: Election, num_winners: int, question_limit: int) -> list[int]:
        """
        Returns a list of the winners of the election according to the K-Borda rule with first k truncated ballots with
        the budget k distributed equally among voters
        :param election: the election to find the winners for
        :param num_winners: the number of winners to find
        :param question_limit: the number of questions all voters can answer
        :return: the list of winners according to the K-Borda rule constrained by the budget of questions all voters can
        answer
        """
        # Set up the election
        voters = election.voters
        candidates = election.candidates
        num_candidates = len(candidates)
        scores = np.zeros(num_candidates, dtype = int)
        rank_scores = np.arange(num_candidates, 0, -1)  # Pre-calculate the scores for each rank
        # Calculate the budget for each voter
        questions_per_voter = question_limit // len(voters)
        # Calculate the number of questions each voter can answer based on the budget
        temp = questions_per_voter
        temp_candidates = candidates.copy()
        counter = 0
        while temp > 0 and len(temp_candidates) > 0:
            temp -= questionPrice.get_price(temp_candidates, [1 / len(temp_candidates), 1 - 1 / len(temp_candidates)])
            temp_candidates = temp_candidates[1:]
            counter += 1
        questions_per_voter = counter
        # Score the candidates based on the preferences of the voters
        for voter in voters:
            voter_preferences = voter.OrdinalPreferences[:questions_per_voter]
            scores[voter_preferences] += rank_scores[:questions_per_voter]
            # If the budget does not allow the voter to answer all questions, score the remaining candidates equally
            if questions_per_voter < num_candidates:
                scores[voter.OrdinalPreferences[questions_per_voter + 1:]] += (
                        sum(rank_scores[questions_per_voter:]) // (num_candidates - questions_per_voter))
        # Return the num_winners candidates with the highest scores
        return bn.argpartition(scores, num_winners)[-num_winners:]
    
    @staticmethod
    def __str__():
        return "K-Borda Next Questions distributed equally among voters"
