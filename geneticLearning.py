import os
import random

from dotenv import load_dotenv
from tqdm.contrib.telegram import tqdm, trange

from anealing import random_function, evaluate_function, mutate_function, test_best_function, send_message


# Assuming all the necessary imports and existing functions are present

def initialize_population(pop_size, min_size = 1, max_size = 10):
    return [random_function(min_size, max_size) for _ in range(pop_size)]


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


def tournament_selection(population, tournament_size):
    tournament = random.sample(population, tournament_size)
    return min(tournament, key = lambda x: evaluate_function(x))


def evaluate_chromosome(chromosome):
    fitness = evaluate_function(chromosome)
    return chromosome, fitness


def genetic_algorithm(pop_size, generations, tournament_size, crossover_rate, mutation_rate):
    load_dotenv()
    population = initialize_population(pop_size)
    population_fitness = []
    for chromosome in tqdm(population, desc = 'Evaluating initial population',
                           token = os.getenv("TELEGRAM_TOKEN"), chat_id = os.getenv("CHAT_ID")):
        population_fitness.append(evaluate_chromosome(chromosome))
    best_chromosome, best_fitness = min(population_fitness, key = lambda x: x[1])
    
    gens = trange(generations, token = os.getenv("TELEGRAM_TOKEN"), chat_id = os.getenv("CHAT_ID"),
                  desc = 'Running generations')
    
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
            gens.postfix = f"New best fitness: {best_fitness % 1e6:.2f}"
        else:
            gens.postfix = f"Best fitness: {best_fitness % 1e6:.2f}"
    
    return best_chromosome, best_fitness


def main():
    # Run the genetic algorithm
    pop_size = 20
    generations = 20
    tournament_size = 5
    crossover_rate = 0.8
    mutation_rate = 0.2
    
    best_function, best_score = genetic_algorithm(pop_size, generations, tournament_size, crossover_rate, mutation_rate)
    
    print(f"\nBest function (vector size: {len(best_function)}):")
    send_message(f"Best function: (vector size: {len(best_function)})")
    for expr in best_function:
        print(expr)
        send_message(expr)
    print(f"Best score (average error): {best_score}")
    send_message(f"Best score (average error): {best_score}")
    
    # Test the best function using the existing test_best_function
    print("\nTesting the best function:")
    send_message("Testing the best function:")
    test_best_function(best_function)
    
    return best_function, best_score


if __name__ == "__main__":
    main()
