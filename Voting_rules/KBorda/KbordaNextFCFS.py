#!/usr/bin/python
# -*- coding: utf-8 -*-
import bottleneck as bn
import numpy as np

from Experiment_framework.Election import Election
from Voting_rules import questionPrice
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained


class KbordaNextFCFS(VotingRuleConstrained):
    """
    Class for K-Borda voting rule constrained by the number of questions all voters can answer

    Methods: find_winners(election, num_winners) -> list[int]: Returns a list of the winners of the election
    according to the K-Borda rule with the next question distributed first come first serve
    """
    
    name = "K-Borda Next first come first serve"
    
    @staticmethod
    def find_winners(election: Election, num_winners: int, question_limit: int) -> list[int]:
        """
        Returns a list of the winners of the election according to the K-Borda rule with first k truncated ballots with
        the budget k distributed according to the first-come-first-serve principle
        :param election: the election to find the winners for
        :param num_winners: the number of winners to find
        :param question_limit: the number of questions all voters can answer
        :return: a list of the winners of the election according to the K-Borda rule with the next question distributed
        first come first serve
        """
        # Initialize variables
        voters = election.voters
        candidates = election.candidates
        num_candidates = len(candidates)
        scores = np.zeros(num_candidates, dtype = int)
        rank_scores = np.arange(num_candidates, 0, -1)
        # Calculate the budget for each voter
        temp = question_limit
        for voter in voters:
            # Calculate the amount of questions that this voter can be asked
            temp_candidates = candidates.copy()
            counter = 0
            while temp > 0 and len(temp_candidates) > 1:
                temp -= questionPrice.get_price(temp_candidates,
                                                [1 / len(temp_candidates), 1 - 1 / len(temp_candidates)])
                temp_candidates = temp_candidates[1:]
                counter += 1
            questions_per_voter = counter
            # Calculate the scores of the candidates
            voter_preferences = voter.OrdinalPreferences[:questions_per_voter]
            scores[voter_preferences] += rank_scores[:questions_per_voter]
            if questions_per_voter < num_candidates:
                scores[voter.OrdinalPreferences[questions_per_voter + 1:]] += (
                        sum(rank_scores[questions_per_voter:]) // (num_candidates - questions_per_voter))
        # Return the num_winners candidates with the highest scores
        return bn.argpartition(scores, num_winners)[-num_winners:]
