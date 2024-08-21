import pickle

import torch

from Experiment_framework.ai_framework import evaluate_function, test_best_function
from Experiment_framework.main_helper import send_file, send_message
from Experiment_framework.QuestionGenerator import QuestionGenerator
from training.anealing import simulated_annealing
from training.geneticLearning import genetic_algorithm
from training.learning import train_model


def deep_learning():
	# %% Deep learning
	num_epochs = 100
	learning_rate = 0.01
	model = QuestionGenerator()
	trained_model = train_model(model, num_epochs, learning_rate)
	training_summary = f"Training complete."
	# Evaluate the trained model
	final_error = evaluate_function(trained_model)
	training_summary += f"Final average error: {final_error}"
	send_message(training_summary)
	test_best_function(trained_model)
	final_learning_model = model.network
	torch.save(final_learning_model, 'final_model.pth')
	send_file('models/final_model.pth')
	return final_learning_model


def genetic():
	# %% Genetic training
	population_size = 5
	num_generations = 5
	tournament_size = 2
	mutation_rate = 0.1
	crossover_rate = 0.8
	best_genetic_function, best_score = genetic_algorithm(population_size, num_generations, tournament_size,
	                                                      crossover_rate, mutation_rate)
	send_message("Genetic training results:")
	send_message(f"Best function (vector size: {len(best_genetic_function)}):")
	for expr in best_genetic_function:
		print(expr)
		send_message(expr)
	send_message(f"Best score (average error): {best_score}")
	test_best_function(best_genetic_function)
	# export to pickle
	with open('models/best_genetic_function.pkl', 'wb') as f:
		pickle.dump(best_genetic_function, f)
	send_file('models/best_genetic_function.pkl')
	return best_genetic_function


def annealing():
	t = 1000
	alpha = 0.9999995
	max_iter = 100
	best_annealing_function, best_score = simulated_annealing(t, alpha, max_iter)
	send_message("Annealing training results:")
	send_message(f"Best function (vector size: {len(best_annealing_function)}):")
	for expr in best_annealing_function:
		send_message(expr)
	send_message(f"Best score (average error): {best_score}")
	test_best_function(best_annealing_function)
	# export to pickle
	with open('models/best_annealing_function.pkl', 'wb') as f:
		pickle.dump(best_annealing_function, f)
	send_file('models/best_annealing_function.pkl')
	return best_annealing_function
