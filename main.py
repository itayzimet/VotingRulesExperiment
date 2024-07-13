# %%

import numpy as np
import torch

from anealing import simulated_annealing, send_message, test_best_function
from Experiment_framework.main_helper import *
from geneticLearning import genetic_algorithm
from learning import train_model, evaluate_model
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
def main():
    """
    Main function to run the experiment
    :return: None
    """
    
    # %% Annealing training
    T = 1000
    alpha = 0.9
    max_iter = 100000
    
    best_annealing_function, best_score = simulated_annealing(T, alpha, max_iter)
    send_message("Annealing training results:")
    send_message(f"Best function (vector size: {len(best_annealing_function)}):")
    for expr in best_annealing_function:
        print(expr)
        send_message(expr)
    send_message(f"Best score (average error): {best_score}")
    test_best_function(best_annealing_function)
    
    # export to pickle
    with open('best_function.pkl', 'wb') as f:
        pickle.dump(best_annealing_function, f)
    
    # %% Genetic training
    pop_size = 2000
    generations = 200
    tournament_size = 200
    crossover_rate = 0.8
    mutation_rate = 0.2
    
    best_genetic_function, best_score = genetic_algorithm(pop_size, generations, tournament_size, crossover_rate,
                                                          mutation_rate)
    send_message("Genetic training results:")
    send_message(f"Best function: (vector size: {len(best_genetic_function)})")
    for expr in best_genetic_function:
        print(expr)
        send_message(expr)
    send_message(f"Best score (average error): {best_score}")
    test_best_function(best_genetic_function)
    
    # export to pickle
    with open('best_function.pkl', 'wb') as f:
        pickle.dump(best_genetic_function, f)
    
    # %% Deep learning
    model = QuestionGenerator()
    train_model(model)
    
    final_error = evaluate_model(model)
    send_message(f"Final average error: {final_error}")
    
    final_learning_model = model.network
    torch.save(final_learning_model, 'final_model.pth')
    
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
            KbordaBucket(question_expression = best_annealing_function),
            KbordaBucket(question_expression = best_genetic_function),
            KbordaBucket(model = final_learning_model),
            VotingRuleRandom],
        number_of_questions = range(1, 150000, 1000), number_of_runs = 1,
        multithreaded = True)
    # %%
    """KBorda testing"""
    # %%
    # load averages from pickle file
    no_of_saved_runs, saved_averages = extract_saved_averages()
    # %%
    # Run the test for KBorda
    averages = run_test(test_parameters)
    # %%
    # Average the saved averages and the new averages
    averages, test_parameters = combine_saved_current(averages, no_of_saved_runs, saved_averages, test_parameters)
    # add averages to pickle file
    write_averages_to_file(averages, test_parameters)
    total_averages = {}
    # Calculate the average Accuracy for each voting rule
    for key in averages:
        total_averages[key] = float(np.mean(averages[key]))
    # %%
    # Print the average Accuracy for each voting rule
    send_message(total_averages.__str__())
    # Plot the graph for KBorda
    plot_graph(test_parameters, averages)


# %%
if __name__ == '__main__':
    main()
