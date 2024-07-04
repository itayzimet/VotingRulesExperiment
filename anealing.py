import math
import random

import bottleneck as bn
import numpy as np

from Experiment_framework import Experiment_helper
from Voting_rules.KBorda.Kborda import Kborda
from Voting_rules.KBorda.KbordaBucket import KbordaBucket


def softmax(x: list):
    """Compute the softmax of vector x."""
    # all output values should be between 0 and 1
    # the sum of all output values should be 1
    e_x = np.exp(np.array(x) - np.max(x))
    return e_x / e_x.sum()


def random_function(min_size = 1, max_size = 10):
    """Generate a random function structure with variable output size."""
    # the function generated will output a question type for voter.general_bucket_question
    # the function will take in 4 inputs: num_winners, num_candidates, num_voters, budget
    operations = ['+', '-', '*', '/']
    inputs = ['winners', 'candidates', 'voters', 'budget']
    constants = [str(x) for x in range(1, 1000, 10)]
    
    def generate_expr():
        if random.random() < 0.1:
            return f"{random.choice(constants)}"
        elif random.random() < 0.5:
            return f"{random.choice(inputs)}"
        else:
            return f"({generate_expr()} {random.choice(operations)} {generate_expr()})"
    
    size = random.randint(min_size, max_size)
    return [generate_expr() for _ in range(size)]


def mutate_function(func):
    """Mutate the given function slightly."""
    if random.random() < 0.7 and len(func) > 1:
        # Modify an existing expression
        index = random.randint(0, len(func) - 1)
        func[index] = random_function(1, 1)[0]
    elif random.random() < 0.5 and len(func) > 1:
        # Remove an expression
        index = random.randint(0, len(func) - 1)
        func.pop(index)
    else:
        # Add a new expression
        func.append(random_function(1, 1)[0])
    return func


# noinspection PyBroadException
def evaluate_function(func: list):
    """Evaluate the function with the given parameters."""
    
    # noinspection PyUnusedLocal
    def execute(expression, _num_winners: int, _num_candidates: int, _num_voters: int, _budget: int):
        winners = _num_winners
        candidates = _num_candidates
        voters = _num_voters
        # noinspection PyShadowingNames
        budget = _budget
        return eval(expression)
    
    total_error = 0
    num_tests = 10
    
    for _ in range(num_tests):
        num_winners = random.randint(20, 50)
        num_candidates = random.randint(50, 100)
        num_voters = random.randint(50, 100)
        budget = random.randint(100, 15000)
        try:
            # Generate a question type
            question = [execute(expression, num_winners, num_candidates, num_voters, budget) for expression in func]
            question = softmax(question)
            sum_question = sum(question)
            if sum_question > 1:
                # Normalize the question type
                question = [q / sum_question for q in question]
                # Add a final bucket to make it sum to 1
                question.append(1 - sum_question)
            else:
                if sum_question != 1:
                    # Add a final bucket to make it sum to 1
                    question.append(1 - sum_question)
            
            # Generate an election based on the parameters
            election = Experiment_helper.fabricate_election(num_candidates, num_voters)
            # experiment = Experiment(num_winners, election, Kborda, KbordaBucket, [budget], question)
            true_scores = Kborda.calculate_scores(election)
            committee_scores = KbordaBucket(question).calculate_scores(election, budget)
            
            true_winners = bn.argpartition(true_scores, num_winners)[-num_winners:]
            committee_winners = bn.argpartition(committee_scores, num_winners)[-num_winners:]
            
            symmetric_difference = len(set(true_winners) ^ set(committee_winners))
            mean_squared_error = sum(
                [(true_scores[i] - committee_scores[i]) ** 2 for i in range(num_candidates)]) / num_candidates
            
            error = symmetric_difference / num_winners + mean_squared_error
            total_error += error
        except:
            total_error += 1000000
    return total_error / num_tests


def simulated_annealing(t, _alpha, _max_iter):
    """Perform simulated annealing to find the best function."""
    # Generate a random function
    current_function = random_function()
    current_score = evaluate_function(current_function)
    _best_function = current_function.copy()
    _best_score = current_score
    
    for _ in range(_max_iter):
        t *= _alpha
        neighbour_function = mutate_function(current_function.copy())
        neighbour_score = evaluate_function(neighbour_function)
        if neighbour_score < current_score:
            current_score = neighbour_score
            current_function = neighbour_function
            if neighbour_score < _best_score:
                _best_score = neighbour_score
                _best_function = neighbour_function.copy()
                print(f"Iteration {_}, Best score: {_best_score}. T: {t} alpha: {_alpha}. New best function")
        else:
            p = math.exp((current_score - neighbour_score) / t)
            if random.random() < p:
                current_score = neighbour_score
                current_function = neighbour_function
        if _best_score < 0.01:
            break
        if _ % 100 == 0:
            print(f"Iteration {_}, Best score: {_best_score}. T: {t} alpha: {_alpha}")
    return _best_function, _best_score


# Test the best function
def test_best_function(func):
    # noinspection PyUnusedLocal
    def execute(expression, _num_winners: int, _num_candidates: int, _num_voters: int, _budget: int):
        winners = _num_winners
        candidates = _num_candidates
        voters = _num_voters
        budget = _budget
        return eval(expression)
    
    for _ in range(10):
        x1, x2, x3, x4 = random.randint(1, 50), random.randint(1, 100), random.randint(1, 100), random.randint(1,
                                                                                                               150000)
        try:
            result = [execute(expression, x1, x2, x3, x4) for expression in func]
        except ZeroDivisionError:
            result = [0]
        print(f"""Inputs:
        num winners: {x1}
        num candidates: {x2}
        num voters: {x3}
        budget: {x4}""")
        print(f"Output (size {len(result)}): {[f'{x:.6f}' for x in result]}")
        print(f"Sum: {sum(result):.6f}")
        print(f"Normalized: {[f'{x / sum(result):.6f}' for x in result]}")
        print(f"Sum of normalized: {sum([x / sum(result) for x in result]):.6f}")
        print(f"Error: {evaluate_function(func)}")
        print()


def main():
    """
    Main function to run the anealing ai
    :return: None
    """
    T = 1
    alpha = 0.999999995
    max_iter = 1000
    
    best_function, best_score = simulated_annealing(T, alpha, max_iter)
    print(f"Best function (vector size: {len(best_function)}):")
    for expr in best_function:
        print(expr)
    print(f"Best score (average error): {best_score}")
    
    print("\nTesting the best function:")
    test_best_function(best_function)


if __name__ == '__main__':
    main()
