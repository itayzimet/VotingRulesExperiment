import bottleneck as bn
import numpy as np

from Experiment_framework.Election import Election
from Voting_rules.KBorda.KbordaHelper import KbordaHelper
from Voting_rules.KBorda.Node import Node
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained


class KbordaBucket(VotingRuleConstrained):
    
    def __init__(self, question_type: list[float]):
        self.question_type = question_type
    
    def find_winners(self, election: Election, num_winners: int, question_limit: int) -> list[int]:
        """
        Find the winners of the election by splitting the candidates using the bucket syntax
        :param election: Election object containing the candidates and voters
        :param num_winners: Number of winners to be selected
        :param question_limit: Maximum number of questions that can be asked
        :return: List of the winners
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
            helper.fill_tree(voter, root_node, i, self.question_type)
            # Score the candidates
            rank = num_candidates
            KbordaHelper.score_candidates(root_node, scores, rank)
        # Return the winners
        return bn.argpartition(scores, num_winners)[-num_winners:]
    
    def calculate_scores(self, election: Election, question_limit: int) -> list[int]:
        """
        Calculate the scores of the candidates using the bucket syntax
        :param election: Election object containing the candidates and voters
        :param question_limit: Maximum number of questions that can be asked
        :return: List of the scores
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
            helper.fill_tree(voter, root_node, i, self.question_type)
            # Score the candidates
            rank = num_candidates
            KbordaHelper.score_candidates(root_node, scores, rank)
        # Return the scores
        return list(scores)
    
    def __str__(self):
        return f"K-Borda Bucket: {self.question_type}"
