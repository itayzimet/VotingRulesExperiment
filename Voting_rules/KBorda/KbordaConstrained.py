#!/usr/bin/python
# -*- coding: utf-8 -*-
from Election import Election
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained


class KbordaConstrained(VotingRuleConstrained):
    """
    Class for K-Borda voting rule constrained by the number of questions all voters can answer

    Attributes:

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
        voters = election.get_voters()
        candidates = election.get_candidates().copy()
        num_candidates = len(candidates)
        scores = [0] * len(candidates)
        questions_per_voter = question_limit//len(voters)
        for voter in voters:
            limit = questions_per_voter
            if limit == 0:
                break
            next_preference = voter.get_next_preference()
            scores[next_preference] += num_candidates - voter.get_candidate_index(next_preference)
            limit -= 1
        candidates.sort(reverse=True, key=lambda x: scores[x])
        election.reset()
        return candidates[:num_winners]



    @staticmethod
    def __str__():
        return "K-Borda constrained"
