import numpy as np

from Experiment_framework.Election import Election
from Voting_rules import questionPrice
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
        Returns the winners of the election according to the K-Borda rule with last k truncated ballots
        with the budget k distributed equally among voters
        :param election: Election object
        :param num_winners: number of winners to be selected
        :param question_limit: the budget for the questions
        :return: the winners of the election according to the K-Borda rule with last k truncated ballots
        with the budget k distributed equally among voters
        """
        # Initialize variables
        voters = election.voters
        candidates = election.candidates
        num_candidates = len(candidates)
        scores = np.zeros(num_candidates, dtype=int)
        rank_scores = np.arange(num_candidates, 0, -1)
        # Calculate the budget for each voter
        questions_per_voter = question_limit // len(voters)
        # Calculate the amount of questions that each voter can be asked
        temp = questions_per_voter
        temp_candidates = candidates.copy()
        counter = 0
        while temp > 0 and len(temp_candidates) > 0:
            temp -= questionPrice.get_price(temp_candidates, [1/len(temp_candidates), 1 - 1/len(temp_candidates)])
            temp_candidates = temp_candidates[1:]
            counter += 1
        questions_per_voter = counter
        # If the budget is not enough to ask any question, return the num_winners candidates with the highest scores
        if questions_per_voter <= 0:
            return bn.argpartition(scores, num_winners)[-num_winners:]
        # Calculate the scores of the candidates
        for voter in voters:
            voter_preferences = voter.OrdinalPreferences[-questions_per_voter:]
            scores[voter_preferences] += rank_scores[-questions_per_voter:]
            if questions_per_voter < num_candidates:
                scores[voter.OrdinalPreferences[:-questions_per_voter]] += (
                        sum(rank_scores[:-questions_per_voter]) // (num_candidates - questions_per_voter))
        # Return the num_winners candidates with the highest scores
        return bn.argpartition(scores, num_winners)[-num_winners:]

    @staticmethod
    def __str__():
        return "K-Borda Last Questions distributed equally among voters"
