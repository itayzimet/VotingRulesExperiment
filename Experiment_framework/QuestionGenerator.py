import torch
from torch import nn as nn


class QuestionGenerator(nn.Module):
	def __init__(self, input_size = 4, hidden_size = 20, output_size = 10):
		super(QuestionGenerator, self).__init__()
		self.network = nn.Sequential(nn.Linear(input_size, hidden_size), nn.ReLU(), nn.Linear(hidden_size,
		hidden_size),
				nn.ReLU(), nn.Linear(hidden_size, output_size), )

	def forward(self, x):
		temp = self.network(x)
		return temp


import numpy as np


def normalize(z):
	sum = np.sum(z)
	z = [x / sum for x in z]
	z = [x for x in z if x > 0.01]
	sum = np.sum(z)
	z = [x / sum for x in z]
	return z


def execute_function(
		_num_winners: int, _num_candidates: int, _num_voters: int, _budget: int,
		model: QuestionGenerator | list[str] | list[float] = None, soft_maxed = True) -> list[float]:
	"""
	Execute the function with the given parameters, returns a question type.
	Args:
		_num_winners: the number of winners to be selected
		_num_candidates: the number of candidates in the election
		_num_voters: the number of voters in the election
		_budget: the budget for the questions
		model: the model to generate the question type
		soft_maxed: whether the output should be soft-maxed

	Returns: a list of floats representing the question type, if soft_maxed is True, the sum of the list will be 1
	and the values will be between 0 and 1.
	"""
	question = get_question_from_model_type(_budget, _num_candidates, _num_voters, _num_winners, model)
	if soft_maxed:
		question = normalize(question)
	return question


def get_question_from_model_type(_budget: int, _num_candidates: int, _num_voters: int, _num_winners: int, model: QuestionGenerator | list[str] | list[float]) -> list[float]:
	"""
	Generate a question type from the given model.
	Args:
		_budget: the budget for the questions
		_num_candidates: the number of candidates in the election
		_num_voters: the number of voters in the election
		_num_winners: the number of winners to be selected
		model: the model to generate the question type

	Returns: a list of floats representing the question type"""

	if type(model) is list:
		expression = model
		question = [eval(expr.__str__(), {'winners': _num_winners, 'candidates': _num_candidates, 'voters': _num_voters,
		                                  'budget':  _budget}) for expr in expression]
	else:
		question = model(
				torch.tensor([_num_winners, _num_candidates, _num_voters, _budget], dtype = torch.float32).unsqueeze(
						0)).squeeze().tolist()
	question = [abs(x) for x in question]
	return question
