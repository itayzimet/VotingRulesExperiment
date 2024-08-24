#!/usr/bin/python
# -*- coding: utf-8 -*-

from Experiment_framework.Election import Election


class VotingRuleConstrained:
	"""
	Abstract class for voting rules with constraints

	Methods:
		find_winners(election, question_limit) -> list[int]:
			Returns a list of the winners of the election
	"""
	name = "Voting Rule Constrained"

	def __init__(self):
		"""
		Constructor of the VotingRuleConstrained class
		"""
		pass

	@staticmethod
	def find_winners(election: Election, num_winners: int, question_limit: int) -> list[int]:
		"""
		Returns a list of the winners of the election
		:param num_winners: the number of winners to find
		:param election: the election to find the winners of
		:param question_limit: the number of questions that can be asked
		:return: the list of winners of the election
		"""
		pass

	def __str__(self):
		"""
		Returns the name of the voting rule
		:return: the name of the voting rule
		"""

		return self.name
