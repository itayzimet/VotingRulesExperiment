import math
import random

from dotenv import load_dotenv
from tqdm import trange

from Experiment_framework.ai_framework import evaluate_function, mutate_function, random_function, test_best_function
from Experiment_framework.main_helper import send_message


def simulated_annealing(t, _alpha, _max_iter):
	load_dotenv()
	"""Perform simulated annealing to find the best function."""
	# Generate a random function
	current_function = random_function()
	current_score = evaluate_function(current_function)
	_best_function = current_function.copy()
	_best_score = current_score

	iterations = trange(_max_iter, desc = "Simulated Annealing", )

	for _ in iterations:
		t *= _alpha
		neighbour_function = mutate_function(current_function.copy())
		neighbour_score = evaluate_function(neighbour_function)
		if neighbour_score < current_score:
			current_score = neighbour_score
			current_function = neighbour_function
			if neighbour_score < _best_score:
				_best_score = neighbour_score
				_best_function = neighbour_function.copy()
				iterations.postfix = f"Best score: {neighbour_score:.4f}"
		else:
			p = math.exp((current_score - neighbour_score) / t)
			if random.random() < p:
				current_score = neighbour_score
				current_function = neighbour_function
			iterations.postfix = f"Best score: {_best_score:.4f}"
		if _best_score < 0.01:
			break
	return _best_function, _best_score


# Test the best function


def main():
	"""
	Main function to run the annealing AI
	:return: None
	"""
	T = 1
	alpha = 0.999999995
	max_iter = 1000

	best_function, best_score = simulated_annealing(T, alpha, max_iter)
	send_message(f"Best function (vector size: {len(best_function)}):")
	for expr in best_function:
		print(expr)
	send_message(f"Best score (average error): {best_score}")

	send_message("\nTesting the best function:")
	test_best_function(best_function)


if __name__ == '__main__':
	main()
