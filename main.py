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
    # %%
    experiment_id = '100x100_mine'
    distance_id = 'emd-positionwise'
    embedding_id = 'kk'
    
    experiment = mapel.prepare_online_ordinal_experiment(
        experiment_id = experiment_id,
        distance_id = distance_id,
        embedding_id = embedding_id,
    
    )
    experiment.reset_cultures()
    experiment.is_exported = True
    experiment.set_default_num_voters(100)
    experiment.set_default_num_candidates(100)
    
    experiment.add_family('ic', size = 10, color = 'blue')
    alphas = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5]
    for alpha in alphas:
        experiment.add_family('urn', size = 30, color = 'red', params = {'alpha': alpha})
    phis = [0.001, 0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.95, 0.99, 0.999]
    for phi in phis:
        experiment.add_family('mallows', size = 20, color = 'green', params = {'phi': phi})
    experiment.add_family('conitzer', size = 30, color = 'brown')
    experiment.add_family('walsh', size = 30, color = 'purple')
    experiment.add_family('spoc', size = 30, color = 'orange')
    experiment.add_family('single-crossing', size = 30, color = 'yellow')
    dims = [1, 2, 3, 5, 10, 20]
    for dim in dims:
        experiment.add_family('euclidean', size = 30, color = 'cyan', params = {'dim': dim, 'space': 'uniform'})
    dims = [2, 3, 5]
    for dim in dims:
        experiment.add_family('euclidean', size = 30, color = 'magenta', params = {'dim': dim, 'space': 'sphere'})
    
    experiment.add_election('identity', color = 'black', label = 'ID', marker = 'x')
    experiment.add_election('uniformity', color = 'black', label = 'UN', marker = 'x')
    experiment.add_election('antagonism', color = 'black', label = 'AN', marker = 'x')
    experiment.add_election('stratification', color = 'black', label = 'ST', marker = 'x')
    experiment.add_family('anid', color = 'silver', size = 20, marker = 3, path = {'variable': 'alpha'})
    experiment.add_family('stid', color = 'silver', size = 20, marker = 3, path = {'variable': 'alpha'})
    experiment.add_family('anun', color = 'silver', size = 20, marker = 3, path = {'variable': 'alpha'})
    experiment.add_family('stun', color = 'silver', size = 20, marker = 3, path = {'variable': 'alpha'})
    
    experiment.prepare_elections()
    
    experiment.add_feature('next_fcfs', maple_feature_next_fcfs)
    experiment.compute_feature('next_fcfs')
    
    # compute distance
    experiment.compute_distances()
    
    # embed 2d and print map
    experiment.embed_2d(embedding_id = 'kk')
    experiment.print_map_2d(tex = True, saveas = 'map')
    experiment.print_map_2d_colored_by_feature(feature_id = 'next_fcfs', cmap = 'viridis', tex = True,
                                               saveas = 'map_colored')


def maple_experiment(voters, num_candidates, num_questions):
    random.shuffle(voters)
    temp_election = Election(list(range(num_candidates)), voters)
    # noinspection PyTypeChecker
    experiment = Experiment(50, temp_election, Kborda, KbordaNextFCFS(), num_questions)
    return experiment.committeeDistance


def maple_feature_next_fcfs(election: mapel.OrdinalElection) -> dict:
    """
    This function computes the feature for the election using the Next FCFS rule.
    :param election: Election object
    :return: Dictionary containing the feature for the election
    """
    
    if election.fake:
        return {'value': 0, 'plot': None}
    voters = election.votes
    new_voters = []
    for voter in voters:
        new_voter = Voter(voter)
        new_voters.append(new_voter)
    num_candidates = election.num_candidates
    num_questions = list(range(1, 80000, 1000))
    
    with Pool() as pool:
        distances = list(
            pool.starmap(maple_experiment,
                         [(new_voters.copy(), num_candidates, num_questions.copy()) for _ in range(5)]))
    distances = np.mean(distances, axis = 0)
    x = num_questions
    y = distances
    x = np.array(x)
    y = np.array(y)
    from numpy.polynomial import Polynomial
    poly: Polynomial = Polynomial.fit(x, y, 2)
    
    # save plot as var to return it
    fig, ax = plt.subplots()
    ax.plot(x, y, 'o')
    ax.plot(x, poly(x))
    ax.set(xlabel = 'Number of questions', ylabel = 'Distance between the committees',
           title = f"{election.election_id}\n {poly}")
    ax.grid()
    plt.show()
    # return the strongest coefficient of the polynomial as the feature
    return {'value': poly.coef[-1], 'plot': (fig, ax)}


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
