#!/usr/bin/python
# -*- coding: utf-8 -*-
import bottleneck as bn
import numpy as np

from Experiment_framework.Election import Election
from Voting_rules import questionPrice
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained


class KbordaNextEq(VotingRuleConstrained):
	"""
	Class for K-Borda voting rule with the next question with budget distributed equally among voters

	Methods: find_winners(election, num_winners) -> list[int]: returns the winners of the election according to the
	K-Borda rule with the next question with budget distributed equally among voters
	"""

	name = "Next equally"

	@staticmethod
	def find_winners(election: Election, num_winners: int, question_limit: int) -> list[int]:
		"""
		Returns a list of the winners of the election according to the K-Borda rule with first k truncated ballots with
		the budget k distributed equally among voters
		:param election: the election to find the winners for
		:param num_winners: the number of winners to find
		:param question_limit: the number of questions all voters can answer
		:return: the list of winners according to the K-Borda rule constrained by the budget of questions all voters
		can
		answer
		"""
		# Initialize variables
		voters = election.voters
		candidates = election.candidates
		num_candidates = len(candidates)
		scores = np.zeros(num_candidates, dtype = int)
		rank_scores = np.arange(num_candidates, 0, -1)
		# Calculate the budget for each voter
		questions = [question_limit // len(voters)] * len(voters)
		if question_limit % len(voters) != 0:
			for i in range(question_limit % len(voters)):
				questions[i] += 1
		# Calculate the scores of the candidates
		if questions[0] < questionPrice.get_price(candidates, [1 / len(candidates), 1 - 1 / len(candidates)]):
			return bn.argpartition(-scores, num_winners)[:num_winners]
		for i, voter in enumerate(voters):
			if questions[i] <= 0:
				break
			# calculate amount of available questions
			question_budget = questions[i]
			question_amount = 0
			candidates_in_bucket = candidates.copy()
			while question_budget > 0:
				price = questionPrice.get_price(candidates_in_bucket,
				                                [1 / len(candidates_in_bucket), 1 - 1 / len(candidates_in_bucket)])
				if price > question_budget:
					break
				question_budget -= price
				candidates_in_bucket = candidates_in_bucket[:-1]
				question_amount += 1
				if question_amount == len(candidates):
					break
			# score the candidates
			preferences = voter.OrdinalPreferences[:question_amount]
			scores[preferences] += rank_scores[:question_amount]

		# Return the num_winners candidates with the highest scores
		return bn.argpartition(scores, num_winners)[-num_winners:]
