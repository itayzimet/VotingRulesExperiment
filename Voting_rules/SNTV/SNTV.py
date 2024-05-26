#!/usr/bin/python
# -*- coding: utf-8 -*-
from Election import Election
from Voting_rules.VotingRule import VotingRule


class SNTV(VotingRule):
    """
    Class for Single Non-Transferable Vote voting rule

    Attributes:

    Methods:
        find_winners(election, num_winners) -> list[int]:
            Returns a list of the winners of the election according to the Single Non-Transferable Vote rule
    """
    @staticmethod
    def find_winners(election: Election, num_winners: int) -> list[int]:
        """
        Returns a list of the winners of the election according to the Single Non-Transferable Vote rule
        :param election: the election to find the winners for
        :param num_winners: the number of winners to find
        :return: the list of winners according to the Single Non-Transferable Vote rule
        """
        no_of_voters = election.get_number_of_voters()
        candidates = election.get_candidates().copy() # Copy the list of candidates
        candidates_scores = [0] * len(candidates) # Initialize the scores of the candidates
        # Count the votes for each candidate
        for voter in range(no_of_voters):
            candidates_scores[election.voters[voter].get_next_preference()] += 1
        # Sort the candidates by their scores in ascending order
        candidates.sort(reverse=True, key=lambda x: candidates_scores[x])
        election.reset() # Reset the election
        return candidates[:num_winners] # Return the first num_winners candidates

    @staticmethod
    def __str__():
        return "Single Non-Transferable Vote"
