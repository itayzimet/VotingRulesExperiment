import bottleneck as bn
import numpy as np

from Experiment_framework.Election import Election
from Experiment_framework.QuestionGenerator import execute_function#, QuestionGenerator
from Voting_rules.KBorda.KbordaHelper import KbordaHelper
from Voting_rules.KBorda.Node import Node
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained


class KbordaBucket(VotingRuleConstrained):

	def __init__(self, question_type: list[float]| list[str] = None, _name = None):
		super().__init__()
		self.question_type = question_type
		if _name is None:
			self.name = "question_type"
		else:
			self.name = _name

	def find_winners(
			self, election: Election, num_winners: int, question_limit: int, distribute_equally: bool = True) -> list[
		int]:
		"""
		Find the winners of the election by splitting the candidates using the bucket syntax
		:param election: Election object containing the candidates and voters
		:param num_winners: Number of winners to be selected
		:param question_limit: Maximum number of questions that can be asked
		:param distribute_equally: Whether the questions should be distributed equally among the voters
		:return: List of the winners
		"""
		self.question_type = execute_function(num_winners, election.numberOfCandidates, election.numberOfVoters,
		                                      question_limit, self.question_type)
		scores = self.calculate_scores(election, question_limit, distribute_equally)
		return bn.argpartition(-scores, num_winners)[:num_winners]

	def calculate_scores(self, election: Election, question_limit: int, distribute_equally: bool = True) -> np.ndarray:
		"""
		Calculate the scores of the candidates using the bucket syntax
		:param election: Election object containing the candidates and voters
		:param question_limit: Maximum number of questions that can be asked
		:param distribute_equally: Whether the questions should be distributed equally among the voters
		:return: List of the scores

		"""
		if distribute_equally:
			questions = [question_limit / election.numberOfVoters] * election.numberOfVoters
			if question_limit % election.numberOfVoters != 0:
				for i in range(question_limit % election.numberOfVoters):
					questions[i] += 1
		else:
			questions = [question_limit]
		helper = KbordaHelper(questions)
		scores = np.zeros(election.numberOfCandidates)
		for idx, voter in enumerate(election.voters):
			idx = idx if distribute_equally else 0
			voter_node = Node(list(range(election.numberOfCandidates)))
			helper.fill_tree(voter, voter_node, idx, self.question_type)
			helper.score_candidates(voter_node, scores, election.numberOfCandidates)
		return scores

	def __str__(self):
		return f"K-Borda Bucket {self.name}"
