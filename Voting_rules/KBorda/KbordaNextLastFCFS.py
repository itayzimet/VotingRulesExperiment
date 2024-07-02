from Experiment_framework.Election import Election
from Voting_rules import questionPrice
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained
import numpy as np
import bottleneck as bn


class KbordaNextLastFCFS(VotingRuleConstrained):
    """
    Class for K-Borda voting rule with top and bottom k truncated ballots with budget distributed according to the
    first-come-first-serve principle

    Methods: find_winners(election, num_winners) -> list[int]: returns the winners of the election according to the
    K-Borda rule with the next and last questions with budget distributed equally among voters
    """

    @staticmethod
    def find_winners(election: Election, num_winners: int, question_limit: int) -> list[int]:
        """
        Returns a list of the winners of the election according to the K-Borda rule with top and bottom k truncated ballots
        with the budget k distributed according to the first-come-first-serve principle
        :param election: the election to find the winners for
        :param num_winners: the number of winners to find
        :param question_limit: the number of questions all voters can answer
        :return: the list of winners according to the K-Borda rule constrained by the number of questions all
        voters can answer
        """
        # Initialize variables
        voters = election.voters
        candidates = election.candidates
        num_candidates = len(candidates)
        scores = np.zeros(num_candidates, dtype=int)
        rank_scores = np.arange(num_candidates, 0, -1)
        # Calculate the budget for each voter
        max_questions_per_voter = (question_limit // len(voters)) // 2
        for voter in voters:
            # Calculate the amount of questions that this voter can be asked
            questions_per_voter = max_questions_per_voter
            temp = questions_per_voter
            temp_candidates = candidates.copy()
            counter = 0
            while temp > 0 and len(temp_candidates) > 0:
                temp -= questionPrice.get_price(temp_candidates, [1/len(temp_candidates), 1 - 2/len(temp_candidates), 1/len(temp_candidates)])
                temp_candidates = temp_candidates[1:]
                counter += 1
            questions_per_voter = counter
            # Calculate the scores of the candidates
            # If the budget is not enough to ask any question, return the num_winners candidates with the highest scores
            if questions_per_voter <= 0:
                return bn.argpartition(scores, num_winners)[-num_winners:]
            # If the budget allows the voter to answer all questions,
            # score the candidates based on the preferences of the voter
            if 2*questions_per_voter >= num_candidates:
                scores[voter.OrdinalPreferences] += rank_scores
                continue
            # Score the candidates based on the preferences of the voters
            # Score the first k questions and the last k questions
            voter_first_truncated_preferences = voter.OrdinalPreferences[:questions_per_voter]
            scores[voter_first_truncated_preferences] += rank_scores[:questions_per_voter]
            voter_last_truncated_preferences = voter.OrdinalPreferences[-questions_per_voter:]
            scores[voter_last_truncated_preferences] += rank_scores[-questions_per_voter:]
            # If the budget does not allow the voter to answer all questions,
            # score the remaining candidates equally
            scores[voter.OrdinalPreferences[questions_per_voter:-questions_per_voter]] += (
                    sum(rank_scores[questions_per_voter:-questions_per_voter]) // (
                        num_candidates - 2*questions_per_voter))
        # Return the num_winners candidates with the highest scores
        return bn.argpartition(scores, num_winners)[-num_winners:]

    @staticmethod
    def __str__():
        """
        Returns the name of the voting rule
        :return: the name of the voting rule
        """
        return "K-Borda Next and Last Questions distributed First Come First Serve"
