#!/usr/bin/python
# -*- coding: utf-8 -*-

from Experiment_framework.Election import Election
from Voting_rules.KBorda.KbordaBucket import KbordaBucket
from Voting_rules.VotingRuleConstrained import VotingRuleConstrained


class KbordaSplitFCFS(VotingRuleConstrained):
	"""
	Class for K-Borda voting rule constrained by the number of questions in the form of a split between preferred and
	not preferred candidates by the voter distributed First Come First Serve among voters.

	Methods: find_winners(election, num_winners) -> list[int]: Returns a list of the winners of the election
	according to the K-Borda rule constrained by the number of questions in the form of a split between preferred and
	not preferred candidates by the voter distributed First Come First Serve among voters.
	"""

	name = "K-Borda split First Come First Serve"

	@staticmethod
	def find_winners(election: Election, num_winners: int, question_limit: int) -> list[int]:
		"""
		Returns a list of the winners of the election according to the K-Borda rule constrained by the number of
		questions in the form of a split between preferred and not preferred candidates by the voter distributed First
		Come First Serve among voters.
		:param election: the election to find the winners for
		:param num_winners: the number of winners to find
		:param question_limit: the number of questions all voters can answer
		:return: the list of winners according to the K-Borda rule constrained by the number of questions
		in the form of a split between preferred and not preferred candidates by the voter distributed First Come
		First Serve among voters.
		"""
		return KbordaBucket([0.5, 0.5]).find_winners(election, num_winners, question_limit, False)
