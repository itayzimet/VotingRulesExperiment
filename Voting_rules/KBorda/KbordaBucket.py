import bottleneck as bn
import numpy as np
import torch

from Experiment_framework.Election import Election
from QuestionGenerator import QuestionGenerator
from Voting_rules.KBorda.KbordaHelper import KbordaHelper
from Voting_rules.KBorda.Node import Node
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained


class KbordaBucket(VotingRuleConstrained):
    
    def __init__(self, question_type: list[float] = None, model: QuestionGenerator = None,
                 question_expression: list[str] = None):
        self.question_type = question_type
        self.model = model
        self.question_expression = question_expression
    
    def find_winners(self, election: Election, num_winners: int, question_limit: int) -> list[int]:
        """
        Find the winners of the election by splitting the candidates using the bucket syntax
        :param election: Election object containing the candidates and voters
        :param num_winners: Number of winners to be selected
        :param question_limit: Maximum number of questions that can be asked
        :return: List of the winners
        """
        
        def softmax(x: list):
            try:
                e_x = np.exp(np.array(x) - np.max(x))
                e_x = e_x[e_x > 1e-3]
                return e_x / e_x.sum()
            except:
                return [1]
        
        def execute(expression, _num_winners: int, _num_candidates: int, _num_voters: int, _budget: int):
            try:
                winners = _num_winners
                candidates = _num_candidates
                voters = _num_voters
                budget = _budget
                return eval(expression)
            except:
                Exception("Error in expression")
        
        question = self.question_type
        if self.model is not None:
            return self.find_winners_model(election, num_winners, question_limit)
        if self.question_expression is not None:
            question = [
                execute(expression, num_winners, election.numberOfCandidates, len(election.voters), question_limit) for
                expression in self.question_expression]
            question = list(softmax(question))
            sum_question = sum(question)
            if sum_question > 1:
                # Normalize the question type
                question = [q / sum_question for q in question]
                # Add a final bucket to make it sum to 1
                question.append(1 - sum_question)
            else:
                if sum_question != 1:
                    # Add a final bucket to make it sum to 1
                    question.append(1 - sum_question)
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
            helper.fill_tree(voter, root_node, i, question)
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
        if self.model is not None:
            return self.calculate_scores_model(election, question_limit)
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
    
    def find_winners_model(self, election: Election, num_winners: int, question_limit: int) -> list[int]:
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
        input_tensor = torch.tensor([num_winners, num_candidates, len(voters), question_limit],
                                    dtype = torch.float32).unsqueeze(0)
        with torch.no_grad():
            question = self.model(input_tensor).squeeze().numpy()
        for i, voter in enumerate(voters):
            # If the voter has no budget left, skip
            if helper.questions[i] <= 0:
                break
            # Create the root node
            root_node = Node(candidates)
            helper.fill_tree(voter, root_node, i, question)
            # Score the candidates
            rank = num_candidates
            KbordaHelper.score_candidates(root_node, scores, rank)
        # Return the winners
        return bn.argpartition(scores, num_winners)[-num_winners:]
    
    def __str__(self):
        if self.model is not None:
            return f"K-Borda Bucket: neural network"
        if self.question_expression is not None:
            return f"K-Borda Bucket: {self.question_expression}"
        return f"K-Borda Bucket: {self.question_type}"
    
    def calculate_scores_model(self, election, question_limit):
        # Set up the election
        voters = election.voters
        candidates = election.candidates
        num_candidates = election.numberOfCandidates
        scores = np.zeros(num_candidates, dtype = int)
        # Set up the budget for each voter
        questions = [question_limit // len(voters)] * len(voters)
        helper = KbordaHelper(questions)
        input_tensor = torch.tensor([1, num_candidates, len(voters), question_limit], dtype = torch.float32).unsqueeze(
            0)
        with torch.no_grad():
            question = self.model(input_tensor).squeeze().numpy()
        for i, voter in enumerate(voters):
            # If the voter has no budget left, skip
            if helper.questions[i] <= 0:
                break
            # Create the root node
            root_node = Node(candidates)
            helper.fill_tree(voter, root_node, i, question)
            # Score the candidates
            rank = num_candidates
            KbordaHelper.score_candidates(root_node, scores, rank)
        # Return the scores
        return list(scores)
