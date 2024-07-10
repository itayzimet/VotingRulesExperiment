import bottleneck as bn
import numpy as np

from Experiment_framework.Election import Election
from Voting_rules.KBorda.KbordaHelper import KbordaHelper
from Voting_rules.KBorda.Node import Node
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained


class KbordaBucketTrinary(VotingRuleConstrained):
    @staticmethod
    def find_winners(election: Election, num_winners: int, question_limit: int) -> list[int]:
        """
        This function finds the winners of an election by splitting the candidates into three equal sized buckets and
        asking questions to the voters to determine the scores of the candidates.
        :param election: Election object
        :param num_winners: number of winners to be selected
        :param question_limit: number of questions that can be asked
        :return: list of the winners
        """
        # Set up the election
        voters = election.voters
        candidates = election.candidates
        num_candidates = election.numberOfCandidates
        scores = np.zeros(num_candidates, dtype = int)
        # Set up the budget for each voter
        questions = [question_limit // len(voters)] * len(voters)
        helper = KbordaHelper(questions)
        for i, voter in enumerate(voters):
            # If the voter has no budget left, skip
            if helper.questions[i] <= 0:
                break
            # Create the root node
            root_node = Node(candidates)
            helper.fill_tree(voter, root_node, i, [1 / 3, 1 / 3, 1 / 3])
            # Score the candidates
            rank = num_candidates
            KbordaHelper.score_candidates(root_node, scores, rank)
        # Return the winners
        return bn.argpartition(scores, num_winners)[-num_winners:]
    
    @staticmethod
    def __str__():
        return "K-Borda Bucket trinary"
