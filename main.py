# %%

import mapel.elections as mapel
import numpy as np
import torch

from ai_framework import test_best_function, evaluate_function
from anealing import simulated_annealing
from Experiment_framework.Election import Election
from Experiment_framework.main_helper import *
from Experiment_framework.Voter import Voter
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
def main_no_maple(training_mode = False, load_saved = True, compute = False):
    """
    Main function to run the experiment
    :return: None
    """
    if training_mode:
        best_annealing_function = annealing()
        best_genetic_function = genetic()
        final_learning_model = deep_learning()
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
            KbordaSplitFCFS(),
            KbordaNextEq(), KbordaNextFCFS(),
            KbordaLastEq(), KbordaLastFCFS(),
            KbordaNextLastEQ(), KbordaNextLastFCFS(),
            KbordaBucketSplit(), KbordaBucketTrinary(),
            KbordaBucket(best_annealing_function, 'Annealing'),
            KbordaBucket(best_genetic_function, 'Genetic'),
            KbordaBucket(final_learning_model, 'Deep Learning'),
            VotingRuleRandom()],
        number_of_questions = range(1, 400000, 1000), number_of_runs = 5000,
        multithreaded = True)
    
    # %%
    """KBorda testing"""
    # %%
    if load_saved:
        no_of_saved_runs, saved_averages = extract_saved_averages()
        if compute:
            averages = run_test(test_parameters)
            averages, test_parameters = combine_saved_current(averages, no_of_saved_runs, saved_averages,
                                                              test_parameters)
            write_averages_to_file(averages, test_parameters)
        else:
            averages = saved_averages
            test_parameters['number_of_runs'] = no_of_saved_runs
    elif compute:
        averages = run_test(test_parameters)
        write_averages_to_file(averages, test_parameters)
    else:
        raise Exception("Please choose either load_saved or compute or both to be True.")
    # %%
    total_averages = {}
    # Calculate the average Accuracy for each voting rule
    for key in averages:
        total_averages[key] = float(np.mean(averages[key]))
    # %%
    # send plot, averages, parameters and file to telegram
    send_plot(test_parameters, averages)
    send_message(total_averages.__str__())
    send_message(test_parameters.__str__())
    send_file('averages.pickle')


def main_maple():
    experiment = mapel.prepare_online_ordinal_experiment()
    experiment.set_default_num_voters(100)
    experiment.set_default_num_candidates(100)
    
    # generate the elections
    experiment.add_family('ic', size = 30, color = 'red', label = 'IC', marker = 'o')
    experiment.add_family('urn', size = 30, params = {'alpha': 0.5}, color = 'blue', label = 'Urn', marker = 'x')
    
    experiment.compute_distances(distance_id = 'emd-positionwise')
    experiment.embed_2d(embedding_id = 'fr')
    
    experiment.print_map_2d()
    
    experiment.add_feature('next_fcfs', maple_feature_next_fcfs)
    experiment.compute_feature('next_fcfs')
    
    experiment.print_map_2d_colored_by_feature(feature_id = 'next_fcfs', cmap = 'Purples')


def maple_feature_next_fcfs(election: mapel.OrdinalElection) -> dict:
    """
    This function computes the feature for the election using the Next FCFS rule.
    :param election: Election object
    :return: Dictionary containing the feature for the election
    """
    voters = election.votes
    new_voters = []
    for voter in voters:
        new_voter = Voter(voter)
        new_voters.append(new_voter)
    election = Election(list(range(election.num_candidates)), new_voters)
    experiment = Experiment(50, election, Kborda, KbordaNextFCFS(), list(range(1, 4500, 10)))
    distances = experiment.committeeDistance
    x = experiment.numberOfQuestions
    y = distances
    poly = np.polyfit(x, y, 3)
    # return the strongest coefficient of the polynomial as the feature
    return {'value': poly[-1]}


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
    send_file('final_model.pth')
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
    with open('best_genetic_function.pkl', 'wb') as f:
        pickle.dump(best_genetic_function, f)
    send_file('best_genetic_function.pkl')
    return best_genetic_function


# %% Annealing training
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
    with open('best_annealing_function.pkl', 'wb') as f:
        pickle.dump(best_annealing_function, f)
    send_file('best_annealing_function.pkl')
    return best_annealing_function


# %%
if __name__ == '__main__':
    main_maple()
