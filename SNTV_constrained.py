#!/usr/bin/python
# -*- coding: utf-8 -*-

from VotingRuleConstrained import VotingRuleConstrained


class SNTV_constrained(VotingRuleConstrained):
    """
    class for Single Non-Transferable Vote voting rule constrained by the number of questions all voters can answer

    Attributes:

    Methods:
        find_winners(election, num_winners, question_limit) -> list[int]:
            Returns a list of the winners of the election according to the Single Non-Transferable Vote rule
    """
    @staticmethod
    def find_winners(election, num_winners, question_limit) -> list[int]:
        """
        Returns a list of the winners of the election according to the Single Non-Transferable Vote rule constrained by the number of questions all voters can answer
        :param election: the election to find the winners for
        :param num_winners: the number of winners to find
        :param question_limit: the number of questions all voters can answer
        :return: the list of winners according to the Single Non-Transferable Vote rule
        """
        no_of_voters = election.get_number_of_voters()
        candidates = election.get_candidates().copy() # Copy the list of candidates
        candidates_scores = [0] * len(candidates) # Initialize the scores of the candidates
        # Count the votes for each candidate until the question limit is reached
        for voter in range(no_of_voters):
            if question_limit == 0:
                break
            candidates_scores[election.voters[voter].get_next_preference()] += 1
            question_limit -= 1
        # Sort the candidates by their scores in ascending order
        candidates.sort(reverse=True, key=lambda x: candidates_scores[x])
        return candidates[:num_winners] # Return the first num_winners candidates
