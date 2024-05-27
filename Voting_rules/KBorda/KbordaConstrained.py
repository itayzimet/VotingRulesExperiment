#!/usr/bin/python
# -*- coding: utf-8 -*-
from heapq import nlargest


from Experiment_framework.Election import Election
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained


class KbordaConstrained(VotingRuleConstrained):
    """
    Class for K-Borda voting rule constrained by the number of questions all voters can answer

    Methods:
        find_winners(election, num_winners) -> list[int]:
            Returns a list of the winners of the election according to the K-Borda rule constrained by the number of questions all voters can answer
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
        scores = [0] * len(candidates)
        questions_per_voter = int(question_limit / len(voters))
        for voter in voters:
            questions_answered = 0
            for i in range(num_candidates):
                if questions_answered >= questions_per_voter or i >= num_candidates:
                    break
                scores[voter.get_preference(i)] += num_candidates - i
                questions_answered += 1
        # Return the num_winners candidates with the highest scores
        return nlargest(num_winners, candidates, key=scores.__getitem__)

    @staticmethod
    def __str__():
        return "K-Borda constrained"
