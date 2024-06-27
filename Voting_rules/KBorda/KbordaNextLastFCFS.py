from Experiment_framework.Election import Election
from Voting_rules import questionPrice
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained
import numpy as np
import bottleneck as bn


class KbordaNextLastFCFS(VotingRuleConstrained):
    """
    Class for K-Borda voting rule with the next and last questions with budget distributed equally among voters

    Methods: find_winners(election, num_winners) -> list[int]: returns the winners of the election according to the
    K-Borda rule with the next and last questions with budget distributed equally among voters
    """

    @staticmethod
    def find_winners(election: Election, num_winners: int, question_limit: int) -> list[int]:
        """
        Returns a list of the winners of the election according to the K-Borda rule with the next and last questions with
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
        rank_scores = np.arange(num_candidates, 0, -1)
        # Pre-calculate the scores for each rank
        # rank_scores = [0, -1, -2, -3, ..., -num_candidates]
        max_questions_per_voter = (question_limit // len(voters)) // 2
        for voter in voters:
            questions_per_voter = max_questions_per_voter
            temp = questions_per_voter
            temp_candidates = candidates.copy()
            counter = 0
            while temp > 0 and len(temp_candidates) > 0:
                temp -= questionPrice.get_price(temp_candidates, [1/len(temp_candidates), 1 - 2/len(temp_candidates), 1/len(temp_candidates)])
                temp_candidates = temp_candidates[1:]
                counter += 1
            questions_per_voter = counter
            if questions_per_voter <= 0:
                return bn.argpartition(scores, num_winners)[-num_winners:]
            if 2*questions_per_voter >= num_candidates:
                scores[voter.OrdinalPreferences] += rank_scores
                continue
            voter_first_truncated_preferences = voter.OrdinalPreferences[:questions_per_voter]
            scores[voter_first_truncated_preferences] += rank_scores[:questions_per_voter]
            voter_last_truncated_preferences = voter.OrdinalPreferences[-questions_per_voter:]
            scores[voter_last_truncated_preferences] += rank_scores[-questions_per_voter:]
            scores[voter.OrdinalPreferences[questions_per_voter:-questions_per_voter]] += (
                    sum(rank_scores[questions_per_voter:-questions_per_voter]) // (
                        num_candidates - 2*questions_per_voter))
        return bn.argpartition(scores, num_winners)[-num_winners:]

    @staticmethod
    def __str__():
        """
        Returns the name of the voting rule
        :return: the name of the voting rule
        """
        return "K-Borda Next and Last Questions distributed First Come First Serve"
