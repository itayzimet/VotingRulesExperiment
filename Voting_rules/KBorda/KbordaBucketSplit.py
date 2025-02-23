import bottleneck as bn
import numpy as np

from Experiment_framework.Election import Election
from Voting_rules.KBorda.KbordaHelper import KbordaHelper
from Voting_rules.KBorda.Node import Node
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained


class KbordaBucketSplit(VotingRuleConstrained):
	"""
	Class for the K-Borda Bucket Split voting rule

	Methods:
		find_winners(election: Election, num_winners: int, question_limit: int) -> list[int]
			Find the winners of the election by splitting the candidates using the bucket syntax
		__str__()
			Return the name of the voting rule as a string
	"""

	name = "Split Equally"

	@staticmethod
	def find_winners(election: Election, num_winners: int, question_limit: int) -> list[int]:
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
		if question_limit % len(voters) != 0:
			for i in range(question_limit % len(voters)):
				questions[i] += 1
		helper = KbordaHelper(questions)
		for i, voter in enumerate(voters):
			# If the voter has no budget left, skip
			if helper.questions[i] <= 0:
				break
			# Create the root node
			root_node = Node(candidates)
			helper.fill_tree(voter, root_node, i, [0.5, 0.5])
			# Score the candidates
			rank = num_candidates
			KbordaHelper.score_candidates(root_node, scores, rank)
		# Return the winners
		return bn.argpartition(scores, num_winners)[-num_winners:]
