import numpy as np

from Experiment_framework.Election import Election
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained
import bottleneck as bn


class KbordaLastEq(VotingRuleConstrained):
    """
    Class for K-Borda voting rule with the last question with budget distributed equally among voters

    Methods: find_winners(election, num_winners) -> list[int]: returns the winners of the election according to the
    K-Borda rule with the last question with budget distributed equally among voters
    """

    @staticmethod
    def find_winners(election: Election, num_winners: int, question_limit: int) -> list[int]:
        """
        Returns a list of the winners of the election according to the K-Borda rule with the last question with
        budget distributed equally among voters
        :param election: the election to find the winners for
        :param num_winners: the number of winners to find
        :param question_limit: the number of questions all voters can answer
        :return: the list of winners according to the K-Borda rule constrained by the number of questions all
        voters can answer
        """
        voters = election.voters
        candidates = election.candidates
        num_candidates = len(candidates)
        scores = np.zeros(num_candidates, dtype=int)
        rank_scores = np.arange(num_candidates, 0, -1)  # Pre-calculate the scores for each rank
        # rank_scores = [0, -1, -2, -3, ..., -num_candidates]
        questions_per_voter = question_limit // len(voters)
        if questions_per_voter == 0:
            return bn.argpartition(scores, num_winners)[-num_winners:]
        for voter in voters:
            voter_preferences = voter.get_preferences()[-questions_per_voter:]
            scores[voter_preferences] += rank_scores[-questions_per_voter:]
            if questions_per_voter < num_candidates:
                scores[voter.get_preferences()[:-questions_per_voter]] += (
                        sum(rank_scores[:-questions_per_voter]) // (num_candidates - questions_per_voter))
        # Return the num_winners candidates with the highest scores using bottleneck argpartition
        return bn.argpartition(scores, num_winners)[-num_winners:]

    @staticmethod
    def __str__():
        """
        Returns the name of the voting rule
        :return: the name of the voting rule
        """
        return "K-Borda Last Questions distributed equally among voters"
