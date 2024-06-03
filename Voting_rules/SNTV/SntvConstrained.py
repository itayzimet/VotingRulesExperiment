#!/usr/bin/python
# -*- coding: utf-8 -*-
from Experiment_framework.Election import Election
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained
import bottleneck as bn


class SntvConstrained(VotingRuleConstrained):
    """
    class for Single Non-Transferable Vote voting rule constrained by the number of questions all voters can answer

    Methods:
        find_winners(election, num_winners, question_limit) -> list[int]:
            Returns a list of the winners of the election according to the Single Non-Transferable Vote rule
    """

    @staticmethod
    def find_winners(election: Election, num_winners: int, question_limit: int) -> list[int]:
        """
        Returns a list of the winners of the election according to the Single Non-Transferable Vote rule constrained by the number of questions all voters can answer
        :param election: the election to find the winners for
        :param num_winners: the number of winners to find
        :param question_limit: the number of questions all voters can answer
        :return: the list of winners according to the Single Non-Transferable Vote rule
        """
        no_of_voters = election.numberOfVoters
        candidates = election.candidates  # Copy the list of candidates
        scores = [0] * len(candidates)  # Initialize the scores of the candidates
        # Count the votes for each candidate until the question limit is reached
        for voter in range(min(no_of_voters, question_limit)):
            scores[election.voters[voter].OrdinalPreferences[0]] += 1
            question_limit -= 1
        # Return the num_winners candidates with the highest scores using bottleneck argsort
        return bn.argpartition(scores, num_winners)[-num_winners:]

    @staticmethod
    def __str__():
        return "SNTV constrained"
