import random

import bottleneck as bn
import numpy as np

from Experiment_framework import Experiment_helper
from Experiment_framework.main_helper import send_message
from Experiment_framework.QuestionGenerator import execute_function, QuestionGenerator
from Voting_rules.KBorda.Kborda import Kborda
from Voting_rules.KBorda.KbordaBucket import KbordaBucket


def random_function(min_size = 1, max_size = 10):
	"""Generate a random function structure with variable output size."""

	operations = ['+', '-', '*', '/']
	inputs = ['winners', 'candidates', 'voters', 'budget']
	constants = [str(x) for x in [0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]]

	def generate_expr():
		if random.random() < 0.1:
			return f"{random.choice(constants)}"
		elif random.random() < 0.6:
			return f"{random.choices(inputs, weights = [0.3, 0.3, 0.3, 0.1], k = 1)[0]}"
		else:
			return f"({generate_expr()} {random.choice(operations)} {generate_expr()})"

	size = random.randint(min_size, max_size)
	return [generate_expr() for _ in range(size)]


def mutate_function(func):
	"""Mutate the given function slightly."""
	if random.random() < 0.4 and len(func) > 1:
		# Modify an existing expression
		index = random.randint(0, len(func) - 1)
		func[index] = random_function(1, 1)[0]
	elif random.random() < 0.6 and len(func) > 1:
		# Remove an expression
		index = random.randint(0, len(func) - 1)
		func.pop(index)
	else:
		# Add a new expression
		func.append(random_function(1, 1)[0])
	return func


def evaluate_function(
		func: list = None, num_tests = 50, num_winners = 50, num_candidates = 100, num_voters = 50,
		max_budget = 200000) -> float:
	"""Evaluate the function with the given parameters."""
	error = 0
	total_error = 0
	best_error = int(1e9)
	worst_error = 0
	if func is None:
		func = random_function()
	for _ in range(num_tests + 2):
		error += test_function(func, max_budget, num_candidates, num_voters, num_winners)
		best_error = min(best_error, error)
		total_error += error
		error = 0
	total_error -= best_error
	return total_error / num_tests


def test_function(func, max_budget, num_candidates, num_voters, num_winners):
	budget = random.randint(max_budget // 5, max_budget)

	try:
		# Generate an election based on the parameters
		election = Experiment_helper.fabricate_election(num_candidates, num_voters)
		# experiment = Experiment(num_winners, election, Kborda, KbordaBucket, [budget], question)
		true_scores = Kborda.calculate_scores(election)
		true_scores = np.array(true_scores)

		true_winners = bn.argpartition(true_scores, num_winners)[-num_winners:]
		committee_winners = KbordaBucket(func).find_winners(election, num_winners, budget)

		symmetric_difference = len(set(true_winners) ^ set(committee_winners))
		# mean_squared_error = np.mean((true_scores - committee_scores) ** 2)

		error = float(symmetric_difference) / num_winners
	except:
		error = 1000000
	return error


def test_best_function(func: list | QuestionGenerator = None, num_tests = 10):
	for _ in range(num_tests):
		num_candidates = random.randint(2, 300)
		num_winners = random.randint(1, num_candidates // 2)
		num_voters = random.randint(1, 100)
		budget = random.randint(1000, 150000)

		question = execute_function(num_winners, num_candidates, num_voters, budget, func)

		test_summary = f"""Inputs:
        num winners: {num_winners}
        num candidates: {num_candidates}
        num voters: {num_voters}
        budget: {budget}
        Question type: {[f'{x}' for x in question]}
        Sum: {sum(question)}
        total error: 
        {evaluate_function(func, num_winners = num_winners, num_candidates = num_candidates, num_voters = num_voters, max_budget = budget)}
        """
		send_message(test_summary)


def crossover(parent1: list, parent2: list) -> tuple[list, list]:
	# Determine the length of the shorter parent
	min_length = min(len(parent1), len(parent2))

	# Choose a random number of crossover points
	if min_length < 2:
		return parent1, parent2
	num_crossover_points = random.randint(1, min_length - 1)

	# Generate sorted crossover points
	crossover_points = sorted(random.sample(range(1, min_length), num_crossover_points))

	# Initialize children
	child1 = []
	child2 = []

	# Perform crossover
	start = 0
	for end in crossover_points + [None]:
		if random.random() < 0.5:
			child1.extend(parent1[start:end])
			child2.extend(parent2[start:end])
		else:
			child1.extend(parent2[start:end])
			child2.extend(parent1[start:end])
		start = end

	# Handle case where parents have different lengths
	if len(parent1) > len(parent2):
		child1.extend(parent1[min_length:])
	elif len(parent2) > len(parent1):
		child2.extend(parent2[min_length:])

	# Ensure minimum length and add variation
	while len(child1) < 1:
		child1.append(random_function(1, 1)[0])
	while len(child2) < 1:
		child2.append(random_function(1, 1)[0])

	# Optional: Add some randomness
	if random.random() < 0.1:  # 10% chance to add a new random expression
		child1.append(random_function(1, 1)[0])
	if random.random() < 0.1:
		child2.append(random_function(1, 1)[0])

	return child1, child2


def initialize_population(pop_size, min_size = 1, max_size = 10):
	return [random_function(min_size, max_size) for _ in range(pop_size)]


def tournament_selection(population, tournament_size):
	tournament = random.sample(population, tournament_size)
	return min(tournament, key = lambda x: evaluate_function(x))


def evaluate_chromosome(chromosome):
	fitness = evaluate_function(chromosome)
	return chromosome, fitness
