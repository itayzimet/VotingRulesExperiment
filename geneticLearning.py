import os
import random

from dotenv import load_dotenv
from tqdm import tqdm, trange

from ai_framework import mutate_function, evaluate_function, test_best_function, crossover, \
    initialize_population, tournament_selection, evaluate_chromosome
from Experiment_framework.main_helper import send_message


def genetic_algorithm(pop_size, generations, tournament_size, crossover_rate, mutation_rate):
    load_dotenv()
    population = initialize_population(pop_size)
    population_fitness = []
    for chromosome in tqdm(population, desc = 'Evaluating initial population',
                           leave = True):
        population_fitness.append(evaluate_chromosome(chromosome))
    best_chromosome, best_fitness = min(population_fitness, key = lambda x: x[1])
    
    gens = trange(generations,
                  desc = 'Running genetic algorithm', postfix = f"Best fitness: {best_fitness % 1e6:.2f})",
                  leave = True)
    
    for _ in gens:
        new_population = []
        
        while len(new_population) < pop_size:
            parent1 = tournament_selection(population, tournament_size)
            parent2 = tournament_selection(population, tournament_size)
            
            if random.random() < crossover_rate:
                child1, child2 = crossover(parent1, parent2)
            else:
                child1, child2 = parent1, parent2
            
            if random.random() < mutation_rate:
                child1 = mutate_function(child1)
            if random.random() < mutation_rate:
                child2 = mutate_function(child2)
            
            new_population.extend([child1, child2])
        
        population = new_population[:pop_size]  # Ensure population size remains constant
        
        # Update the best chromosome if necessary
        current_best = min(population, key = lambda x: evaluate_function(x))
        current_best_fitness = evaluate_function(current_best)
        if current_best_fitness < best_fitness:
            best_chromosome = current_best
            best_fitness = current_best_fitness
            gens.postfix = f"New best fitness: {best_fitness}"
        else:
            gens.postfix = f"Best fitness: {best_fitness}"
    
    return best_chromosome, best_fitness


def main():
    # Run the genetic algorithm
    pop_size = 20
    generations = 20
    tournament_size = 5
    crossover_rate = 0.8
    mutation_rate = 0.2
    
    best_function, best_score = genetic_algorithm(pop_size, generations, tournament_size, crossover_rate, mutation_rate)
    
    send_message(f"Best function: (vector size: {len(best_function)})")
    for expr in best_function:
        print(expr)
        send_message(expr)
    send_message(f"Best score (average error): {best_score}")
    
    # Test the best function using the existing test_best_function
    send_message("Testing the best function:")
    test_best_function(best_function)
    
    return best_function, best_score


if __name__ == "__main__":
    main()
