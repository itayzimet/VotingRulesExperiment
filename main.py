# %%

import numpy as np
import torch

from ai_framework import test_best_function, evaluate_function
from anealing import simulated_annealing
from Experiment_framework.main_helper import *
from geneticLearning import genetic_algorithm
from learning import train_model
from QuestionGenerator import QuestionGenerator
from Voting_rules.KBorda.Kborda import Kborda
from Voting_rules.KBorda.KbordaBucket import KbordaBucket
from Voting_rules.KBorda.KbordaBucketSplit import KbordaBucketSplit
from Voting_rules.KBorda.KbordaBucketTrinary import KbordaBucketTrinary
from Voting_rules.KBorda.KbordaLastEq import KbordaLastEq
from Voting_rules.KBorda.KbordaLastFCFS import KbordaLastFCFS
from Voting_rules.KBorda.KbordaNextEq import KbordaNextEq
from Voting_rules.KBorda.KbordaNextFCFS import KbordaNextFCFS
from Voting_rules.KBorda.KbordaNextLastEQ import KbordaNextLastEQ
from Voting_rules.KBorda.KbordaNextLastFCFS import KbordaNextLastFCFS
from Voting_rules.KBorda.KbordaSplitFCFS import KbordaSplitFCFS
from Voting_rules.VotingRuleRandom import VotingRuleRandom

"""
This file is the main file to run the experiment. It contains the main function that runs the experiment and plots the
graph for the experiment.
"""


# %%
def main(training_mode = True, load_saved = False):
    """
    Main function to run the experiment
    :return: None
    """
    if training_mode:
        best_annealing_function = annealing()
        best_genetic_function = genetic()
        final_learning_model = Deep_learning()
    else:
        try:
            with open('best_annealing_function.pkl', 'rb') as f:
                best_annealing_function = pickle.load(f)
            with open('best_genetic_function.pkl', 'rb') as f:
                best_genetic_function = pickle.load(f)
            final_learning_model = torch.load('final_model.pth')
        except FileNotFoundError:
            send_message("Please run the training mode first.")
            return
    # %%
    test_parameters = dict(
        target_committee_size = 50, num_candidates = 100, num_voters = 100,
        voting_rule = Kborda,
        constrained_voting_rule =
        [
            KbordaSplitFCFS,
            KbordaNextEq, KbordaNextFCFS,
            KbordaLastEq, KbordaLastFCFS,
            KbordaNextLastEQ, KbordaNextLastFCFS,
            KbordaBucketSplit, KbordaBucketTrinary,
            KbordaBucket(best_annealing_function, name = 'Annealing'),
            KbordaBucket(best_genetic_function, name = 'Genetic'),
            KbordaBucket(final_learning_model, name = 'Deep Learning'),
            VotingRuleRandom],
        number_of_questions = range(1, 400000, 1000), number_of_runs = 1,
        multithreaded = True)
    
    # %%
    """KBorda testing"""
    # %%
    if load_saved:
        # load averages from pickle file
        no_of_saved_runs, saved_averages = extract_saved_averages()
    # %%
    # Run the test for KBorda
    averages = run_test(test_parameters)
    # %%
    if load_saved:
        # Average the saved averages and the new averages
        averages, test_parameters = combine_saved_current(averages, no_of_saved_runs, saved_averages, test_parameters)
        # add averages to pickle file
        write_averages_to_file(averages, test_parameters)
    total_averages = {}
    # Calculate the average Accuracy for each voting rule
    for key in averages:
        total_averages[key] = float(np.mean(averages[key]))
    # %%
    # send plot, averages, parameters and file to telegram
    send_plot(test_parameters, averages)
    send_message(total_averages.__str__())
    send_message(test_parameters.__str__())


def Deep_learning():
    # %% Deep learning
    num_epochs = 1000
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
    send_file('final_model.pth')
    return final_learning_model


def genetic():
    # %% Genetic training
    population_size = 10
    num_generations = 10
    tournament_size = 5
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
    with open('best_genetic_function.pkl', 'wb') as f:
        pickle.dump(best_genetic_function, f)
    send_file('best_genetic_function.pkl')
    return best_genetic_function


# %% Annealing training
def annealing():
    T = 1000
    alpha = 0.9999995
    max_iter = 100
    best_annealing_function, best_score = simulated_annealing(T, alpha, max_iter)
    send_message("Annealing training results:")
    send_message(f"Best function (vector size: {len(best_annealing_function)}):")
    for expr in best_annealing_function:
        send_message(expr)
    send_message(f"Best score (average error): {best_score}")
    test_best_function(best_annealing_function)
    # export to pickle
    with open('best_annealing_function.pkl', 'wb') as f:
        pickle.dump(best_annealing_function, f)
    send_file('best_annealing_function.pkl')
    return best_annealing_function


# %%
if __name__ == '__main__':
    main()
